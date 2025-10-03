#!/usr/bin/env python3
"""
Script pour extraire les mots-clés réels des documents dans ChromaDB avec KeyBERT
"""

import chromadb
import json
from collections import Counter
from pathlib import Path

def extract_keywords_with_keybert():
    """Extrait les mots-clés avec KeyBERT des documents dans ChromaDB."""
    try:
        # Import KeyBERT
        from keybert import KeyBERT
        from sentence_transformers import SentenceTransformer
        
        print("🔄 Initialisation de KeyBERT...")
        model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        kw_model = KeyBERT(model=model)
        
        # Connexion à ChromaDB
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_collection("transcriptions")
        
        # Récupérer tous les documents
        results = collection.get(include=['documents', 'metadatas'])
        
        if not results['ids']:
            print("❌ Aucun document trouvé dans la base")
            return
        
        print(f"📊 Analyse de {len(results['ids'])} documents dans ChromaDB")
        print("=" * 60)
        
        all_keywords = []
        document_keywords = {}
        
        for i, doc_id in enumerate(results['ids']):
            metadata = results['metadatas'][i]
            document = results['documents'][i]
            
            print(f"\n📄 Document {i+1}: {metadata.get('filename', 'N/A')}")
            print(f"   ID: {doc_id}")
            print(f"   Durée: {metadata.get('duration', 0):.1f}s")
            print(f"   Langue: {metadata.get('language', 'N/A')}")
            print(f"   Méthode: {metadata.get('transcription_method', 'N/A')}")
            
            # Extraire les mots-clés avec KeyBERT
            print("   🔍 Extraction des mots-clés avec KeyBERT...")
            keywords = kw_model.extract_keywords(
                document,
                keyphrase_ngram_range=(1, 3),
                stop_words='french',
                top_n=15,
                use_mmr=True,
                diversity=0.5
            )
            
            # Filtrer les mots-clés métiers
            business_keywords = filter_business_keywords(keywords, document)
            document_keywords[doc_id] = business_keywords
            
            if business_keywords:
                print(f"   🔑 Mots-clés métiers détectés ({len(business_keywords)}):")
                for j, (keyword, score) in enumerate(business_keywords, 1):
                    print(f"      {j:2d}. {keyword:<30} (score: {score:.3f})")
                all_keywords.extend([kw[0] for kw in business_keywords])
            else:
                print("   ❌ Aucun mot-clé métier détecté")
        
        # Analyse globale
        print("\n" + "=" * 60)
        print("🔍 ANALYSE GLOBALE DES MOTS-CLÉS MÉTIERS")
        print("=" * 60)
        
        if all_keywords:
            # Compter les occurrences
            keyword_counts = Counter(all_keywords)
            
            print(f"📊 Statistiques:")
            print(f"   - Total mots-clés uniques: {len(keyword_counts)}")
            print(f"   - Total occurrences: {sum(keyword_counts.values())}")
            print(f"   - Moyenne par document: {sum(keyword_counts.values()) / len(results['ids']):.1f}")
            
            print(f"\n🏆 Top 20 des mots-clés métiers les plus fréquents:")
            for i, (keyword, count) in enumerate(keyword_counts.most_common(20), 1):
                print(f"   {i:2d}. {keyword:<35} ({count} fois)")
            
            # Sauvegarder les résultats
            output_data = {
                "total_documents": len(results['ids']),
                "total_unique_keywords": len(keyword_counts),
                "total_occurrences": sum(keyword_counts.values()),
                "top_keywords": dict(keyword_counts.most_common(50)),
                "document_keywords": document_keywords,
                "extraction_method": "KeyBERT + filtrage métier"
            }
            
            output_file = "keywords_from_embeddings.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ Analyse sauvegardée: {output_file}")
            
        else:
            print("❌ Aucun mot-clé métier trouvé dans les documents")
        
    except ImportError:
        print("❌ KeyBERT non installé. Installez avec: pip install keybert")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def filter_business_keywords(keywords, text):
    """Filtre les mots-clés pour ne garder que ceux liés au métier."""
    # Mots-clés métiers typiques
    business_indicators = [
        "projet", "équipe", "développement", "architecture", "code", "review",
        "maintenance", "go-live", "application", "système", "technologie",
        "processus", "méthodologie", "qualité", "performance", "sécurité",
        "intégration", "déploiement", "test", "validation", "documentation",
        "formation", "support", "monitoring", "backup", "migration",
        "analyse", "conception", "implémentation", "optimisation", "résolution",
        "planification", "gestion", "coordination", "collaboration", "communication",
        "réunion", "présentation", "formation", "audit", "compliance",
        "budget", "ressources", "planning", "livrable", "milestone",
        "client", "utilisateur", "interface", "base de données", "serveur",
        "réseau", "cloud", "mobile", "web", "api", "framework", "library"
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

if __name__ == "__main__":
    extract_keywords_with_keybert()

