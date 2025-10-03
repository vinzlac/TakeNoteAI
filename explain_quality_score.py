#!/usr/bin/env python3
"""
Script pour expliquer le calcul du score de qualité RAG
"""

import json
from pathlib import Path

def explain_quality_calculation():
    """Explique le calcul du score de qualité."""
    print("📊 Explication du Score de Qualité RAG")
    print("=" * 50)
    
    json_files = list(Path('.').glob('*advanced_rag*.json'))
    
    print("🔍 Méthode de calcul:")
    print("   Le score de qualité est basé sur 2 métriques:")
    print("   1. Longueur du texte transcrit (caractères)")
    print("   2. Nombre de segments")
    print()
    
    print("📏 Seuils de qualité:")
    print("   - Score 0.9: >10,000 caractères ET >10 segments")
    print("   - Score 0.7: >5,000 caractères ET >5 segments") 
    print("   - Score 0.5: >1,000 caractères")
    print("   - Score 0.3: <1,000 caractères")
    print()
    
    print("📄 Analyse détaillée de vos fichiers:")
    print("-" * 50)
    
    quality_scores = []
    
    for i, file in enumerate(json_files, 1):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Calculer les métriques
            text_length = 0
            segment_count = 0
            
            if 'transcription' in data and 'segments' in data['transcription']:
                for segment in data['transcription']['segments']:
                    if 'text' in segment:
                        text_length += len(segment['text'])
                segment_count = len(data['transcription']['segments'])
            
            # Calculer le score
            if text_length > 10000 and segment_count > 10:
                score = 0.9
                reason = "Excellent: >10k chars ET >10 segments"
            elif text_length > 5000 and segment_count > 5:
                score = 0.7
                reason = "Bon: >5k chars ET >5 segments"
            elif text_length > 1000:
                score = 0.5
                reason = "Moyen: >1k chars"
            else:
                score = 0.3
                reason = "Faible: <1k chars"
            
            quality_scores.append(score)
            
            print(f"{i:2d}. {file.name}")
            print(f"     📝 Texte: {text_length:,} caractères")
            print(f"     📋 Segments: {segment_count}")
            print(f"     🎯 Score: {score} - {reason}")
            print()
            
        except Exception as e:
            print(f"{i:2d}. {file.name} - Erreur: {e}")
            quality_scores.append(0.1)
            print()
    
    # Score moyen
    avg_score = sum(quality_scores) / len(quality_scores)
    
    print("📊 RÉSUMÉ:")
    print(f"   - Nombre de fichiers: {len(json_files)}")
    print(f"   - Score moyen: {avg_score:.2f}/1.0")
    print(f"   - Seuil configuré: 0.8")
    print(f"   - Recommandation: {'NETTOYER' if avg_score < 0.8 else 'ACCUMULER'}")
    print()
    
    print("🎯 INTERPRÉTATION:")
    if avg_score >= 0.8:
        print("   ✅ Qualité excellente - Accumulation recommandée")
        print("   💡 Vos transcriptions sont riches et détaillées")
    elif avg_score >= 0.6:
        print("   ⚠️  Qualité moyenne - Accumulation possible")
        print("   💡 Certaines transcriptions sont de bonne qualité")
    else:
        print("   ❌ Qualité insuffisante - Nettoyage recommandé")
        print("   💡 Beaucoup de transcriptions sont incomplètes ou vides")
    
    print()
    print("🔧 ACTIONS RECOMMANDÉES:")
    if avg_score < 0.8:
        print("   1. Nettoyer les données existantes")
        print("   2. Relancer le RAG avec de meilleurs paramètres")
        print("   3. Vérifier la qualité audio")
        print("   4. Utiliser des mots-clés pertinents")
    else:
        print("   1. Continuer l'accumulation")
        print("   2. Monitorer la qualité")
        print("   3. Nettoyer périodiquement")

if __name__ == "__main__":
    explain_quality_calculation()
