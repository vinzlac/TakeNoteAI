#!/usr/bin/env python3
"""
Script pour expliquer les différences de taille entre les fichiers JSON RAG
"""

import json
from pathlib import Path

def explain_file_differences():
    """Explique pourquoi certains fichiers JSON sont plus volumineux."""
    print("📊 Explication des Différences de Taille des Fichiers JSON RAG")
    print("=" * 70)
    
    # Analyser les fichiers JSON et leurs sources
    json_files = [
        'test_output_advanced_rag_keywords_111_20251003_221142.json',
        'test_output_1_advanced_rag_20251003_214507.json',
        'test_output_1_advanced_rag_20251003_183500.json'
    ]
    
    print("🔍 ANALYSE COMPARATIVE:")
    print("-" * 50)
    
    for json_file in json_files:
        file_path = Path(json_file)
        if not file_path.exists():
            continue
            
        print(f"\n📄 {json_file}:")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Fichier audio source
        source_audio = data.get('metadata', {}).get('filename', 'N/A')
        print(f"   🎵 Fichier audio source: {source_audio}")
        
        # Taille du fichier audio
        if source_audio != 'N/A':
            audio_path = Path(source_audio)
            if audio_path.exists():
                audio_size_mb = audio_path.stat().st_size / 1024 / 1024
                estimated_minutes = audio_size_mb  # Approximation
                print(f"   📏 Taille audio: {audio_size_mb:.2f} MB (~{estimated_minutes:.1f} min)")
        
        # Métriques de transcription
        if 'transcription' in data and 'segments' in data['transcription']:
            segments = data['transcription']['segments']
            total_text = sum(len(segment.get('text', '')) for segment in segments)
            
            print(f"   📝 Segments: {len(segments)}")
            print(f"   📏 Texte total: {total_text:,} caractères")
            print(f"   📊 Moyenne/segment: {total_text/len(segments):.1f} caractères")
        
        # Mots-clés
        keywords_count = len(data.get('custom_keywords_applied', []))
        print(f"   🔤 Mots-clés: {keywords_count}")
    
    print("\n" + "=" * 70)
    print("🎯 EXPLICATION DES DIFFÉRENCES:")
    print("=" * 70)
    
    print("\n📊 COMPARAISON:")
    print("   Fichier volumineux (30k chars):")
    print("   - Source: test_output.mp3 (11.92 MB)")
    print("   - Durée estimée: ~12 minutes")
    print("   - Segments: 727")
    print("   - Mots-clés: 111")
    
    print("\n   Fichiers plus petits (1.7k chars):")
    print("   - Source: test_output_1.mp3 (0.74 MB)")
    print("   - Durée estimée: ~0.7 minute")
    print("   - Segments: 49")
    print("   - Mots-clés: 0")
    
    print("\n🔍 RAISONS PRINCIPALES:")
    print("   1. 📏 TAILLE DU FICHIER AUDIO:")
    print("      - test_output.mp3: 11.92 MB (16x plus gros)")
    print("      - test_output_1.mp3: 0.74 MB")
    print("      → Plus d'audio = plus de contenu à transcrire")
    
    print("\n   2. ⏱️  DURÉE DE L'AUDIO:")
    print("      - test_output.mp3: ~12 minutes")
    print("      - test_output_1.mp3: ~0.7 minute")
    print("      → Plus de temps = plus de segments")
    
    print("\n   3. 🔤 MOTS-CLÉS APPLIQUÉS:")
    print("      - Fichier volumineux: 111 mots-clés")
    print("      - Fichiers petits: 0 mots-clés")
    print("      → Mots-clés améliorent la transcription")
    
    print("\n   4. 📝 QUALITÉ DE TRANSCRIPTION:")
    print("      - Avec mots-clés: transcription plus précise")
    print("      - Sans mots-clés: transcription basique")
    print("      → Meilleure transcription = plus de contenu utile")
    
    print("\n💡 CONCLUSION:")
    print("   Le fichier test_output_advanced_rag_keywords_111_20251003_221142.json")
    print("   est plus volumineux car:")
    print("   ✅ Il traite un fichier audio 16x plus gros")
    print("   ✅ Il contient 12 minutes d'audio vs 0.7 minute")
    print("   ✅ Il utilise 111 mots-clés pour améliorer la transcription")
    print("   ✅ Il génère 727 segments détaillés vs 49 segments basiques")
    
    print("\n🚀 RECOMMANDATION:")
    print("   C'est NORMAL et ATTENDU que les fichiers soient de tailles différentes")
    print("   selon la durée et la complexité de l'audio source.")

if __name__ == "__main__":
    explain_file_differences()
