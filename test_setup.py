#!/usr/bin/env python3
"""
Script de test pour vérifier l'installation de TakeNote AI
"""

import sys
import subprocess
from pathlib import Path


def test_python_version():
    """Teste la version de Python."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} détecté. Python 3.8+ requis.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def test_ffmpeg():
    """Teste l'installation de FFmpeg."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # Extraire la version
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg: {version_line}")
            return True
        else:
            print("❌ FFmpeg installé mais ne fonctionne pas correctement")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg n'est pas installé")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout lors du test FFmpeg")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du test FFmpeg: {e}")
        return False


def test_python_packages():
    """Teste l'installation des packages Python."""
    packages = {
        'whisper': 'openai-whisper',
        'ffmpeg': 'ffmpeg-python'
    }
    
    all_good = True
    for package, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package} installé")
        except ImportError:
            print(f"❌ {package} non installé")
            all_good = False
    
    return all_good


def test_scripts():
    """Teste la présence des scripts."""
    scripts = [
        'takenote.py',
        'audio_converter.py', 
        'audio_cleaner.py',
        'audio_transcriber.py'
    ]
    
    all_good = True
    for script in scripts:
        if Path(script).exists():
            print(f"✅ {script} présent")
        else:
            print(f"❌ {script} manquant")
            all_good = False
    
    return all_good


def test_whisper_model():
    """Teste le chargement d'un modèle Whisper."""
    try:
        import whisper
        print("🔄 Test de chargement du modèle Whisper 'tiny'...")
        model = whisper.load_model("tiny")
        print("✅ Modèle Whisper chargé avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du chargement du modèle Whisper: {e}")
        return False


def main():
    """Fonction principale de test."""
    print("🧪 Test de l'installation TakeNote AI")
    print("=" * 40)
    
    tests = [
        ("Version Python", test_python_version),
        ("FFmpeg", test_ffmpeg),
        ("Packages Python", test_python_packages),
        ("Scripts", test_scripts),
        ("Modèle Whisper", test_whisper_model)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Test: {test_name}")
        print("-" * 20)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 40)
    print("📊 Résumé des tests:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 Tous les tests sont passés! TakeNote AI est prêt à utiliser.")
        print("\n📖 Pour commencer:")
        print("   python takenote.py votre_fichier.mp3")
    else:
        print("⚠️  Certains tests ont échoué. Consultez le README.md pour l'installation.")
        sys.exit(1)


if __name__ == "__main__":
    main()

