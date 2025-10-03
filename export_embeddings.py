#!/usr/bin/env python3
"""
Script pour exporter les embeddings de ChromaDB vers un fichier
"""

import chromadb
import json
import numpy as np
from pathlib import Path

def export_embeddings():
    """Exporte les embeddings de ChromaDB vers un fichier JSON."""
    try:
        # Connexion à ChromaDB
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_collection("transcriptions")
        
        # Récupérer tous les documents avec embeddings
        results = collection.get(include=['embeddings', 'documents', 'metadatas'])
        
        if not results['ids']:
            print("❌ Aucun document trouvé dans la base")
            return
        
        # Préparer les données
        embedding_dim = len(results['embeddings'][0]) if results['embeddings'] and len(results['embeddings']) > 0 else 0
        export_data = {
            "total_documents": len(results['ids']),
            "embedding_dimension": embedding_dim,
            "documents": []
        }
        
        for i, doc_id in enumerate(results['ids']):
            export_data["documents"].append({
                "id": doc_id,
                "text": results['documents'][i],
                "embedding": results['embeddings'][i],
                "metadata": results['metadatas'][i]
            })
        
        # Sauvegarder
        output_file = "embeddings_export.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Embeddings exportés: {output_file}")
        print(f"📊 Statistiques:")
        print(f"   - Nombre de documents: {export_data['total_documents']}")
        print(f"   - Dimension des embeddings: {export_data['embedding_dimension']}")
        print(f"   - Taille du fichier: {Path(output_file).stat().st_size / 1024 / 1024:.2f} MB")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    export_embeddings()
