#!/usr/bin/env python3
# Version optimisée pour Mac M4
# Générée automatiquement par optimize_rag_for_m4.py

import warnings
import torch
import os

# Optimisations M4 - DÉBUT
if torch.backends.mps.is_available():
    torch.set_num_threads(14)
    os.environ['OMP_NUM_THREADS'] = '14'
    os.environ['MKL_NUM_THREADS'] = '14'
    os.environ['NUMEXPR_NUM_THREADS'] = '14'
    print("🚀 Optimisations Mac M4 activées")
else:
    print("⚠️  MPS non disponible - Utilisation CPU uniquement")
# Optimisations M4 - FIN

#!/usr/bin/env python3
"""
Script avancé de transcription avec RAG et extraction de mots-clés métiers
Combine SpeechBrain, KeyBERT, Sentence Transformers et ChromaDB
"""

import os
import sys
import argparse
import json
import warnings
import torch
import os

# Optimisations M4
if torch.backends.mps.is_available():
    torch.set_num_threads(14)
    os.environ['OMP_NUM_THREADS'] = '14'
    os.environ['MKL_NUM_THREADS'] = '14'
    os.environ['NUMEXPR_NUM_THREADS'] = '14'
    print("🚀 Optimisations M4 activées")

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import numpy as np

# Supprimer les avertissements dès le début
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

# Imports pour la transcription
import whisper  # Import Whisper en premier
try:
    import torch
    import torchaudio
    from speechbrain.inference import EncoderDecoderASR
    SPEECHBRAIN_AVAILABLE = True
except ImportError:
    print("⚠️  SpeechBrain non disponible, utilisation de Whisper en fallback")
    SPEECHBRAIN_AVAILABLE = False

# Imports pour RAG et embeddings
try:
    from sentence_transformers import SentenceTransformer
    from keybert import KeyBERT
    import chromadb
    from chromadb.config import Settings
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Composants RAG non disponibles: {e}")
    print("💡 Installez avec: pip install sentence-transformers keybert chromadb")
    RAG_AVAILABLE = False

# Imports pour le traitement de texte
try:
    import spacy
    from spacy.lang.fr.stop_words import STOP_WORDS
    SPACY_AVAILABLE = True
except ImportError:
    print("⚠️  spaCy non disponible, utilisation de stop words basiques")
    SPACY_AVAILABLE = False

