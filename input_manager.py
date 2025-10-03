#!/usr/bin/env python3
"""
Gestionnaire des fichiers d'entrée audio pour TakeNoteAI
"""

import os
from pathlib import Path
from typing import List, Optional

class InputManager:
    """Gestionnaire des fichiers d'entrée audio."""
    
    def __init__(self, input_dir="input"):
        """Initialise le gestionnaire d'entrée."""
        self.input_dir = Path(input_dir)
        self.input_dir.mkdir(exist_ok=True)
        
        # Créer un .gitkeep pour maintenir la structure
        gitkeep_path = self.input_dir / ".gitkeep"
        if not gitkeep_path.exists():
            gitkeep_path.touch()
    
    def get_audio_files(self, pattern="*") -> List[Path]:
        """Récupère tous les fichiers audio disponibles."""
        audio_extensions = ["*.mp3", "*.m4a", "*.wav", "*.flac", "*.aac", "*.ogg"]
        audio_files = []
        
        for extension in audio_extensions:
            files = list(self.input_dir.glob(f"{pattern}{extension}"))
            audio_files.extend(files)
        
        return sorted(audio_files)
    
    def find_audio_file(self, filename: str) -> Optional[Path]:
        """Trouve un fichier audio par nom (avec ou sans extension)."""
        # Essayer d'abord dans le répertoire input
        input_path = self.input_dir / filename
        if input_path.exists():
            return input_path
        
        # Essayer avec différentes extensions
        base_name = Path(filename).stem
        for ext in [".mp3", ".m4a", ".wav", ".flac", ".aac", ".ogg"]:
            test_path = self.input_dir / f"{base_name}{ext}"
            if test_path.exists():
                return test_path
        
        # Essayer dans le répertoire courant (fallback)
        current_path = Path(filename)
        if current_path.exists():
            return current_path
        
        # Essayer avec extensions dans le répertoire courant
        for ext in [".mp3", ".m4a", ".wav", ".flac", ".aac", ".ogg"]:
            test_path = Path(f"{base_name}{ext}")
            if test_path.exists():
                return test_path
        
        return None
    
    def list_available_files(self) -> List[dict]:
        """Liste tous les fichiers audio disponibles avec leurs infos."""
        audio_files = self.get_audio_files()
        file_info = []
        
        for file_path in audio_files:
            try:
                stat = file_path.stat()
                size_mb = stat.st_size / 1024 / 1024
                file_info.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size_mb": round(size_mb, 2),
                    "extension": file_path.suffix
                })
            except (OSError, PermissionError):
                continue
        
        return file_info
    
    def copy_to_input(self, source_path: str) -> Optional[Path]:
        """Copie un fichier audio vers le répertoire input."""
        source = Path(source_path)
        if not source.exists():
            return None
        
        destination = self.input_dir / source.name
        
        try:
            import shutil
            shutil.copy2(source, destination)
            return destination
        except Exception as e:
            print(f"❌ Erreur lors de la copie: {e}")
            return None
    
    def move_to_input(self, source_path: str) -> Optional[Path]:
        """Déplace un fichier audio vers le répertoire input."""
        source = Path(source_path)
        if not source.exists():
            return None
        
        destination = self.input_dir / source.name
        
        try:
            source.rename(destination)
            return destination
        except Exception as e:
            print(f"❌ Erreur lors du déplacement: {e}")
            return None
    
    def get_status(self) -> dict:
        """Retourne le statut du répertoire d'entrée."""
        audio_files = self.get_audio_files()
        total_size = 0
        
        for file_path in audio_files:
            try:
                total_size += file_path.stat().st_size
            except (OSError, PermissionError):
                continue
        
        return {
            "input_dir": str(self.input_dir),
            "file_count": len(audio_files),
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "files": self.list_available_files()
        }

def resolve_audio_path(filename: str) -> Optional[Path]:
    """Fonction utilitaire pour résoudre un chemin de fichier audio."""
    input_mgr = InputManager()
    return input_mgr.find_audio_file(filename)

def main():
    """Fonction principale pour tester le gestionnaire."""
    print("🎵 Gestionnaire de fichiers d'entrée audio TakeNoteAI")
    print("=" * 55)
    
    # Initialiser le gestionnaire
    input_mgr = InputManager()
    
    # Afficher le statut
    status = input_mgr.get_status()
    print(f"\n📁 Répertoire d'entrée: {status['input_dir']}")
    print(f"📊 Fichiers audio: {status['file_count']}")
    print(f"💾 Taille totale: {status['total_size_mb']} MB")
    
    if status['files']:
        print(f"\n🎵 Fichiers audio disponibles:")
        print("-" * 40)
        for file_info in status['files']:
            print(f"   📄 {file_info['name']} ({file_info['size_mb']} MB)")
    else:
        print(f"\n⚠️  Aucun fichier audio trouvé dans input/")
        print(f"   Placez vos fichiers .mp3, .m4a, .wav, etc. dans le répertoire input/")
    
    # Exemples d'utilisation
    print(f"\n🚀 Exemples d'utilisation:")
    print("-" * 30)
    
    examples = [
        "python rag_ultra_simple.py audio.mp3",
        "   → Cherche automatiquement dans input/audio.mp3",
        "",
        "python advanced_rag_transcription.py input/meeting.m4a",
        "   → Utilise le chemin complet",
        "",
        "input_mgr = InputManager()",
        "file_path = input_mgr.find_audio_file('audio')",
        "   → Trouve automatiquement audio.mp3, audio.m4a, etc."
    ]
    
    for example in examples:
        print(f"   {example}")
    
    print(f"\n✅ Le répertoire input/ est maintenant configuré !")

if __name__ == "__main__":
    main()
