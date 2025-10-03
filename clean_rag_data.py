#!/usr/bin/env python3
"""
Script pour nettoyer les données RAG (ChromaDB et fichiers JSON)
Permet de repartir d'une base propre
"""

import os
import shutil
import argparse
from pathlib import Path
from typing import List

class RAGDataCleaner:
    """Nettoyeur de données RAG."""
    
    def __init__(self):
        """Initialise le nettoyeur."""
        print("🧹 Initialisation du nettoyeur de données RAG...")
        
        # Chemins des données à nettoyer
        self.chroma_db_path = Path("./chroma_db")
        self.json_files_pattern = "*advanced_rag*.json"
        self.summary_files_pattern = "resume_*.md"
        
        print("✅ Nettoyeur initialisé")
    
    def list_cleanable_data(self) -> dict:
        """Liste les données qui peuvent être nettoyées."""
        data = {
            "chroma_db": {
                "exists": self.chroma_db_path.exists(),
                "size_mb": self._get_directory_size_mb(self.chroma_db_path) if self.chroma_db_path.exists() else 0,
                "files": list(self.chroma_db_path.rglob("*")) if self.chroma_db_path.exists() else []
            },
            "json_files": {
                "files": list(Path(".").glob(self.json_files_pattern)),
                "count": len(list(Path(".").glob(self.json_files_pattern)))
            },
            "summary_files": {
                "files": list(Path(".").glob(self.summary_files_pattern)),
                "count": len(list(Path(".").glob(self.summary_files_pattern)))
            }
        }
        
        return data
    
    def _get_directory_size_mb(self, directory: Path) -> float:
        """Calcule la taille d'un répertoire en MB."""
        if not directory.exists():
            return 0
        
        total_size = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return total_size / 1024 / 1024
    
    def clean_chroma_db(self, confirm: bool = False) -> bool:
        """Nettoie la base de données ChromaDB."""
        if not self.chroma_db_path.exists():
            print("✅ ChromaDB n'existe pas, rien à nettoyer")
            return True
        
        if not confirm:
            print(f"⚠️  ChromaDB trouvé: {self.chroma_db_path}")
            print(f"   Taille: {self._get_directory_size_mb(self.chroma_db_path):.2f} MB")
            print(f"   Fichiers: {len(list(self.chroma_db_path.rglob('*')))}")
            
            response = input("\n❓ Voulez-vous supprimer ChromaDB ? (oui/non): ")
            if response.lower() not in ["oui", "o", "yes", "y"]:
                print("❌ Suppression annulée")
                return False
        
        try:
            shutil.rmtree(self.chroma_db_path)
            print("✅ ChromaDB supprimé avec succès")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression de ChromaDB: {e}")
            return False
    
    def clean_json_files(self, confirm: bool = False, pattern: str = None) -> bool:
        """Nettoie les fichiers JSON de transcription."""
        pattern = pattern or self.json_files_pattern
        json_files = list(Path(".").glob(pattern))
        
        if not json_files:
            print("✅ Aucun fichier JSON trouvé, rien à nettoyer")
            return True
        
        if not confirm:
            print(f"⚠️  {len(json_files)} fichier(s) JSON trouvé(s):")
            for i, file in enumerate(json_files, 1):
                size_mb = file.stat().st_size / 1024 / 1024
                print(f"   {i:2d}. {file.name} ({size_mb:.2f} MB)")
            
            response = input(f"\n❓ Voulez-vous supprimer ces {len(json_files)} fichier(s) JSON ? (oui/non): ")
            if response.lower() not in ["oui", "o", "yes", "y"]:
                print("❌ Suppression annulée")
                return False
        
        deleted_count = 0
        for file in json_files:
            try:
                file.unlink()
                deleted_count += 1
                print(f"✅ Supprimé: {file.name}")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression de {file.name}: {e}")
        
        print(f"✅ {deleted_count}/{len(json_files)} fichier(s) JSON supprimé(s)")
        return deleted_count == len(json_files)
    
    def clean_summary_files(self, confirm: bool = False) -> bool:
        """Nettoie les fichiers de résumé."""
        summary_files = list(Path(".").glob(self.summary_files_pattern))
        
        if not summary_files:
            print("✅ Aucun fichier de résumé trouvé, rien à nettoyer")
            return True
        
        if not confirm:
            print(f"⚠️  {len(summary_files)} fichier(s) de résumé trouvé(s):")
            for i, file in enumerate(summary_files, 1):
                print(f"   {i:2d}. {file.name}")
            
            response = input(f"\n❓ Voulez-vous supprimer ces {len(summary_files)} fichier(s) de résumé ? (oui/non): ")
            if response.lower() not in ["oui", "o", "yes", "y"]:
                print("❌ Suppression annulée")
                return False
        
        deleted_count = 0
        for file in summary_files:
            try:
                file.unlink()
                deleted_count += 1
                print(f"✅ Supprimé: {file.name}")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression de {file.name}: {e}")
        
        print(f"✅ {deleted_count}/{len(summary_files)} fichier(s) de résumé supprimé(s)")
        return deleted_count == len(summary_files)
    
    def clean_keywords_files(self, confirm: bool = False) -> bool:
        """Nettoie les fichiers de mots-clés générés."""
        keywords_patterns = [
            "keywords_generated_*.txt",
            "mots_cles_*.json",
            "keywords_*.txt"
        ]
        
        keywords_files = []
        for pattern in keywords_patterns:
            keywords_files.extend(list(Path(".").glob(pattern)))
        
        if not keywords_files:
            print("✅ Aucun fichier de mots-clés trouvé, rien à nettoyer")
            return True
        
        if not confirm:
            print(f"⚠️  {len(keywords_files)} fichier(s) de mots-clés trouvé(s):")
            for i, file in enumerate(keywords_files, 1):
                print(f"   {i:2d}. {file.name}")
            
            response = input(f"\n❓ Voulez-vous supprimer ces {len(keywords_files)} fichier(s) de mots-clés ? (oui/non): ")
            if response.lower() not in ["oui", "o", "yes", "y"]:
                print("❌ Suppression annulée")
                return False
        
        deleted_count = 0
        for file in keywords_files:
            try:
                file.unlink()
                deleted_count += 1
                print(f"✅ Supprimé: {file.name}")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression de {file.name}: {e}")
        
        print(f"✅ {deleted_count}/{len(keywords_files)} fichier(s) de mots-clés supprimé(s)")
        return deleted_count == len(keywords_files)
    
    def clean_all(self, confirm: bool = False) -> bool:
        """Nettoie toutes les données RAG."""
        print("🧹 Nettoyage complet des données RAG...")
        
        # Lister les données
        data = self.list_cleanable_data()
        
        total_files = 0
        total_size_mb = 0
        
        if data["chroma_db"]["exists"]:
            total_files += len(data["chroma_db"]["files"])
            total_size_mb += data["chroma_db"]["size_mb"]
        
        total_files += data["json_files"]["count"]
        total_files += data["summary_files"]["count"]
        
        # Afficher le résumé
        print(f"\n📊 Données à nettoyer:")
        print(f"   - ChromaDB: {data['chroma_db']['size_mb']:.2f} MB ({len(data['chroma_db']['files'])} fichiers)")
        print(f"   - Fichiers JSON: {data['json_files']['count']} fichiers")
        print(f"   - Fichiers de résumé: {data['summary_files']['count']} fichiers")
        print(f"   - Total: {total_size_mb:.2f} MB, {total_files} fichiers")
        
        if total_files == 0:
            print("✅ Aucune donnée à nettoyer")
            return True
        
        if not confirm:
            response = input(f"\n❓ Voulez-vous supprimer TOUTES ces données ? (oui/non): ")
            if response.lower() not in ["oui", "o", "yes", "y"]:
                print("❌ Nettoyage annulé")
                return False
        
        # Nettoyer dans l'ordre
        success = True
        
        print("\n🧹 Nettoyage en cours...")
        
        # 1. ChromaDB
        if data["chroma_db"]["exists"]:
            print("   1. Nettoyage de ChromaDB...")
            success &= self.clean_chroma_db(confirm=True)
        
        # 2. Fichiers JSON
        if data["json_files"]["count"] > 0:
            print("   2. Nettoyage des fichiers JSON...")
            success &= self.clean_json_files(confirm=True)
        
        # 3. Fichiers de résumé
        if data["summary_files"]["count"] > 0:
            print("   3. Nettoyage des fichiers de résumé...")
            success &= self.clean_summary_files(confirm=True)
        
        # 4. Fichiers de mots-clés
        print("   4. Nettoyage des fichiers de mots-clés...")
        success &= self.clean_keywords_files(confirm=True)
        
        if success:
            print("\n🎉 Nettoyage complet terminé avec succès !")
            print("💡 Vous pouvez maintenant relancer le RAG avec une base propre")
        else:
            print("\n⚠️  Nettoyage terminé avec des erreurs")
        
        return success
    
    def show_status(self):
        """Affiche le statut des données RAG."""
        print("📊 Statut des données RAG:")
        print("=" * 50)
        
        data = self.list_cleanable_data()
        
        # ChromaDB
        if data["chroma_db"]["exists"]:
            print(f"🗄️  ChromaDB: ✅ Présent")
            print(f"   Taille: {data['chroma_db']['size_mb']:.2f} MB")
            print(f"   Fichiers: {len(data['chroma_db']['files'])}")
        else:
            print(f"🗄️  ChromaDB: ❌ Absent")
        
        # Fichiers JSON
        print(f"📄 Fichiers JSON: {data['json_files']['count']} fichier(s)")
        for file in data["json_files"]["files"]:
            size_mb = file.stat().st_size / 1024 / 1024
            print(f"   - {file.name} ({size_mb:.2f} MB)")
        
        # Fichiers de résumé
        print(f"📝 Fichiers de résumé: {data['summary_files']['count']} fichier(s)")
        for file in data["summary_files"]["files"]:
            print(f"   - {file.name}")
        
        # Recommandations
        total_files = len(data["json_files"]["files"]) + len(data["summary_files"]["files"])
        if data["chroma_db"]["exists"]:
            total_files += len(data["chroma_db"]["files"])
        
        if total_files > 0:
            print(f"\n💡 Recommandation: Nettoyage recommandé avant un nouveau RAG")
            print(f"   Utilisez: python clean_rag_data.py --all")
        else:
            print(f"\n✅ Base propre, prêt pour un nouveau RAG")


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Nettoie les données RAG pour repartir d'une base propre",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s --status                           # Afficher le statut
  %(prog)s --all                              # Nettoyer tout (avec confirmation)
  %(prog)s --all --force                      # Nettoyer tout sans confirmation
  %(prog)s --chromadb                         # Nettoyer seulement ChromaDB
  %(prog)s --json                             # Nettoyer seulement les JSON
  %(prog)s --summaries                        # Nettoyer seulement les résumés
  %(prog)s --keywords                         # Nettoyer seulement les mots-clés
        """
    )
    
    parser.add_argument("--status", action="store_true", help="Afficher le statut des données")
    parser.add_argument("--all", action="store_true", help="Nettoyer toutes les données")
    parser.add_argument("--chromadb", action="store_true", help="Nettoyer ChromaDB")
    parser.add_argument("--json", action="store_true", help="Nettoyer les fichiers JSON")
    parser.add_argument("--summaries", action="store_true", help="Nettoyer les fichiers de résumé")
    parser.add_argument("--keywords", action="store_true", help="Nettoyer les fichiers de mots-clés")
    parser.add_argument("--force", action="store_true", help="Nettoyer sans demander confirmation")
    
    args = parser.parse_args()
    
    try:
        cleaner = RAGDataCleaner()
        
        # Afficher le statut
        if args.status or not any([args.all, args.chromadb, args.json, args.summaries, args.keywords]):
            cleaner.show_status()
            return 0
        
        # Nettoyage complet
        if args.all:
            success = cleaner.clean_all(confirm=not args.force)
            return 0 if success else 1
        
        # Nettoyages spécifiques
        success = True
        
        if args.chromadb:
            success &= cleaner.clean_chroma_db(confirm=not args.force)
        
        if args.json:
            success &= cleaner.clean_json_files(confirm=not args.force)
        
        if args.summaries:
            success &= cleaner.clean_summary_files(confirm=not args.force)
        
        if args.keywords:
            success &= cleaner.clean_keywords_files(confirm=not args.force)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️  Nettoyage interrompu par l'utilisateur")
        return 1
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
