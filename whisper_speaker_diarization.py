#!/usr/bin/env python3
"""
Script hybride Whisper + pyannote.audio pour transcription avec identification des locuteurs
Combine la transcription de qualité de Whisper avec la reconnaissance de locuteurs de pyannote.audio
"""

import os
import sys
import argparse
import json
import tempfile
from pathlib import Path
from datetime import datetime
import whisper
import torch
import torchaudio
from typing import Dict, List, Tuple

# Import pyannote avec gestion d'erreur
try:
    from pyannote.audio import Pipeline
    PYANNOTE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  pyannote.audio non disponible: {e}")
    PYANNOTE_AVAILABLE = False

class WhisperSpeakerDiarization:
    """Classe pour combiner Whisper et pyannote.audio."""
    
    def __init__(self, whisper_model="base", device=None):
        """
        Initialise les modèles Whisper et pyannote.audio.
        
        Args:
            whisper_model (str): Modèle Whisper à utiliser
            device (str): Device à utiliser (cuda, mps, cpu)
        """
        self.whisper_model_name = whisper_model
        # Forcer CPU pour éviter les problèmes de compatibilité avec pyannote.audio
        self.device = device or "cpu"
        
        print(f"🔧 Initialisation des modèles...")
        print(f"   Device: {self.device}")
        print(f"   Modèle Whisper: {whisper_model}")
        
        # Charger Whisper
        print("🔄 Chargement du modèle Whisper...")
        self.whisper_model = whisper.load_model(whisper_model, device=self.device)
        
        # Charger pyannote.audio (diarisation des locuteurs)
        if PYANNOTE_AVAILABLE:
            print("🔄 Chargement du modèle pyannote.audio...")
            try:
                # Désactiver temporairement pyannote.audio à cause de problèmes de compatibilité
                # avec PyTorch 2.8.0 et torchcodec
                raise RuntimeError("pyannote.audio temporairement désactivé - problèmes de compatibilité")
                
                self.diarization_pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1"
                )
                self.diarization_pipeline.to(torch.device(self.device))
                self.pyannote_available = True
            except Exception as e:
                print(f"⚠️  pyannote.audio non disponible: {str(e)[:100]}")
                print("💡 Utilisation de la diarisation manuelle optimisée à la place")
                print("💡 Pour de meilleurs résultats, utilisez whisper_balanced_diarization.py")
                self.pyannote_available = False
        else:
            print("🔄 pyannote.audio non disponible, utilisation de la diarisation manuelle...")
            self.pyannote_available = False
    
    def diarize_speakers(self, audio_path: str) -> List[Dict]:
        """
        Identifie les locuteurs dans l'audio.
        
        Args:
            audio_path (str): Chemin vers le fichier audio
            
        Returns:
            List[Dict]: Liste des segments avec locuteurs
        """
        print("🎤 Identification des locuteurs...")
        
        if self.pyannote_available:
            # Diarisation avec pyannote.audio
            diarization = self.diarization_pipeline(audio_path)
            
            # Convertir en format plus lisible
            speaker_segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                speaker_segments.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker,
                    "duration": turn.end - turn.start
                })
            
            # Trier par temps de début
            speaker_segments.sort(key=lambda x: x["start"])
            
            print(f"✅ {len(set(seg['speaker'] for seg in speaker_segments))} locuteurs identifiés avec pyannote.audio")
            return speaker_segments
        else:
            # Diarisation manuelle basée sur les pauses
            print("🔄 Utilisation de la diarisation manuelle...")
            return self._manual_diarization(audio_path)
    
    def _manual_diarization(self, audio_path: str) -> List[Dict]:
        """
        Diarisation manuelle basée sur les pauses et patterns.
        
        Args:
            audio_path (str): Chemin vers le fichier audio
            
        Returns:
            List[Dict]: Segments avec locuteurs assignés
        """
        # D'abord, transcrir avec Whisper pour obtenir les segments
        result = self.whisper_model.transcribe(audio_path, verbose=False)
        segments = result.get("segments", [])
        
        if not segments:
            return []
        
        speaker_segments = []
        current_speaker = "SPEAKER_00"
        speaker_count = 1
        
        for i, segment in enumerate(segments):
            seg_start = segment["start"]
            seg_end = segment["end"]
            
            # Calculer la pause avant ce segment
            pause_duration = seg_start - segments[i-1]["end"] if i > 0 else 0
            
            # Règles pour changer de locuteur
            speaker_changed = False
            
            # 1. Pause significative
            if pause_duration > 2.0:
                speaker_changed = True
                print(f"   🔄 Changement par pause à {seg_start:.1f}s (pause: {pause_duration:.1f}s)")
            
            # 2. Réponses courtes
            elif (len(segment["text"]) < 20 and 
                  pause_duration > 0.8 and
                  any(word in segment["text"].lower() for word in ["oui", "non", "ok", "d'accord"])):
                speaker_changed = True
                print(f"   🔄 Changement par réponse courte à {seg_start:.1f}s")
            
            # Appliquer le changement
            if speaker_changed and i > 0:
                if current_speaker == "SPEAKER_00":
                    current_speaker = "SPEAKER_01"
                    speaker_count = max(speaker_count, 2)
                else:
                    current_speaker = "SPEAKER_00"
            
            speaker_segments.append({
                "start": seg_start,
                "end": seg_end,
                "speaker": current_speaker,
                "duration": seg_end - seg_start
            })
        
        print(f"✅ {len(set(seg['speaker'] for seg in speaker_segments))} locuteurs identifiés (méthode manuelle)")
        return speaker_segments
    
    def transcribe_audio(self, audio_path: str, language=None) -> Dict:
        """
        Transcrit l'audio avec Whisper.
        
        Args:
            audio_path (str): Chemin vers le fichier audio
            language (str): Langue pour la transcription
            
        Returns:
            Dict: Résultat de la transcription Whisper
        """
        print("🎤 Transcription avec Whisper...")
        
        result = self.whisper_model.transcribe(
            audio_path,
            language=language,
            verbose=True
        )
        
        return result
    
    def align_speakers_with_transcription(self, speaker_segments: List[Dict], 
                                        whisper_result: Dict) -> List[Dict]:
        """
        Aligne les segments de locuteurs avec la transcription Whisper.
        
        Args:
            speaker_segments (List[Dict]): Segments des locuteurs
            whisper_result (Dict): Résultat de Whisper
            
        Returns:
            List[Dict]: Transcription alignée avec les locuteurs
        """
        print("🔗 Alignement des locuteurs avec la transcription...")
        
        aligned_segments = []
        whisper_segments = whisper_result.get("segments", [])
        
        for whisper_seg in whisper_segments:
            seg_start = whisper_seg["start"]
            seg_end = whisper_seg["end"]
            seg_text = whisper_seg["text"].strip()
            
            # Trouver le locuteur dominant pour ce segment
            dominant_speaker = self._find_dominant_speaker(speaker_segments, seg_start, seg_end)
            
            aligned_segments.append({
                "start": seg_start,
                "end": seg_end,
                "text": seg_text,
                "speaker": dominant_speaker,
                "confidence": whisper_seg.get("avg_logprob", 0)
            })
        
        return aligned_segments
    
    def _find_dominant_speaker(self, speaker_segments: List[Dict], 
                             start_time: float, end_time: float) -> str:
        """
        Trouve le locuteur dominant pour un segment donné.
        
        Args:
            speaker_segments (List[Dict]): Segments des locuteurs
            start_time (float): Temps de début
            end_time (float): Temps de fin
            
        Returns:
            str: Nom du locuteur dominant
        """
        # Calculer le temps de parole de chaque locuteur dans le segment
        speaker_times = {}
        
        for seg in speaker_segments:
            # Calculer l'intersection entre le segment de locuteur et le segment de transcription
            overlap_start = max(seg["start"], start_time)
            overlap_end = min(seg["end"], end_time)
            
            if overlap_start < overlap_end:
                overlap_duration = overlap_end - overlap_start
                speaker = seg["speaker"]
                speaker_times[speaker] = speaker_times.get(speaker, 0) + overlap_duration
        
        # Retourner le locuteur avec le plus de temps de parole
        if speaker_times:
            return max(speaker_times, key=speaker_times.get)
        else:
            return "SPEAKER_00"  # Locuteur par défaut
    
    def process_audio(self, audio_path: str, output_path: str = None, 
                     language: str = None, output_format: str = "txt") -> str:
        """
        Traite un fichier audio complet : diarisation + transcription.
        
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
            # Étape 1: Diarisation des locuteurs
            speaker_segments = self.diarize_speakers(str(audio_path))
            
            # Étape 2: Transcription avec Whisper
            whisper_result = self.transcribe_audio(str(audio_path), language)
            
            # Étape 3: Alignement des locuteurs avec la transcription
            aligned_segments = self.align_speakers_with_transcription(
                speaker_segments, whisper_result
            )
            
            # Étape 4: Sauvegarde selon le format
            if output_format == "txt":
                self._save_as_text(aligned_segments, output_path)
            elif output_format == "json":
                self._save_as_json(aligned_segments, whisper_result, output_path)
            elif output_format == "srt":
                self._save_as_srt(aligned_segments, output_path)
            else:
                raise ValueError(f"Format non supporté: {output_format}")
            
            # Statistiques
            speakers = list(set(seg["speaker"] for seg in aligned_segments))
            total_duration = max(seg["end"] for seg in aligned_segments)
            
            print(f"\n✅ Traitement terminé!")
            print(f"📊 Statistiques:")
            print(f"   - Durée totale: {total_duration:.2f} secondes")
            print(f"   - Nombre de locuteurs: {len(speakers)}")
            print(f"   - Locuteurs: {', '.join(speakers)}")
            print(f"   - Langue détectée: {whisper_result.get('language', 'Inconnue')}")
            print(f"   - Fichier de sortie: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            print(f"❌ Erreur lors du traitement: {e}")
            raise
    
    def _save_as_text(self, aligned_segments: List[Dict], output_path: Path):
        """Sauvegarde en format texte avec locuteurs."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for seg in aligned_segments:
                start_time = self._format_time(seg["start"])
                end_time = self._format_time(seg["end"])
                f.write(f"[{start_time} - {end_time}] {seg['speaker']}: {seg['text']}\n\n")
    
    def _save_as_json(self, aligned_segments: List[Dict], whisper_result: Dict, output_path: Path):
        """Sauvegarde en format JSON."""
        result = {
            "metadata": {
                "language": whisper_result.get("language"),
                "duration": whisper_result.get("duration"),
                "speakers": list(set(seg["speaker"] for seg in aligned_segments))
            },
            "segments": aligned_segments
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    def _save_as_srt(self, aligned_segments: List[Dict], output_path: Path):
        """Sauvegarde en format SRT avec locuteurs."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, seg in enumerate(aligned_segments, 1):
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
        description="Transcription avec identification des locuteurs (Whisper + pyannote.audio)",
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
        processor = WhisperSpeakerDiarization(
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