class AdvancedRAGTranscription:
    """Classe pour transcription avancée avec RAG et extraction de mots-clés métiers."""
    
    def _get_optimal_device(self):
        """Détecte le device optimal pour M4."""
        if torch.backends.mps.is_available():
            print("✅ GPU M4 détecté via MPS")
            return "mps"
        elif torch.cuda.is_available():
            print("✅ GPU CUDA détecté")
            return "cuda"
        else:
            print("⚠️  Utilisation CPU uniquement")
            return "cpu"
    
    def __init__(self, 
                 transcription_model="speechbrain/asr-crdnn-commonvoice-fr",
                 embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                 device=None):
        """
        Initialise les modèles pour transcription, embeddings et extraction de mots-clés.
        
        Args:
            transcription_model (str): Modèle de transcription SpeechBrain
            embedding_model (str): Modèle d'embeddings Sentence Transformers
            device (str): Device à utiliser
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        print(f"🔧 Initialisation des modèles avancés...")
        print(f"   Device: {self.device}")
        
        # Initialiser le modèle de transcription
        self._init_transcription_model(transcription_model)
        
        # Initialiser les composants RAG si disponibles
        if RAG_AVAILABLE:
            self._init_rag_components(embedding_model)
        else:
            print("⚠️  Mode dégradé: RAG non disponible")
    
    def _init_transcription_model(self, model_name: str):
        """Initialise le modèle de transcription."""
        print("🔄 Chargement du modèle de transcription...")
        
        if SPEECHBRAIN_AVAILABLE and "whisper" not in model_name.lower():
            try:
                # Essayer SpeechBrain avec gestion d'erreur améliorée
                from speechbrain.pretrained import EncoderDecoderASR
                self.asr_model = EncoderDecoderASR.from_hparams(
                    source=model_name,
                    savedir=f"pretrained_models/{model_name.split('/')[-1]}"
                )
                self.transcription_method = "speechbrain"
                print(f"✅ Modèle SpeechBrain chargé: {model_name}")
            except Exception as e:
                error_msg = str(e).lower()
                if "401" in error_msg or "authentication" in error_msg or "token" in error_msg:
                    print(f"⚠️  Erreur d'authentification SpeechBrain: Token Hugging Face requis")
                    print("💡 Solution: huggingface-cli login")
                elif "not found" in error_msg:
                    print(f"⚠️  Modèle SpeechBrain non trouvé: {model_name}")
                else:
                    print(f"⚠️  Erreur SpeechBrain: {e}")
                print("🔄 Basculement vers Whisper...")
                self.asr_model = whisper.load_model("base", device=self.device)
            
            # Optimisations M4
            if self.device == "mps":
                print("🚀 Optimisations M4 appliquées au modèle Whisper")
                # Mixed precision pour MPS
                if hasattr(self.asr_model, 'half'):
                    self.asr_model.half()
                self.transcription_method = "whisper"
        else:
            # Utiliser directement Whisper
            if "whisper" in model_name.lower():
                model_size = model_name.split("-")[-1] if "-" in model_name else "base"
                self.asr_model = whisper.load_model(model_size, device=self.device)
            else:
                self.asr_model = whisper.load_model("base", device=self.device)
            
            # Optimisations M4
            if self.device == "mps":
                print("🚀 Optimisations M4 appliquées au modèle Whisper")
                # Mixed precision pour MPS
                if hasattr(self.asr_model, 'half'):
                    self.asr_model.half()
            self.transcription_method = "whisper"
    
    def _init_rag_components(self, embedding_model: str):
        """Initialise les composants RAG."""
        print("🔄 Initialisation des composants RAG...")
        
        # Modèle d'embeddings
        print("   - Chargement du modèle d'embeddings...")
        self.embedding_model = SentenceTransformer(embedding_model, device=self.device)
        
        # Extracteur de mots-clés
        print("   - Initialisation de KeyBERT...")
        self.keybert_model = KeyBERT(model=self.embedding_model)
        
        # Base de données vectorielle
        print("   - Configuration de ChromaDB...")
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        # Collection pour les documents
        try:
            self.collection = self.chroma_client.get_collection("transcriptions")
        except:
            self.collection = self.chroma_client.create_collection("transcriptions")
        
        # Modèle spaCy pour le traitement de texte
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("fr_core_news_sm")
            except OSError:
                print("   ⚠️  Modèle spaCy français non trouvé, installation...")
                os.system("python -m spacy download fr_core_news_sm")
                self.nlp = spacy.load("fr_core_news_sm")
        
        print("✅ Composants RAG initialisés")
    
    def transcribe_audio(self, audio_path: str) -> Dict:
        """
        Transcrit l'audio avec le modèle choisi.
        
        Args:
            audio_path (str): Chemin vers le fichier audio
            
        Returns:
            Dict: Résultat de la transcription
        """
        print(f"🎤 Transcription avec {self.transcription_method}...")
        
        if self.transcription_method == "speechbrain":
            # Transcription avec API SpeechBrain moderne et correcte
            try:
                # Méthode SpeechBrain moderne - utiliser transcribe_file
                text = self.asr_model.transcribe_file(audio_path)
                
                # Formatage du résultat
                result = {
                    "text": text,
                    "segments": [{"start": 0, "end": len(text)/10, "text": text}],
                    "language": "fr",
                    "method": "speechbrain"
                }
            except Exception as e:
                print(f"⚠️  Erreur SpeechBrain lors de la transcription: {e}")
                print("🔄 Basculement vers Whisper...")
                # Fallback vers Whisper - charger un nouveau modèle Whisper
                import whisper
                whisper_model = whisper.load_model("base", device=self.device)
            
            # Optimisations M4
            if self.device == "mps":
                print("🚀 Optimisations M4 appliquées au modèle Whisper")
                # Mixed precision pour MPS
                if hasattr(self.asr_model, 'half'):
                    self.asr_model.half()
                result = whisper_model.transcribe(audio_path, verbose=True)
                result["method"] = "whisper"
        else:
            # Whisper fallback
            result = self.asr_model.transcribe(audio_path, verbose=True)
            result["method"] = "whisper"
        
        return result
    
    def extract_business_keywords(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Extrait les mots-clés métiers du texte.
        
        Args:
            text (str): Texte à analyser
            top_k (int): Nombre de mots-clés à extraire
            
        Returns:
            List[Tuple[str, float]]: Mots-clés avec scores
        """
        if not RAG_AVAILABLE:
            return []
        
        print("🔍 Extraction des mots-clés métiers...")
        
        # Extraction avec KeyBERT
        keywords = self.keybert_model.extract_keywords(
            text, 
            keyphrase_ngram_range=(1, 3),
            stop_words='french' if SPACY_AVAILABLE else None,
            top_n=top_k,
            use_mmr=True,
            diversity=0.5
        )
        
        # Filtrage des mots-clés métiers
        business_keywords = self._filter_business_keywords(keywords, text)
        
        print(f"✅ {len(business_keywords)} mots-clés métiers extraits")
        return business_keywords
    
    def _filter_business_keywords(self, keywords: List[Tuple[str, float]], text: str) -> List[Tuple[str, float]]:
        """
        Filtre les mots-clés pour ne garder que ceux liés au métier.
        
        Args:
            keywords (List[Tuple[str, float]]): Mots-clés extraits
            text (str): Texte original
            
        Returns:
            List[Tuple[str, float]]: Mots-clés métiers filtrés
        """
        # Mots-clés métiers typiques (à adapter selon le domaine)
        business_indicators = [
            "projet", "équipe", "développement", "architecture", "code", "review",
            "maintenance", "go-live", "application", "système", "technologie",
            "processus", "méthodologie", "qualité", "performance", "sécurité",
            "intégration", "déploiement", "test", "validation", "documentation",
            "formation", "support", "monitoring", "backup", "migration"
        ]
        
        filtered_keywords = []
        text_lower = text.lower()
        
        for keyword, score in keywords:
            keyword_lower = keyword.lower()
            
            # Vérifier si le mot-clé contient des indicateurs métiers
            is_business = any(indicator in keyword_lower for indicator in business_indicators)
            
            # Vérifier la fréquence dans le texte
            frequency = text_lower.count(keyword_lower)
            
            # Score combiné: score KeyBERT + fréquence + indicateur métier
            combined_score = score + (frequency * 0.1) + (0.2 if is_business else 0)
            
            if combined_score > 0.3:  # Seuil minimum
                filtered_keywords.append((keyword, combined_score))
        
        # Trier par score décroissant
        filtered_keywords.sort(key=lambda x: x[1], reverse=True)
        
        return filtered_keywords[:10]  # Top 10
    
    def create_embeddings(self, text: str) -> np.ndarray:
        """
        Crée les embeddings vectoriels du texte.
        
        Args:
            text (str): Texte à vectoriser
            
        Returns:
            np.ndarray: Embeddings vectoriels
        """
        if not RAG_AVAILABLE:
            return np.array([])
        
        print("🧠 Génération des embeddings...")
        embeddings = self.embedding_model.encode(text)
        return embeddings
    
    def store_in_vector_db(self, text: str, metadata: Dict, embeddings: np.ndarray):
        """
        Stocke le texte et ses embeddings dans la base vectorielle.
        
        Args:
            text (str): Texte à stocker
            metadata (Dict): Métadonnées
            embeddings (np.ndarray): Embeddings vectoriels
        """
        if not RAG_AVAILABLE:
            return
        
        print("💾 Stockage dans la base vectorielle...")
        
        # ID unique basé sur le timestamp
        doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Ajouter à la collection
        self.collection.add(
            documents=[text],
            embeddings=[embeddings.tolist()],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        print(f"✅ Document stocké avec ID: {doc_id}")
    
    def search_similar_documents(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Recherche des documents similaires dans la base vectorielle.
        
        Args:
            query (str): Requête de recherche
            top_k (int): Nombre de résultats à retourner
            
        Returns:
            List[Dict]: Documents similaires
        """
        if not RAG_AVAILABLE:
            return []
        
        print(f"🔍 Recherche de documents similaires: '{query}'")
        
        # Embeddings de la requête
        query_embeddings = self.embedding_model.encode(query)
        
        # Recherche dans la base
        results = self.collection.query(
            query_embeddings=[query_embeddings.tolist()],
            n_results=top_k
        )
        
        # Formatage des résultats
        similar_docs = []
        for i in range(len(results['documents'][0])):
            similar_docs.append({
                "text": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i],
                "id": results['ids'][0][i]
            })
        
        print(f"✅ {len(similar_docs)} documents similaires trouvés")
        return similar_docs
    
    def process_audio_complete(self, audio_path: str, output_path: str = None) -> Dict:
        """
        Traite un fichier audio complet : transcription + RAG + mots-clés.
        
        Args:
            audio_path (str): Chemin vers le fichier audio
            output_path (str): Chemin de sortie
            
        Returns:
            Dict: Résultats complets
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Le fichier {audio_path} n'existe pas")
        
        # Générer le nom de sortie
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = audio_path.parent / f"{audio_path.stem}_advanced_rag_{timestamp}.json"
        else:
            output_path = Path(output_path)
        
        print(f"🚀 Traitement avancé: {audio_path.name}")
        print(f"   Taille: {audio_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        try:
            # 1. Transcription
            transcription_result = self.transcribe_audio(str(audio_path))
            full_text = transcription_result["text"]
            
            # 2. Extraction de mots-clés métiers
            business_keywords = self.extract_business_keywords(full_text)
            
            # 3. Génération d'embeddings
            embeddings = self.create_embeddings(full_text)
            
            # 4. Métadonnées
            metadata = {
                "filename": audio_path.name,
                "size_mb": round(audio_path.stat().st_size / 1024 / 1024, 2),
                "transcription_method": self.transcription_method,
                "language": transcription_result.get("language", "unknown"),
                "duration": round(transcription_result.get("duration", 0), 2),
                "timestamp": datetime.now().isoformat(),
                "business_keywords_count": len(business_keywords)
            }
            
            # 5. Stockage dans la base vectorielle
            if RAG_AVAILABLE and len(embeddings) > 0:
                self.store_in_vector_db(full_text, metadata, embeddings)
            
            # 6. Résultats complets
            results = {
                "transcription": transcription_result,
                "business_keywords": business_keywords,
                "metadata": metadata,
                "embeddings_available": RAG_AVAILABLE and len(embeddings) > 0,
                "vector_db_stored": RAG_AVAILABLE
            }
            
            # 7. Sauvegarde
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            # 8. Statistiques
            print(f"\n✅ Traitement avancé terminé!")
            print(f"📊 Statistiques:")
            print(f"   - Méthode de transcription: {self.transcription_method}")
            print(f"   - Longueur du texte: {len(full_text)} caractères")
            print(f"   - Mots-clés métiers: {len(business_keywords)}")
            print(f"   - Embeddings générés: {'Oui' if RAG_AVAILABLE else 'Non'}")
            print(f"   - Stocké en base vectorielle: {'Oui' if RAG_AVAILABLE else 'Non'}")
            print(f"   - Fichier de sortie: {output_path}")
            
            return results
            
        except Exception as e:
            print(f"❌ Erreur lors du traitement: {e}")
            raise


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Transcription avancée avec RAG et extraction de mots-clés métiers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s audio.mp3                           # Traitement complet
  %(prog)s audio.mp3 -o results.json          # Sortie personnalisée
  %(prog)s audio.mp3 --search "architecture"  # Recherche dans la base
        """
    )
    
    parser.add_argument("input", help="Fichier audio d'entrée")
    parser.add_argument("-o", "--output", help="Fichier de sortie JSON")
    parser.add_argument("--search", help="Rechercher des documents similaires")
    parser.add_argument("--transcription-model", 
                       default="speechbrain/asr-crdnn-commonvoice-fr",
                       help="Modèle de transcription SpeechBrain")
    parser.add_argument("--embedding-model",
                       default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                       help="Modèle d'embeddings")
    parser.add_argument("--device", choices=["cpu", "cuda", "mps"],
                       help="Device à utiliser")
    
    args = parser.parse_args()
    
    try:
        # Initialiser le processeur
        processor = AdvancedRAGTranscription(
            transcription_model=args.transcription_model,
            embedding_model=args.embedding_model,
            device=args.device
        )
        
        if args.search:
            # Recherche dans la base existante
            results = processor.search_similar_documents(args.search)
            print(f"\n🔍 Résultats de recherche pour '{args.search}':")
            for i, doc in enumerate(results, 1):
                print(f"{i}. Distance: {doc['distance']:.3f}")
                print(f"   Texte: {doc['text'][:100]}...")
                print(f"   Métadonnées: {doc['metadata']}")
                print()
        else:
            # Traitement complet
            results = processor.process_audio_complete(args.input, args.output)
            
            print(f"\n🎉 Succès! Résultats sauvegardés: {args.output or 'auto-généré'}")
            
            # Afficher les mots-clés métiers
            if results.get("business_keywords"):
                print(f"\n🔑 Mots-clés métiers détectés:")
                for keyword, score in results["business_keywords"][:5]:
                    print(f"   - {keyword} (score: {score:.3f})")
        
    except KeyboardInterrupt:
        print("\n⏹️  Traitement interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

