#!/usr/bin/env python3
"""
Script pour lister tous les mots-clés extraits des documents dans ChromaDB
"""

import chromadb
import json
from collections import Counter
from pathlib import Path

def list_all_keywords():
    """Liste tous les mots-clés des documents dans ChromaDB."""
    try:
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
            
            # Extraire les mots-clés du texte
            keywords = extract_keywords_from_text(document)
            document_keywords[doc_id] = keywords
            
            if keywords:
                print(f"   🔑 Mots-clés détectés ({len(keywords)}):")
                for j, (keyword, score) in enumerate(keywords[:10], 1):  # Top 10
                    print(f"      {j:2d}. {keyword:<25} (score: {score:.3f})")
                all_keywords.extend([kw[0] for kw in keywords])
            else:
                print("   ❌ Aucun mot-clé détecté")
        
        # Analyse globale
        print("\n" + "=" * 60)
        print("🔍 ANALYSE GLOBALE DES MOTS-CLÉS")
        print("=" * 60)
        
        if all_keywords:
            # Compter les occurrences
            keyword_counts = Counter(all_keywords)
            
            print(f"📊 Statistiques:")
            print(f"   - Total mots-clés uniques: {len(keyword_counts)}")
            print(f"   - Total occurrences: {sum(keyword_counts.values())}")
            print(f"   - Moyenne par document: {sum(keyword_counts.values()) / len(results['ids']):.1f}")
            
            print(f"\n🏆 Top 20 des mots-clés les plus fréquents:")
            for i, (keyword, count) in enumerate(keyword_counts.most_common(20), 1):
                print(f"   {i:2d}. {keyword:<30} ({count} fois)")
            
            # Sauvegarder les résultats
            output_data = {
                "total_documents": len(results['ids']),
                "total_unique_keywords": len(keyword_counts),
                "total_occurrences": sum(keyword_counts.values()),
                "top_keywords": dict(keyword_counts.most_common(50)),
                "document_keywords": document_keywords
            }
            
            output_file = "all_keywords_analysis.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ Analyse sauvegardée: {output_file}")
            
        else:
            print("❌ Aucun mot-clé trouvé dans les documents")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def extract_keywords_from_text(text):
    """Extrait les mots-clés d'un texte (version simplifiée)."""
    # Mots-clés métiers typiques
    business_keywords = [
        "projet", "équipe", "développement", "architecture", "code", "review",
        "maintenance", "go-live", "application", "système", "technologie",
        "processus", "méthodologie", "qualité", "performance", "sécurité",
        "intégration", "déploiement", "test", "validation", "documentation",
        "formation", "support", "monitoring", "backup", "migration",
        "analyse", "conception", "implémentation", "optimisation", "résolution",
        "planification", "gestion", "coordination", "collaboration", "communication",
        "réunion", "présentation", "formation", "audit", "compliance",
        "budget", "ressources", "planning", "livrable", "milestone"
    ]
    
    text_lower = text.lower()
    found_keywords = []
    
    for keyword in business_keywords:
        if keyword in text_lower:
            # Calculer un score basé sur la fréquence
            count = text_lower.count(keyword)
            score = min(count * 0.1 + 0.5, 1.0)  # Score entre 0.5 et 1.0
            found_keywords.append((keyword, score))
    
    # Trier par score décroissant
    found_keywords.sort(key=lambda x: x[1], reverse=True)
    
    return found_keywords[:15]  # Top 15

if __name__ == "__main__":
    list_all_keywords()

