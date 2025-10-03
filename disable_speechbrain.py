#!/usr/bin/env python3
"""
Script pour désactiver SpeechBrain et utiliser uniquement Whisper
"""

def disable_speechbrain():
    """Désactive SpeechBrain en modifiant le script principal."""
    print("🔧 Désactivation de SpeechBrain...")
    
    # Lire le fichier
    with open('advanced_rag_transcription.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Modifier SPEECHBRAIN_AVAILABLE pour le forcer à False
    old_line = 'SPEECHBRAIN_AVAILABLE = True'
    new_line = 'SPEECHBRAIN_AVAILABLE = False  # Désactivé manuellement'
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        
        # Écrire le fichier modifié
        with open('advanced_rag_transcription.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ SpeechBrain désactivé - utilisation exclusive de Whisper")
    else:
        print("⚠️  Ligne non trouvée, SpeechBrain peut déjà être désactivé")

def enable_speechbrain():
    """Réactive SpeechBrain."""
    print("🔧 Réactivation de SpeechBrain...")
    
    # Lire le fichier
    with open('advanced_rag_transcription.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remettre SPEECHBRAIN_AVAILABLE à True
    old_line = 'SPEECHBRAIN_AVAILABLE = False  # Désactivé manuellement'
    new_line = 'SPEECHBRAIN_AVAILABLE = True'
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        
        # Écrire le fichier modifié
        with open('advanced_rag_transcription.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ SpeechBrain réactivé")
    else:
        print("⚠️  SpeechBrain était déjà activé")

def main():
    """Fonction principale."""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "disable":
            disable_speechbrain()
        elif sys.argv[1] == "enable":
            enable_speechbrain()
        else:
            print("Usage: python disable_speechbrain.py [disable|enable]")
    else:
        print("🔧 Gestion de SpeechBrain")
        print("Usage:")
        print("  python disable_speechbrain.py disable  # Désactiver SpeechBrain")
        print("  python disable_speechbrain.py enable   # Réactiver SpeechBrain")

if __name__ == "__main__":
    main()
