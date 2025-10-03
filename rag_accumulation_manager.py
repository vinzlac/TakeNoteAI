#!/usr/bin/env python3
"""
Gestionnaire d'accumulation intelligente pour RAG
Permet d'accumuler ou de nettoyer selon le contexte
"""

import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import argparse

class RAGAccumulationManager:
    """Gestionnaire d'accumulation RAG."""
    
    def __init__(self):
        """Initialise le gestionnaire."""
        print("🔄 Initialisation du gestionnaire d'accumulation RAG...")
        
        self.chroma_db_path = Path("./chroma_db")
        self.json_files_pattern = "*advanced_rag*.json"
        self.config_file = Path("./rag_accumulation_config.json")
        
        # Configuration par défaut
        self.default_config = {
            "max_documents": 1000,
            "quality_threshold": 0.8,
            "max_age_days": 90,
            "auto_cleanup": True,
            "projects": {},
            "accumulation_strategy": "intelligent"  # intelligent, always, never
        }
        
        self.config = self._load_config()
        print("✅ Gestionnaire initialisé")
    
    def _load_config(self) -> Dict:
        """Charge la configuration."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Fusionner avec la config par défaut
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                print(f"⚠️  Erreur lors du chargement de la config: {e}")
                return self.default_config.copy()
        else:
            self._save_config(self.default_config)
            return self.default_config.copy()
    
    def _save_config(self, config: Dict):
        """Sauvegarde la configuration."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Erreur lors de la sauvegarde de la config: {e}")
    
    def get_accumulation_status(self) -> Dict:
        """Obtient le statut de l'accumulation."""
        status = {
            "chroma_db_exists": self.chroma_db_path.exists(),
            "chroma_db_size_mb": 0,
            "chroma_db_files": 0,
            "json_files_count": 0,
            "json_files_size_mb": 0,
            "oldest_file": None,
            "newest_file": None,
            "quality_score": 0.0,
            "recommendation": "unknown"
        }
        
        # ChromaDB
        if self.chroma_db_path.exists():
            status["chroma_db_size_mb"] = self._get_directory_size_mb(self.chroma_db_path)
            status["chroma_db_files"] = len(list(self.chroma_db_path.rglob("*")))
        
        # Fichiers JSON
        json_files = list(Path(".").glob(self.json_files_pattern))
        status["json_files_count"] = len(json_files)
        
        if json_files:
            total_size = sum(f.stat().st_size for f in json_files)
            status["json_files_size_mb"] = total_size / 1024 / 1024
            
            # Dates
            dates = []
            for file in json_files:
                try:
                    # Extraire la date du nom de fichier
                    date_str = file.stem.split('_')[-1]  # Dernière partie
                    if len(date_str) == 14:  # Format YYYYMMDDHHMMSS
                        date = datetime.strptime(date_str, '%Y%m%d%H%M%S')
                        dates.append((file, date))
                except:
                    dates.append((file, datetime.fromtimestamp(file.stat().st_mtime)))
            
            if dates:
                dates.sort(key=lambda x: x[1])
                status["oldest_file"] = dates[0][0].name
                status["newest_file"] = dates[-1][0].name
        
        # Qualité estimée
        status["quality_score"] = self._estimate_quality(json_files)
        
        # Recommandation
        status["recommendation"] = self._get_recommendation(status)
        
        return status
    
    def _get_directory_size_mb(self, directory: Path) -> float:
        """Calcule la taille d'un répertoire en MB."""
        if not directory.exists():
            return 0
        
        total_size = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return total_size / 1024 / 1024
    
    def _estimate_quality(self, json_files: List[Path]) -> float:
        """Estime la qualité des données accumulées."""
        if not json_files:
            return 0.0
        
        quality_scores = []
        for file in json_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Métriques de qualité - chercher dans la structure réelle
                text_length = 0
                segment_count = 0
                keyword_count = 0
                
                # Chercher le texte dans différentes structures possibles
                if 'full_text' in data:
                    text_length = len(data['full_text'])
                elif 'transcription' in data and 'full_text' in data['transcription']:
                    text_length = len(data['transcription']['full_text'])
                elif 'segments' in data:
                    # Calculer la longueur totale des segments
                    for segment in data['segments']:
                        if 'text' in segment:
                            text_length += len(segment['text'])
                elif 'transcription' in data and 'segments' in data['transcription']:
                    # Structure RAG standard
                    for segment in data['transcription']['segments']:
                        if 'text' in segment:
                            text_length += len(segment['text'])
                
                # Compter les segments
                if 'segments' in data:
                    segment_count = len(data['segments'])
                elif 'transcription' in data and 'segments' in data['transcription']:
                    segment_count = len(data['transcription']['segments'])
                
                # Compter les mots-clés
                if 'keywords' in data:
                    keyword_count = len(data['keywords'])
                elif 'business_keywords' in data:
                    keyword_count = len(data['business_keywords'])
                elif 'custom_keywords_applied' in data:
                    keyword_count = len(data['custom_keywords_applied'])
                
                # Score basé sur la richesse du contenu
                if text_length > 10000 and segment_count > 10:
                    quality_scores.append(0.9)
                elif text_length > 5000 and segment_count > 5:
                    quality_scores.append(0.7)
                elif text_length > 1000:
                    quality_scores.append(0.5)
                else:
                    quality_scores.append(0.3)
                    
            except Exception as e:
                print(f"⚠️  Erreur lors de l'analyse de {file.name}: {e}")
                quality_scores.append(0.1)
        
        return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
    
    def _get_recommendation(self, status: Dict) -> str:
        """Génère une recommandation basée sur le statut."""
        strategy = self.config.get("accumulation_strategy", "intelligent")
        
        if strategy == "never":
            return "clean"
        elif strategy == "always":
            return "accumulate"
        
        # Stratégie intelligente
        quality = status["quality_score"]
        doc_count = status["json_files_count"]
        size_mb = status["json_files_size_mb"]
        
        if quality < self.config["quality_threshold"]:
            return "clean"
        elif doc_count > self.config["max_documents"]:
            return "clean"
        elif size_mb > 100:  # Plus de 100MB
            return "clean"
        else:
            return "accumulate"
    
    def should_accumulate(self, new_file: Path = None) -> bool:
        """Détermine si on doit accumuler ou nettoyer."""
        status = self.get_accumulation_status()
        recommendation = status["recommendation"]
        
        print(f"📊 Statut d'accumulation:")
        print(f"   - Documents: {status['json_files_count']}")
        print(f"   - Taille: {status['json_files_size_mb']:.2f} MB")
        print(f"   - Qualité: {status['quality_score']:.2f}")
        print(f"   - Recommandation: {recommendation}")
        
        if new_file:
            print(f"   - Nouveau fichier: {new_file.name}")
        
        return recommendation == "accumulate"
    
    def clean_old_data(self, days: int = None) -> bool:
        """Nettoie les données anciennes."""
        days = days or self.config["max_age_days"]
        cutoff_date = datetime.now() - timedelta(days=days)
        
        print(f"🧹 Nettoyage des données de plus de {days} jours...")
        
        json_files = list(Path(".").glob(self.json_files_pattern))
        deleted_count = 0
        
        for file in json_files:
            try:
                # Vérifier l'âge du fichier
                file_date = datetime.fromtimestamp(file.stat().st_mtime)
                if file_date < cutoff_date:
                    file.unlink()
                    deleted_count += 1
                    print(f"✅ Supprimé (ancien): {file.name}")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression de {file.name}: {e}")
        
        print(f"✅ {deleted_count} fichier(s) ancien(s) supprimé(s)")
        return deleted_count > 0
    
    def clean_low_quality_data(self) -> bool:
        """Nettoie les données de faible qualité."""
        print("🧹 Nettoyage des données de faible qualité...")
        
        json_files = list(Path(".").glob(self.json_files_pattern))
        deleted_count = 0
        
        for file in json_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Vérifier la qualité
                text_length = len(data.get('full_text', ''))
                segment_count = len(data.get('segments', []))
                
                if text_length < 1000 or segment_count < 5:
                    file.unlink()
                    deleted_count += 1
                    print(f"✅ Supprimé (faible qualité): {file.name}")
                    
            except Exception as e:
                print(f"❌ Erreur lors de l'analyse de {file.name}: {e}")
        
        print(f"✅ {deleted_count} fichier(s) de faible qualité supprimé(s)")
        return deleted_count > 0
    
    def configure_accumulation(self, strategy: str, max_docs: int = None, quality_threshold: float = None):
        """Configure la stratégie d'accumulation."""
        print(f"⚙️  Configuration de l'accumulation: {strategy}")
        
        if strategy in ["intelligent", "always", "never"]:
            self.config["accumulation_strategy"] = strategy
        
        if max_docs:
            self.config["max_documents"] = max_docs
        
        if quality_threshold:
            self.config["quality_threshold"] = quality_threshold
        
        self._save_config(self.config)
        print("✅ Configuration sauvegardée")
    
    def show_recommendations(self):
        """Affiche les recommandations détaillées."""
        status = self.get_accumulation_status()
        
        print("📊 Analyse d'accumulation RAG")
        print("=" * 50)
        
        print(f"🗄️  ChromaDB:")
        print(f"   - Présent: {'✅' if status['chroma_db_exists'] else '❌'}")
        print(f"   - Taille: {status['chroma_db_size_mb']:.2f} MB")
        print(f"   - Fichiers: {status['chroma_db_files']}")
        
        print(f"\n📄 Fichiers JSON:")
        print(f"   - Nombre: {status['json_files_count']}")
        print(f"   - Taille: {status['json_files_size_mb']:.2f} MB")
        print(f"   - Plus ancien: {status['oldest_file'] or 'N/A'}")
        print(f"   - Plus récent: {status['newest_file'] or 'N/A'}")
        
        print(f"\n📊 Qualité:")
        print(f"   - Score: {status['quality_score']:.2f}/1.0")
        print(f"   - Seuil configuré: {self.config['quality_threshold']}")
        
        print(f"\n🎯 Recommandation: {status['recommendation'].upper()}")
        
        # Recommandations détaillées
        if status['recommendation'] == 'accumulate':
            print("\n✅ ACCUMULER - Raisons:")
            print("   - Qualité des données acceptable")
            print("   - Taille raisonnable")
            print("   - Contexte métier enrichi")
            print("\n💡 Actions recommandées:")
            print("   - Continuer l'accumulation")
            print("   - Monitorer la qualité")
            print("   - Nettoyer périodiquement les anciennes données")
        
        elif status['recommendation'] == 'clean':
            print("\n🧹 NETTOYER - Raisons:")
            if status['quality_score'] < self.config['quality_threshold']:
                print("   - Qualité insuffisante")
            if status['json_files_count'] > self.config['max_documents']:
                print("   - Trop de documents")
            if status['json_files_size_mb'] > 100:
                print("   - Taille excessive")
            
            print("\n💡 Actions recommandées:")
            print("   - Nettoyer les données existantes")
            print("   - Repartir d'une base propre")
            print("   - Améliorer la qualité des nouvelles données")


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Gestionnaire d'accumulation intelligente pour RAG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s --status                    # Afficher le statut d'accumulation
  %(prog)s --recommendations           # Afficher les recommandations détaillées
  %(prog)s --should-accumulate         # Déterminer si accumuler
  %(prog)s --clean-old --days 30       # Nettoyer les données anciennes
  %(prog)s --clean-quality             # Nettoyer les données de faible qualité
  %(prog)s --configure intelligent     # Configurer la stratégie
  %(prog)s --configure always          # Toujours accumuler
  %(prog)s --configure never           # Toujours nettoyer
        """
    )
    
    parser.add_argument("--status", action="store_true", help="Afficher le statut")
    parser.add_argument("--recommendations", action="store_true", help="Afficher les recommandations")
    parser.add_argument("--should-accumulate", action="store_true", help="Déterminer si accumuler")
    parser.add_argument("--clean-old", action="store_true", help="Nettoyer les données anciennes")
    parser.add_argument("--clean-quality", action="store_true", help="Nettoyer les données de faible qualité")
    parser.add_argument("--configure", choices=["intelligent", "always", "never"], help="Configurer la stratégie")
    parser.add_argument("--max-docs", type=int, help="Nombre maximum de documents")
    parser.add_argument("--quality-threshold", type=float, help="Seuil de qualité")
    parser.add_argument("--days", type=int, default=30, help="Âge maximum en jours pour le nettoyage")
    
    args = parser.parse_args()
    
    try:
        manager = RAGAccumulationManager()
        
        if args.status:
            status = manager.get_accumulation_status()
            print(f"📊 Statut: {status['json_files_count']} docs, {status['json_files_size_mb']:.2f} MB, qualité {status['quality_score']:.2f}")
        
        elif args.recommendations:
            manager.show_recommendations()
        
        elif args.should_accumulate:
            should_accumulate = manager.should_accumulate()
            print(f"🎯 Recommandation: {'ACCUMULER' if should_accumulate else 'NETTOYER'}")
            return 0 if should_accumulate else 1
        
        elif args.clean_old:
            success = manager.clean_old_data(args.days)
            return 0 if success else 1
        
        elif args.clean_quality:
            success = manager.clean_low_quality_data()
            return 0 if success else 1
        
        elif args.configure:
            manager.configure_accumulation(
                args.configure, 
                args.max_docs, 
                args.quality_threshold
            )
        
        else:
            # Par défaut, afficher les recommandations
            manager.show_recommendations()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️  Opération interrompue par l'utilisateur")
        return 1
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
