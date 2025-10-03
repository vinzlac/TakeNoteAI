#!/usr/bin/env python3
"""
Démonstration simple des fonctionnalités RAG avancées
"""

import sys
from pathlib import Path

def demo_keyword_extraction():
    """Démonstration de l'extraction de mots-clés métiers."""
    print("🔍 Démonstration: Extraction de mots-clés métiers")
    print("=" * 50)
    
    # Texte d'exemple (transcription d'une réunion)
    sample_text = """
    Bonjour, nous allons discuter de l'architecture du projet. 
    L'équipe de développement a terminé la phase de code review. 
    Nous devons maintenant procéder au déploiement en production. 
    La maintenance du système sera assurée par l'équipe support. 
    Les tests d'intégration sont en cours de validation.
    """
    
    try:
        from keybert import KeyBERT
        from sentence_transformers import SentenceTransformer
        
        # Initialiser KeyBERT
        model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        kw_model = KeyBERT(model=model)
        
        # Extraire les mots-clés
        keywords = kw_model.extract_keywords(
            sample_text,
            keyphrase_ngram_range=(1, 3),
            stop_words='french',
            top_n=10,
            use_mmr=True,
            diversity=0.5
        )
        
        print("📝 Texte analysé:")
        print(f"   {sample_text.strip()}")
        print()
        print("🔑 Mots-clés métiers extraits:")
        for i, (keyword, score) in enumerate(keywords, 1):
            print(f"   {i}. {keyword} (score: {score:.3f})")
        
        return True
        
    except ImportError:
        print("❌ KeyBERT non installé. Installez avec: pip install keybert")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def demo_embeddings():
    """Démonstration des embeddings sémantiques."""
    print("\n🧠 Démonstration: Embeddings sémantiques")
    print("=" * 50)
    
    texts = [
        "Architecture du système et développement",
        "Code review et tests d'intégration", 
        "Déploiement en production et maintenance"
    ]
    
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
        
        # Initialiser le modèle
        model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        
        # Générer les embeddings
        embeddings = model.encode(texts)
        
        print("📝 Textes analysés:")
        for i, text in enumerate(texts, 1):
            print(f"   {i}. {text}")
        print()
        print("🧠 Embeddings générés:")
        print(f"   - Nombre de textes: {len(texts)}")
        print(f"   - Dimension des embeddings: {embeddings.shape[1]}")
        print(f"   - Type: {embeddings.dtype}")
        
        # Calculer les similarités
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(embeddings)
        
        print("\n🔗 Similarités entre les textes:")
        for i in range(len(texts)):
            for j in range(i+1, len(texts)):
                sim = similarities[i][j]
                print(f"   - Texte {i+1} ↔ Texte {j+1}: {sim:.3f}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("💡 Installez avec: pip install sentence-transformers scikit-learn")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def demo_vector_db():
    """Démonstration de la base de données vectorielle."""
    print("\n💾 Démonstration: Base de données vectorielle")
    print("=" * 50)
    
    try:
        import chromadb
        from chromadb.config import Settings
        from sentence_transformers import SentenceTransformer
        
        # Initialiser ChromaDB (nouvelle configuration)
        client = chromadb.PersistentClient(path="./demo_chroma_db")
        
        # Créer une collection
        try:
            collection = client.get_collection("demo_documents")
        except:
            collection = client.create_collection("demo_documents")
        
        # Modèle d'embeddings
        model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        
        # Documents d'exemple
        documents = [
            "Architecture microservices et déploiement Docker",
            "Tests unitaires et intégration continue",
            "Monitoring et alertes système en production"
        ]
        
        # Générer les embeddings
        embeddings = model.encode(documents)
        
        # Ajouter à la base
        collection.add(
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=[
                {"type": "architecture", "priority": "high"},
                {"type": "testing", "priority": "medium"},
                {"type": "monitoring", "priority": "high"}
            ],
            ids=["doc1", "doc2", "doc3"]
        )
        
        print("📝 Documents stockés:")
        for i, doc in enumerate(documents, 1):
            print(f"   {i}. {doc}")
        
        # Recherche
        query = "déploiement et production"
        query_embedding = model.encode([query])
        
        results = collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=2
        )
        
        print(f"\n🔍 Recherche: '{query}'")
        print("📋 Résultats:")
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0], 
            results['metadatas'][0], 
            results['distances'][0]
        ), 1):
            print(f"   {i}. {doc}")
            print(f"      Métadonnées: {metadata}")
            print(f"      Distance: {distance:.3f}")
        
        # Nettoyer
        import shutil
        shutil.rmtree("./demo_chroma_db", ignore_errors=True)
        
        return True
        
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("💡 Installez avec: pip install chromadb sentence-transformers")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Fonction principale de démonstration."""
    print("🎯 Démonstration des fonctionnalités RAG avancées")
    print("=" * 60)
    
    success_count = 0
    total_demos = 3
    
    # Démonstration 1: Extraction de mots-clés
    if demo_keyword_extraction():
        success_count += 1
    
    # Démonstration 2: Embeddings
    if demo_embeddings():
        success_count += 1
    
    # Démonstration 3: Base vectorielle
    if demo_vector_db():
        success_count += 1
    
    # Résumé
    print(f"\n📊 Résumé de la démonstration:")
    print(f"   - Démonstrations réussies: {success_count}/{total_demos}")
    
    if success_count == total_demos:
        print("🎉 Toutes les fonctionnalités RAG sont opérationnelles!")
        print("\n🚀 Pour utiliser avec vos fichiers audio:")
        print("   python advanced_rag_transcription.py votre_audio.mp3")
    else:
        print("⚠️  Certaines fonctionnalités nécessitent une installation.")
        print("\n💡 Pour installer toutes les dépendances:")
        print("   ./install_advanced.sh")
    
    print(f"\n📋 Scripts disponibles:")
    print(f"   - advanced_rag_transcription.py : Script principal")
    print(f"   - install_advanced.sh : Installation des dépendances")
    print(f"   - demo_rag.py : Cette démonstration")

if __name__ == "__main__":
    main()
