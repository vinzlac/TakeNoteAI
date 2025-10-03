#!/usr/bin/env python3
"""
Script pour régénérer la base de données ChromaDB à partir des transcriptions JSON
"""

import os
import sys
import warnings
from pathlib import Path
import json
import shutil

# Optimisations M4
import torch
if torch.backends.mps.is_available():
    torch.set_num_threads(14)
    os.environ['OMP_NUM_THREADS'] = '14'
    os.environ['MKL_NUM_THREADS'] = '14'
    os.environ['NUMEXPR_NUM_THREADS'] = '14'

# Supprimer les avertissements
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

try:
    from sentence_transformers import SentenceTransformer
    from keybert import KeyBERT
    import chromadb
    from chromadb.config import Settings
    print("✅ Modules RAG importés avec succès")
except ImportError as e:
    print(f"❌ Erreur import modules RAG: {e}")
    print("💡 Installez les dépendances avec: ./install_advanced.sh")
    sys.exit(1)

class ChromaDBRegenerator:
    """Régénérateur de la base de données ChromaDB."""
    
    def __init__(self):
        """Initialise le régénérateur."""
        print("🔧 Initialisation du régénérateur ChromaDB...")
        
        # Initialiser les modèles
        print("🔄 Chargement du modèle d'embeddings...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("🔄 Initialisation de KeyBERT...")
        self.keybert_model = KeyBERT(model=self.embedding_model)
        
        # Configuration ChromaDB
        self.chroma_dir = Path("chroma_db")
        self.client = None
        self.collection = None
    
    def backup_existing_chromadb(self):
        """Sauvegarde la base ChromaDB existante."""
        if self.chroma_dir.exists():
            backup_dir = Path("chroma_db_backup")
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            shutil.copytree(self.chroma_dir, backup_dir)
            print(f"💾 Sauvegarde créée: {backup_dir}")
            return True
        return False
    
    def clear_chromadb(self):
        """Vide la base de données ChromaDB."""
        if self.chroma_dir.exists():
            shutil.rmtree(self.chroma_dir)
            print("🗑️  Base ChromaDB existante supprimée")
        
        self.chroma_dir.mkdir(exist_ok=True)
        print("📁 Nouveau répertoire ChromaDB créé")
    
    def initialize_chromadb(self):
        """Initialise une nouvelle base ChromaDB."""
        print("🔄 Initialisation de ChromaDB...")
        
        self.client = chromadb.PersistentClient(
            path=str(self.chroma_dir),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Créer ou récupérer la collection
        try:
            self.collection = self.client.get_collection("transcriptions")
            print("✅ Collection 'transcriptions' récupérée")
        except:
            self.collection = self.client.create_collection(
                name="transcriptions",
                metadata={"description": "Transcriptions audio avec embeddings"}
            )
            print("✅ Collection 'transcriptions' créée")
    
    def process_transcription_file(self, json_file: Path):
        """Traite un fichier de transcription JSON."""
        print(f"📄 Traitement de: {json_file.name}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extraire les informations
            transcription_data = data.get('transcription', {})
            full_text = transcription_data.get('full_text', '')
            segments = transcription_data.get('segments', [])
            
            if not full_text and not segments:
                print(f"⚠️  Aucun texte trouvé dans {json_file.name}")
                return False
            
            # Utiliser le texte complet ou combiner les segments
            if full_text:
                text_to_process = full_text
            else:
                text_to_process = ' '.join([seg.get('text', '') for seg in segments])
            
            if not text_to_process.strip():
                print(f"⚠️  Texte vide dans {json_file.name}")
                return False
            
            # Générer les embeddings
            print(f"   🧠 Génération des embeddings...")
            embedding = self.embedding_model.encode(text_to_process).tolist()
            
            # Extraire les mots-clés
            print(f"   🔍 Extraction des mots-clés...")
            keywords = self.keybert_model.extract_keywords(
                text_to_process,
                keyphrase_ngram_range=(1, 2),
                stop_words='french',
                use_maxsum=True,
                nr_candidates=20,
                top_k=10
            )
            
            # Préparer les métadonnées
            metadata = {
                "source_file": str(json_file.name),
                "transcription_method": data.get('transcription_method', 'unknown'),
                "audio_duration": data.get('audio_duration', 0),
                "text_length": len(text_to_process),
                "segments_count": len(segments),
                "keywords": ', '.join([kw[0] for kw in keywords]),
                "processing_date": data.get('timestamp', 'unknown')
            }
            
            # Stocker dans ChromaDB
            doc_id = f"doc_{json_file.stem}"
            self.collection.add(
                documents=[text_to_process],
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            print(f"   ✅ Document ajouté avec ID: {doc_id}")
            print(f"   📊 Mots-clés: {', '.join([kw[0] for kw in keywords[:5]])}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Erreur traitement {json_file.name}: {e}")
            return False
    
    def regenerate_from_transcriptions(self, transcriptions_dir: Path = None):
        """Régénère la base ChromaDB à partir des transcriptions."""
        if transcriptions_dir is None:
            transcriptions_dir = Path("output/transcriptions")
        
        if not transcriptions_dir.exists():
            print(f"❌ Répertoire non trouvé: {transcriptions_dir}")
            return False
        
        # Trouver tous les fichiers JSON de transcription
        json_files = list(transcriptions_dir.glob("*advanced_rag*.json"))
        
        if not json_files:
            print(f"❌ Aucun fichier de transcription trouvé dans {transcriptions_dir}")
            return False
        
        print(f"📁 {len(json_files)} fichiers de transcription trouvés")
        
        # Sauvegarder l'ancienne base
        self.backup_existing_chromadb()
        
        # Nettoyer et réinitialiser
        self.clear_chromadb()
        self.initialize_chromadb()
        
        # Traiter chaque fichier
        success_count = 0
        for json_file in sorted(json_files):
            if self.process_transcription_file(json_file):
                success_count += 1
        
        print(f"\n🎉 Régénération terminée!")
        print(f"✅ {success_count}/{len(json_files)} fichiers traités avec succès")
        
        # Afficher le statut de la base
        count = self.collection.count()
        print(f"📊 Base ChromaDB: {count} documents stockés")
        
        return success_count > 0
    
    def get_status(self):
        """Retourne le statut de la base ChromaDB."""
        if not self.chroma_dir.exists():
            return {"status": "not_found", "count": 0}
        
        try:
            if not self.client:
                self.initialize_chromadb()
            
            count = self.collection.count()
            return {"status": "active", "count": count}
        except Exception as e:
            return {"status": "error", "error": str(e)}

def main():
    """Fonction principale."""
    print("🔄 Régénérateur de base ChromaDB TakeNoteAI")
    print("=" * 50)
    
    # Vérifier les répertoires
    output_dir = Path("output")
    transcriptions_dir = output_dir / "transcriptions"
    
    if not output_dir.exists():
        print("❌ Répertoire output/ non trouvé")
        print("💡 Exécutez d'abord des transcriptions RAG")
        return 1
    
    if not transcriptions_dir.exists():
        print("❌ Répertoire output/transcriptions/ non trouvé")
        print("💡 Exécutez d'abord des transcriptions RAG")
        return 1
    
    # Initialiser le régénérateur
    regenerator = ChromaDBRegenerator()
    
    # Afficher le statut actuel
    status = regenerator.get_status()
    if status["status"] == "active":
        print(f"📊 Base ChromaDB actuelle: {status['count']} documents")
    
    # Régénérer
    print(f"\n🚀 Début de la régénération...")
    success = regenerator.regenerate_from_transcriptions(transcriptions_dir)
    
    if success:
        print(f"\n✅ Régénération réussie!")
        print(f"💡 La base ChromaDB est maintenant à jour")
        print(f"🗂️  Sauvegarde disponible dans chroma_db_backup/")
    else:
        print(f"\n❌ Régénération échouée")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
