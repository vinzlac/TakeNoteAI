#!/usr/bin/env python3
"""
Script de transcription avec identification des locuteurs équilibrée
Approche équilibrée qui combine pauses, énergie et analyse textuelle
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
import whisper
import numpy as np
import torch
import torchaudio
from typing import Dict, List, Tuple

class BalancedSpeakerDiarization:
    """Classe pour transcription avec détection de locuteurs équilibrée."""
    
    def __init__(self, whisper_model="base", device=None):
        """
        Initialise le modèle Whisper.
        
        Args:
            whisper_model (str): Modèle Whisper à utiliser
            device (str): Device à utiliser (cuda, mps, cpu)
        """
        self.whisper_model_name = whisper_model
        self.device = device or "cpu"
        
        print(f"🔧 Initialisation du modèle Whisper...")
        print(f"   Device: {self.device}")
        print(f"   Modèle: {whisper_model}")
        
        # Charger Whisper
        print("🔄 Chargement du modèle Whisper...")
        self.whisper_model = whisper.load_model(whisper_model, device=self.device)
    
    def detect_speakers_balanced(self, audio_path: str, segments: List[Dict]) -> List[Dict]:
        """
        Détecte les locuteurs avec une approche équilibrée.
        
        Args:
            audio_path (str): Chemin vers le fichier audio
            segments (List[Dict]): Segments de transcription Whisper
            
        Returns:
            List[Dict]: Segments avec locuteurs assignés
        """
        print("🎤 Détection des locuteurs (approche équilibrée)...")
        
        # Charger l'audio pour l'analyse d'énergie
        try:
            waveform, sample_rate = torchaudio.load(audio_path)
            audio_data = waveform.numpy().flatten()
        except Exception as e:
            print(f"⚠️  Impossible de charger l'audio pour l'analyse: {e}")
            audio_data = None
        
        speaker_segments = []
        current_speaker = "SPEAKER_00"
        speaker_count = 1
        
        # Analyser les segments
        for i, segment in enumerate(segments):
            seg_start = segment["start"]
            seg_end = segment["end"]
            text = segment["text"].strip()
            
            # Calculer l'énergie audio du segment
            if audio_data is not None:
                start_sample = int(seg_start * sample_rate)
                end_sample = int(seg_end * sample_rate)
                
                if end_sample > len(audio_data):
                    end_sample = len(audio_data)
                
                if start_sample < len(audio_data):
                    segment_audio = audio_data[start_sample:end_sample]
                    energy = np.mean(np.abs(segment_audio))
                else:
                    energy = 0
            else:
                energy = 0
            
            # Calculer la pause avant ce segment
            pause_duration = seg_start - segments[i-1]["end"] if i > 0 else 0
            
            # Détecter les changements de locuteurs
            speaker_changed = False
            change_reason = "none"
            
            # 1. Pause significative (critère principal)
            if pause_duration > 1.8:  # Pause de plus de 1.8 secondes
                speaker_changed = True
                change_reason = "pause"
                print(f"   🔄 Changement par pause à {seg_start:.1f}s (pause: {pause_duration:.1f}s)")
            
            # 2. Changement d'énergie significatif + pause
            elif i > 0 and audio_data is not None:
                prev_energy = speaker_segments[-1]["energy"]
                energy_ratio = energy / (prev_energy + 1e-8)
                
                if (energy_ratio > 2.5 or energy_ratio < 0.4) and pause_duration > 0.8:
                    speaker_changed = True
                    change_reason = "energy_change"
                    print(f"   🔄 Changement par énergie à {seg_start:.1f}s (ratio: {energy_ratio:.2f})")
            
            # 3. Réponses courtes typiques
            elif (len(text) < 25 and 
                  pause_duration > 0.6 and
                  any(word in text.lower() for word in ["oui", "non", "ok", "d'accord", "exactement"])):
                speaker_changed = True
                change_reason = "short_response"
                print(f"   🔄 Changement par réponse courte à {seg_start:.1f}s: '{text}'")
            
            # 4. Questions directes
            elif (pause_duration > 0.5 and
                  any(word in text.lower() for word in ["comment", "pourquoi", "quand", "où", "qui", "quoi"]) and
                  len(text) < 100):
                speaker_changed = True
                change_reason = "question"
                print(f"   🔄 Changement par question à {seg_start:.1f}s: '{text[:50]}...'")
            
            # Appliquer le changement de locuteur
            if speaker_changed and i > 0:
                if current_speaker == "SPEAKER_00":
                    current_speaker = "SPEAKER_01"
                    speaker_count = max(speaker_count, 2)
                else:
                    current_speaker = "SPEAKER_00"
            
            speaker_segments.append({
                "start": seg_start,
                "end": seg_end,
                "text": text,
                "speaker": current_speaker,
                "confidence": segment.get("avg_logprob", 0),
                "energy": energy,
                "pause_before": pause_duration,
                "speaker_changed": speaker_changed,
                "change_reason": change_reason
            })
        
        # Compter les locuteurs
        speakers = list(set(seg["speaker"] for seg in speaker_segments))
        print(f"✅ {len(speakers)} locuteurs détectés: {', '.join(speakers)}")
        
        return speaker_segments
    
    def process_audio(self, audio_path: str, output_path: str = None, 
                     language: str = None, output_format: str = "txt") -> str:
        """
        Traite un fichier audio : transcription + détection de locuteurs.
        
        Args:
            audio_path (str): Chemin vers le fichier audio
            output_path (str): Chemin de sortie
            language (str): Langue pour la transcription
            output_format (str): Format de sortie (txt, json, srt)
            
        Returns:
            str: Chemin du fichier de sortie
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Le fichier {audio_path} n'existe pas")
        
        # Générer le nom de sortie si non fourni
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = audio_path.parent / f"{audio_path.stem}_speakers_{timestamp}.{output_format}"
        else:
            output_path = Path(output_path)
        
        print(f"🚀 Traitement: {audio_path.name}")
        print(f"   Taille: {audio_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        try:
            # Étape 1: Transcription avec Whisper
            print("🎤 Transcription avec Whisper...")
            result = self.whisper_model.transcribe(
                str(audio_path),
                language=language,
                verbose=True
            )
            
            # Étape 2: Détection des locuteurs équilibrée
            speaker_segments = self.detect_speakers_balanced(str(audio_path), result.get("segments", []))
            
            # Étape 3: Sauvegarde selon le format
            if output_format == "txt":
                self._save_as_text(speaker_segments, output_path)
            elif output_format == "json":
                self._save_as_json(speaker_segments, result, output_path)
            elif output_format == "srt":
                self._save_as_srt(speaker_segments, output_path)
            else:
                raise ValueError(f"Format non supporté: {output_format}")
            
            # Statistiques
            speakers = list(set(seg["speaker"] for seg in speaker_segments))
            total_duration = max(seg["end"] for seg in speaker_segments) if speaker_segments else 0
            
            print(f"\n✅ Traitement terminé!")
            print(f"📊 Statistiques:")
            print(f"   - Durée totale: {total_duration:.2f} secondes")
            print(f"   - Nombre de locuteurs: {len(speakers)}")
            print(f"   - Locuteurs: {', '.join(speakers)}")
            print(f"   - Langue détectée: {result.get('language', 'Inconnue')}")
            print(f"   - Fichier de sortie: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            print(f"❌ Erreur lors du traitement: {e}")
            raise
    
    def _save_as_text(self, speaker_segments: List[Dict], output_path: Path):
        """Sauvegarde en format texte avec locuteurs."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for seg in speaker_segments:
                start_time = self._format_time(seg["start"])
                end_time = self._format_time(seg["end"])
                f.write(f"[{start_time} - {end_time}] {seg['speaker']}: {seg['text']}\n\n")
    
    def _save_as_json(self, speaker_segments: List[Dict], whisper_result: Dict, output_path: Path):
        """Sauvegarde en format JSON."""
        # Convertir les float32 en float Python pour la sérialisation JSON
        def convert_numpy_types(obj):
            if hasattr(obj, 'item'):  # NumPy types
                return obj.item()
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            else:
                return obj
        
        result = {
            "metadata": {
                "language": whisper_result.get("language"),
                "duration": float(whisper_result.get("duration", 0)),
                "speakers": list(set(seg["speaker"] for seg in speaker_segments)),
                "method": "balanced_diarization"
            },
            "segments": convert_numpy_types(speaker_segments)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    def _save_as_srt(self, speaker_segments: List[Dict], output_path: Path):
        """Sauvegarde en format SRT avec locuteurs."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, seg in enumerate(speaker_segments, 1):
                start_time = self._format_time_srt(seg["start"])
                end_time = self._format_time_srt(seg["end"])
                text = f"{seg['speaker']}: {seg['text']}"
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
    
    def _format_time(self, seconds: float) -> str:
        """Formate le temps en HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def _format_time_srt(self, seconds: float) -> str:
        """Formate le temps pour SRT (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Transcription avec identification des locuteurs équilibrée",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s audio.mp3                           # Transcription avec locuteurs
  %(prog)s audio.mp3 -m large -l fr           # Modèle large, français
  %(prog)s audio.mp3 -f json                  # Format JSON
  %(prog)s audio.mp3 -f srt                   # Format SRT (sous-titres)
        """
    )
    
    parser.add_argument("input", help="Fichier audio d'entrée")
    parser.add_argument("-o", "--output", help="Fichier de sortie (optionnel)")
    parser.add_argument("-m", "--model", choices=["tiny", "base", "small", "medium", "large"], 
                       default="base", help="Modèle Whisper à utiliser (défaut: base)")
    parser.add_argument("-l", "--language", help="Code langue (ex: fr, en). Détection automatique si non spécifié")
    parser.add_argument("-f", "--format", choices=["txt", "json", "srt"], 
                       default="txt", help="Format de sortie (défaut: txt)")
    parser.add_argument("--device", choices=["cpu", "cuda", "mps"], 
                       help="Device à utiliser (auto-détection par défaut)")
    
    args = parser.parse_args()
    
    try:
        # Initialiser le processeur
        processor = BalancedSpeakerDiarization(
            whisper_model=args.model,
            device=args.device
        )
        
        # Traiter l'audio
        output_file = processor.process_audio(
            args.input,
            args.output,
            args.language,
            args.format
        )
        
        print(f"\n🎉 Succès! Transcription avec locuteurs sauvegardée: {output_file}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Traitement interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
