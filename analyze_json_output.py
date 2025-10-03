#!/usr/bin/env python3
"""
Script pour analyser et générer des statistiques du JSON de sortie
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def analyze_json_output(json_file):
    """Analyse le JSON et génère des statistiques."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extraire les données
    transcription = data.get('transcription', {})
    keywords = data.get('business_keywords', [])
    metadata = data.get('metadata', {})
    
    # Statistiques du texte
    text = transcription.get('text', '')
    segments = transcription.get('segments', [])
    
    # Calculs
    word_count = len(text.split())
    char_count = len(text)
    segment_count = len(segments)
    duration = metadata.get('duration', 0)
    
    # Statistiques des mots-clés
    keyword_count = len(keywords)
    avg_keyword_score = sum(score for _, score in keywords) / len(keywords) if keywords else 0
    
    # Analyse des segments
    if segments:
        avg_segment_duration = sum(seg.get('end', 0) - seg.get('start', 0) for seg in segments) / len(segments)
        confidence_scores = [seg.get('avg_logprob', 0) for seg in segments if 'avg_logprob' in seg]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
    else:
        avg_segment_duration = 0
        avg_confidence = 0
    
    return {
        'text_stats': {
            'word_count': word_count,
            'char_count': char_count,
            'segment_count': segment_count,
            'duration': duration,
            'words_per_minute': (word_count / (duration / 60)) if duration > 0 else 0
        },
        'keyword_stats': {
            'count': keyword_count,
            'avg_score': avg_keyword_score,
            'top_keywords': keywords[:5]
        },
        'quality_stats': {
            'avg_segment_duration': avg_segment_duration,
            'avg_confidence': avg_confidence,
            'transcription_method': transcription.get('method', 'unknown'),
            'language': transcription.get('language', 'unknown')
        },
        'metadata': metadata
    }

def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_json_output.py <fichier.json>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    if not Path(json_file).exists():
        print(f"❌ Fichier {json_file} non trouvé")
        sys.exit(1)
    
    try:
        stats = analyze_json_output(json_file)
        
        print("📊 Analyse du fichier JSON")
        print("=" * 60)
        
        # Statistiques du texte
        text_stats = stats['text_stats']
        print(f"📝 Statistiques du texte:")
        print(f"   - Nombre de mots: {text_stats['word_count']:,}")
        print(f"   - Nombre de caractères: {text_stats['char_count']:,}")
        print(f"   - Nombre de segments: {text_stats['segment_count']}")
        print(f"   - Durée: {text_stats['duration']:.1f} secondes")
        print(f"   - Mots par minute: {text_stats['words_per_minute']:.1f}")
        
        # Statistiques des mots-clés
        keyword_stats = stats['keyword_stats']
        print(f"\n🔑 Statistiques des mots-clés:")
        print(f"   - Nombre de mots-clés: {keyword_stats['count']}")
        print(f"   - Score moyen: {keyword_stats['avg_score']:.3f}")
        print(f"   - Top 5 mots-clés:")
        for i, (keyword, score) in enumerate(keyword_stats['top_keywords'], 1):
            print(f"     {i}. {keyword} ({score:.3f})")
        
        # Statistiques de qualité
        quality_stats = stats['quality_stats']
        print(f"\n🎯 Statistiques de qualité:")
        print(f"   - Méthode de transcription: {quality_stats['transcription_method']}")
        print(f"   - Langue détectée: {quality_stats['language']}")
        print(f"   - Durée moyenne des segments: {quality_stats['avg_segment_duration']:.1f}s")
        print(f"   - Confiance moyenne: {quality_stats['avg_confidence']:.3f}")
        
        # Métadonnées
        metadata = stats['metadata']
        print(f"\n📋 Métadonnées:")
        print(f"   - Fichier source: {metadata.get('filename', 'N/A')}")
        print(f"   - Taille: {metadata.get('size_mb', 0):.2f} MB")
        print(f"   - Timestamp: {metadata.get('timestamp', 'N/A')}")
        # Recharger les données pour les métadonnées finales
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"   - Embeddings disponibles: {data.get('embeddings_available', False)}")
        print(f"   - Stocké en base vectorielle: {data.get('vector_db_stored', False)}")
        
        print("=" * 60)
        
        # Sauvegarder le rapport
        output_file = Path(json_file).stem + "_analyse.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Rapport d'analyse - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("STATISTIQUES DU TEXTE\n")
            f.write("-" * 30 + "\n")
            for key, value in text_stats.items():
                f.write(f"{key}: {value}\n")
            
            f.write(f"\nSTATISTIQUES DES MOTS-CLÉS\n")
            f.write("-" * 30 + "\n")
            for key, value in keyword_stats.items():
                if key != 'top_keywords':
                    f.write(f"{key}: {value}\n")
            
            f.write(f"\nSTATISTIQUES DE QUALITÉ\n")
            f.write("-" * 30 + "\n")
            for key, value in quality_stats.items():
                f.write(f"{key}: {value}\n")
        
        print(f"✅ Rapport sauvegardé: {output_file}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
