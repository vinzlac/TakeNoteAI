#!/usr/bin/env python3
"""
Script simplifié pour transcription avec identification basique des locuteurs
Utilise Whisper avec une approche simple de détection de changement de locuteur
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

class SimpleSpeakerDiarization:
    """Classe pour transcription avec détection basique des locuteurs."""
    
    def __init__(self, whisper_model="base", device=None, sensitivity="medium"):
        """
        Initialise le modèle Whisper.
        
        Args:
            whisper_model (str): Modèle Whisper à utiliser
            device (str): Device à utiliser (cuda, mps, cpu)
            sensitivity (str): Sensibilité de détection ("low", "medium", "high")
        """
        self.whisper_model_name = whisper_model
        # Utiliser CPU par défaut pour éviter les problèmes de compatibilité
        self.device = device or "cpu"
        self.sensitivity = sensitivity
        
        # Paramètres selon la sensibilité
        if sensitivity == "low":
            self.pause_threshold = 3.0
            self.energy_ratio_threshold = 4.0
            self.min_score = 4
        elif sensitivity == "high":
            self.pause_threshold = 1.5
            self.energy_ratio_threshold = 2.0
            self.min_score = 2
        else:  # medium
            self.pause_threshold = 2.0
            self.energy_ratio_threshold = 2.5
            self.min_score = 3
        
        print(f"🔧 Initialisation du modèle Whisper...")
        print(f"   Device: {self.device}")
        print(f"   Modèle: {whisper_model}")
        print(f"   Sensibilité: {sensitivity}")
        
        # Charger Whisper
        print("🔄 Chargement du modèle Whisper...")
        self.whisper_model = whisper.load_model(whisper_model, device=self.device)
    
    def detect_speaker_changes(self, audio_path: str, segments: List[Dict]) -> List[Dict]:
        """
        Détecte les changements de locuteurs basés sur les pauses, l'énergie audio et l'analyse du texte.
        
        Args:
            audio_path (str): Chemin vers le fichier audio
            segments (List[Dict]): Segments de transcription Whisper
            
        Returns:
            List[Dict]: Segments avec locuteurs assignés
        """
        print("🎤 Détection des changements de locuteurs...")
        
        # Charger l'audio pour l'analyse
        try:
            waveform, sample_rate = torchaudio.load(audio_path)
            audio_data = waveform.numpy().flatten()
        except Exception as e:
            print(f"⚠️  Impossible de charger l'audio pour l'analyse: {e}")
            # Fallback: assigner des locuteurs alternés
            return self._assign_alternating_speakers(segments)
        
        # Analyser les pauses entre segments
        speaker_segments = []
        current_speaker = "SPEAKER_00"
        speaker_count = 1
        
        for i, segment in enumerate(segments):
            seg_start = segment["start"]
            seg_end = segment["end"]
            text = segment["text"].strip()
            
            # Calculer l'énergie audio du segment
            start_sample = int(seg_start * sample_rate)
            end_sample = int(seg_end * sample_rate)
            
            if end_sample > len(audio_data):
                end_sample = len(audio_data)
            
            if start_sample < len(audio_data):
                segment_audio = audio_data[start_sample:end_sample]
                energy = np.mean(np.abs(segment_audio))
            else:
                energy = 0
            
            # Calculer la pause avant ce segment
            pause_duration = seg_start - segments[i-1]["end"] if i > 0 else 0
            
            # Détecter les changements de locuteurs avec des critères plus stricts
            speaker_changed = False
            change_score = 0
            
            # 1. Pause longue (critère principal)
            if pause_duration > self.pause_threshold:
                change_score += 3
            elif pause_duration > self.pause_threshold * 0.7:
                change_score += 1
            
            # 2. Changement d'énergie significatif
            if i > 0:
                prev_energy = speaker_segments[-1]["energy"]
                energy_ratio = energy / (prev_energy + 1e-8)
                if energy_ratio > self.energy_ratio_threshold or energy_ratio < (1/self.energy_ratio_threshold):
                    change_score += 2
                elif energy_ratio > self.energy_ratio_threshold * 0.8 or energy_ratio < (1/(self.energy_ratio_threshold * 0.8)):
                    change_score += 1
            
            # 3. Analyse du contenu textuel (plus sélectif)
            change_indicators = ["ok", "donc", "alors", "oui", "non", "mais", "en fait"]
            # Seulement pour les segments très courts avec des mots de transition
            if (len(text) < 25 and 
                any(indicator in text.lower() for indicator in change_indicators) and
                pause_duration > 0.8):  # Nécessite aussi une pause
                change_score += 1
            
            # 4. Changement de longueur de segment (plus strict)
            if i > 0:
                prev_length = len(speaker_segments[-1]["text"])
                current_length = len(text)
                length_ratio = current_length / (prev_length + 1)
                if length_ratio > 3.0 or length_ratio < 0.3:  # Plus strict
                    change_score += 1
            
            # 5. Cohérence temporelle (éviter les changements trop fréquents)
            if i > 2:  # Regarder les 3 derniers segments
                recent_speakers = [seg["speaker"] for seg in speaker_segments[-3:]]
                if len(set(recent_speakers)) == 1:  # Même locuteur sur 3 segments
                    change_score += 1  # Bonus pour la cohérence
            
            # 6. Durée minimale par locuteur (éviter les changements trop rapides)
            if i > 0:
                # Compter combien de segments le locuteur actuel a parlé
                current_speaker_segments = sum(1 for seg in speaker_segments 
                                             if seg["speaker"] == current_speaker)
                if current_speaker_segments < 2:  # Au moins 2 segments par locuteur
                    change_score -= 1  # Pénalité pour changement trop rapide
            
            # Appliquer le changement seulement si le score est suffisant
            if change_score >= self.min_score and i > 0:
                if current_speaker == "SPEAKER_00":
                    current_speaker = "SPEAKER_01"
                    speaker_count = max(speaker_count, 2)
                else:
                    current_speaker = "SPEAKER_00"
                speaker_changed = True
            
            speaker_segments.append({
                "start": seg_start,
                "end": seg_end,
                "text": text,
                "speaker": current_speaker,
                "confidence": segment.get("avg_logprob", 0),
                "energy": energy,
                "pause_before": pause_duration,
                "speaker_changed": speaker_changed
            })
        
        # Compter les locuteurs
        speakers = list(set(seg["speaker"] for seg in speaker_segments))
        print(f"✅ {len(speakers)} locuteurs détectés: {', '.join(speakers)}")
        
        return speaker_segments
    
    def _assign_alternating_speakers(self, segments: List[Dict]) -> List[Dict]:
        """Assignation alternée des locuteurs en fallback."""
        speaker_segments = []
        current_speaker = "SPEAKER_00"
        
        for i, segment in enumerate(segments):
            # Changer de locuteur tous les 3 segments ou après une pause longue
            if i > 0:
                pause = segment["start"] - segments[i-1]["end"]
                if pause > 1.5 or i % 3 == 0:
                    current_speaker = "SPEAKER_01" if current_speaker == "SPEAKER_00" else "SPEAKER_00"
            
            speaker_segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip(),
                "speaker": current_speaker,
                "confidence": segment.get("avg_logprob", 0),
                "energy": 0,
                "pause_before": segment["start"] - segments[i-1]["end"] if i > 0 else 0
            })
        
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
            
            # Étape 2: Détection des locuteurs
            speaker_segments = self.detect_speaker_changes(str(audio_path), result.get("segments", []))
            
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
                "method": "simple_diarization"
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
        description="Transcription avec détection basique des locuteurs (Whisper uniquement)",
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
    parser.add_argument("--sensitivity", choices=["low", "medium", "high"], 
                       default="medium", help="Sensibilité de détection des locuteurs (défaut: medium)")
    
    args = parser.parse_args()
    
    try:
        # Initialiser le processeur
        processor = SimpleSpeakerDiarization(
            whisper_model=args.model,
            device=args.device,
            sensitivity=args.sensitivity
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
