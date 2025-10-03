#!/usr/bin/env python3
"""
Gestionnaire centralisé des répertoires de sortie pour TakeNoteAI
"""

import os
from pathlib import Path
from datetime import datetime

class OutputManager:
    """Gestionnaire des répertoires de sortie."""
    
    def __init__(self, base_output_dir="output"):
        """Initialise le gestionnaire de sortie."""
        self.base_output_dir = Path(base_output_dir)
        self._create_output_structure()
    
    def _create_output_structure(self):
        """Crée la structure de répertoires de sortie."""
        directories = [
            "transcriptions",  # Fichiers JSON de transcription RAG
            "keywords",        # Fichiers de mots-clés générés
            "summaries",       # Résumés générés (MD)
            "workflows",       # Résultats de workflows
            "analysis",        # Analyses et rapports
            "configs",         # Fichiers de configuration générés
            "benchmarks",      # Résultats de benchmarks
            "backups"          # Sauvegardes de scripts
        ]
        
        for directory in directories:
            dir_path = self.base_output_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Créer un .gitkeep pour maintenir la structure
            gitkeep_path = dir_path / ".gitkeep"
            if not gitkeep_path.exists():
                gitkeep_path.touch()
    
    def get_transcription_path(self, filename):
        """Génère le chemin pour un fichier de transcription."""
        return self.base_output_dir / "transcriptions" / filename
    
    def get_keywords_path(self, filename):
        """Génère le chemin pour un fichier de mots-clés."""
        return self.base_output_dir / "keywords" / filename
    
    def get_summary_path(self, filename):
        """Génère le chemin pour un fichier de résumé."""
        return self.base_output_dir / "summaries" / filename
    
    def get_workflow_path(self, filename):
        """Génère le chemin pour un fichier de workflow."""
        return self.base_output_dir / "workflows" / filename
    
    def get_analysis_path(self, filename):
        """Génère le chemin pour un fichier d'analyse."""
        return self.base_output_dir / "analysis" / filename
    
    def get_config_path(self, filename):
        """Génère le chemin pour un fichier de configuration."""
        return self.base_output_dir / "configs" / filename
    
    def get_benchmark_path(self, filename):
        """Génère le chemin pour un fichier de benchmark."""
        return self.base_output_dir / "benchmarks" / filename
    
    def get_backup_path(self, filename):
        """Génère le chemin pour un fichier de sauvegarde."""
        return self.base_output_dir / "backups" / filename
    
    def generate_filename(self, prefix, extension, timestamp=None):
        """Génère un nom de fichier avec timestamp."""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"{prefix}_{timestamp}.{extension}"
    
    def get_status(self):
        """Retourne le statut des répertoires de sortie."""
        status = {
            "base_dir": str(self.base_output_dir),
            "directories": {},
            "total_size": 0
        }
        
        for item in self.base_output_dir.iterdir():
            if item.is_dir():
                size = self._get_directory_size(item)
                file_count = len(list(item.rglob("*"))) - 1  # -1 pour .gitkeep
                status["directories"][item.name] = {
                    "size_mb": round(size, 2),
                    "files": file_count
                }
                status["total_size"] += size
        
        status["total_size"] = round(status["total_size"], 2)
        return status
    
    def _get_directory_size(self, directory):
        """Calcule la taille d'un répertoire en MB."""
        total_size = 0
        try:
            for file_path in directory.rglob('*'):
                if file_path.is_file() and file_path.name != '.gitkeep':
                    total_size += file_path.stat().st_size
        except (PermissionError, OSError):
            pass
        return total_size / 1024 / 1024
    
    def clean_directory(self, directory_name, keep_recent=5):
        """Nettoie un répertoire en gardant les N fichiers les plus récents."""
        target_dir = self.base_output_dir / directory_name
        if not target_dir.exists():
            return
        
        # Récupérer tous les fichiers (sauf .gitkeep)
        files = [f for f in target_dir.iterdir() if f.is_file() and f.name != '.gitkeep']
        
        if len(files) <= keep_recent:
            return
        
        # Trier par date de modification (plus récent en premier)
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Supprimer les anciens fichiers
        files_to_delete = files[keep_recent:]
        for file_path in files_to_delete:
            try:
                file_path.unlink()
                print(f"🗑️  Supprimé: {file_path.name}")
            except Exception as e:
                print(f"❌ Erreur suppression {file_path.name}: {e}")
    
    def clean_all(self, keep_recent=5):
        """Nettoie tous les répertoires de sortie."""
        directories = ["transcriptions", "keywords", "summaries", "workflows", "analysis", "configs", "benchmarks"]
        for directory in directories:
            print(f"🧹 Nettoyage de {directory}/...")
            self.clean_directory(directory, keep_recent)
    
    def move_existing_files(self):
        """Déplace les fichiers existants vers la nouvelle structure."""
        print("📁 Migration des fichiers existants vers output/...")
        
        # Patterns de fichiers à déplacer
        file_patterns = {
            "*_advanced_rag_*.json": "transcriptions",
            "workflow_results_*.json": "workflows", 
            "keywords_generated_*.txt": "keywords",
            "resume_*.md": "summaries",
            "all_keywords_analysis.json": "analysis",
            "benchmark_results.json": "benchmarks",
            "m4_config.py": "configs",
            "rag_accumulation_config.json": "configs",
            "*.backup": "backups"
        }
        
        moved_count = 0
        for pattern, target_dir in file_patterns.items():
            files = list(Path(".").glob(pattern))
            for file_path in files:
                if file_path.is_file():
                    target_path = self.base_output_dir / target_dir / file_path.name
                    try:
                        file_path.rename(target_path)
                        print(f"✅ Déplacé: {file_path.name} → output/{target_dir}/")
                        moved_count += 1
                    except Exception as e:
                        print(f"❌ Erreur déplacement {file_path.name}: {e}")
        
        print(f"🎉 Migration terminée: {moved_count} fichiers déplacés")

def main():
    """Fonction principale pour tester le gestionnaire."""
    print("🔧 Gestionnaire de répertoires de sortie TakeNoteAI")
    print("=" * 55)
    
    # Initialiser le gestionnaire
    output_mgr = OutputManager()
    
    # Afficher le statut
    status = output_mgr.get_status()
    print(f"\n📊 Statut des répertoires de sortie:")
    print(f"   📁 Répertoire de base: {status['base_dir']}")
    print(f"   💾 Taille totale: {status['total_size']} MB")
    
    for dir_name, info in status["directories"].items():
        print(f"   📂 {dir_name}/: {info['files']} fichiers, {info['size_mb']} MB")
    
    # Proposer la migration
    print(f"\n🔄 Migration des fichiers existants?")
    print("   Cette opération déplacera les fichiers générés vers output/")
    
    # Migration automatique (pour le script)
    output_mgr.move_existing_files()
    
    # Afficher le nouveau statut
    print(f"\n📊 Nouveau statut après migration:")
    status = output_mgr.get_status()
    for dir_name, info in status["directories"].items():
        if info['files'] > 0:
            print(f"   📂 {dir_name}/: {info['files']} fichiers, {info['size_mb']} MB")

if __name__ == "__main__":
    main()
