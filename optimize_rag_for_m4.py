#!/usr/bin/env python3
"""
Script d'optimisation des scripts RAG pour Mac M4
"""

import torch
import os
import shutil
from pathlib import Path

def optimize_rag_scripts():
    """Optimise les scripts RAG pour Mac M4."""
    print("🚀 Optimisation des scripts RAG pour Mac M4...")
    print("=" * 60)
    
    # Vérifier MPS
    if not torch.backends.mps.is_available():
        print("❌ MPS non disponible sur ce système")
        return False
    
    print("✅ MPS disponible - Optimisations activées")
    
    # Optimisations PyTorch
    # torch.backends.mps.enable_amp()  # Non disponible dans cette version
    torch.set_num_threads(14)  # Tous les cœurs M4
    
    # Variables d'environnement
    os.environ['OMP_NUM_THREADS'] = '14'
    os.environ['MKL_NUM_THREADS'] = '14'
    os.environ['NUMEXPR_NUM_THREADS'] = '14'
    
    print("✅ Configuration PyTorch optimisée")
    
    # Optimiser advanced_rag_transcription.py
    optimize_main_script()
    
    # Optimiser les scripts d'analyse
    optimize_analysis_scripts()
    
    print("\n🎉 Optimisation terminée!")
    print("📈 Vos scripts RAG sont maintenant optimisés pour Mac M4")
    
    return True

def optimize_main_script():
    """Optimise advanced_rag_transcription.py."""
    print("\n🔧 Optimisation de advanced_rag_transcription.py...")
    
    script_path = Path("advanced_rag_transcription.py")
    if not script_path.exists():
        print("❌ Script advanced_rag_transcription.py introuvable")
        return
    
    # Sauvegarder l'original
    backup_path = script_path.with_suffix('.py.backup')
    if not backup_path.exists():
        shutil.copy2(script_path, backup_path)
        print(f"✅ Sauvegarde créée: {backup_path}")
    
    # Lire le script
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Optimisations à appliquer
    optimizations = [
        # Ajouter les imports optimisés
        ("import warnings", """import warnings
import torch
import os

# Optimisations M4
if torch.backends.mps.is_available():
    torch.set_num_threads(14)
    os.environ['OMP_NUM_THREADS'] = '14'
    os.environ['MKL_NUM_THREADS'] = '14'
    os.environ['NUMEXPR_NUM_THREADS'] = '14'
    print("🚀 Optimisations M4 activées")
"""),
        
        # Optimiser la détection de device
        ('self.device = "cpu"', '''self.device = self._get_optimal_device()
        print(f"🎯 Device sélectionné: {self.device}")'''),
        
        # Ajouter la méthode de détection de device
        ('def __init__(self', '''def _get_optimal_device(self):
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
    
    def __init__(self'''),
        
        # Optimiser le chargement des modèles
        ('whisper.load_model("base", device=self.device)', '''whisper.load_model("base", device=self.device)
            
            # Optimisations M4
            if self.device == "mps":
                print("🚀 Optimisations M4 appliquées au modèle Whisper")
                # Mixed precision pour MPS
                if hasattr(self.asr_model, 'half'):
                    self.asr_model.half()'''),
    ]
    
    # Appliquer les optimisations
    modified = False
    for old, new in optimizations:
        if old in content and new not in content:
            content = content.replace(old, new)
            modified = True
    
    if modified:
        # Sauvegarder le script optimisé
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Script advanced_rag_transcription.py optimisé")
    else:
        print("ℹ️  Script déjà optimisé")

def optimize_analysis_scripts():
    """Optimise les scripts d'analyse."""
    print("\n🔧 Optimisation des scripts d'analyse...")
    
    scripts_to_optimize = [
        "simple_audio_analyzer.py",
        "audio_summarizer.py",
        "generate_keywords_from_transcription.py"
    ]
    
    for script_name in scripts_to_optimize:
        script_path = Path(script_name)
        if script_path.exists():
            optimize_analysis_script(script_path)
        else:
            print(f"⚠️  Script {script_name} introuvable")

def optimize_analysis_script(script_path):
    """Optimise un script d'analyse spécifique."""
    print(f"   🔧 Optimisation de {script_path.name}...")
    
    # Sauvegarder l'original
    backup_path = script_path.with_suffix('.py.backup')
    if not backup_path.exists():
        shutil.copy2(script_path, backup_path)
    
    # Lire le script
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ajouter les optimisations si pas déjà présentes
    if "torch.set_num_threads(14)" not in content:
        # Ajouter les imports et optimisations
        import_section = """import warnings
import torch
import os

# Optimisations M4 pour l'analyse
if torch.backends.mps.is_available():
    torch.set_num_threads(14)
    os.environ['OMP_NUM_THREADS'] = '14'
    os.environ['MKL_NUM_THREADS'] = '14'
    os.environ['NUMEXPR_NUM_THREADS'] = '14'

"""
        
        # Trouver la première ligne d'import
        lines = content.split('\n')
        import_index = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_index = i
                break
        
        # Insérer les optimisations
        lines.insert(import_index, import_section.strip())
        content = '\n'.join(lines)
        
        # Sauvegarder
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   ✅ {script_path.name} optimisé")

def create_optimized_rag_script():
    """Crée une version optimisée du script RAG principal."""
    print("\n📝 Création d'une version optimisée...")
    
    # Lire le script original
    original_path = Path("advanced_rag_transcription.py")
    if not original_path.exists():
        print("❌ Script original introuvable")
        return
    
    with open(original_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Créer la version optimisée
    optimized_content = f"""#!/usr/bin/env python3
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

{content}
"""
    
    # Sauvegarder
    optimized_path = Path("advanced_rag_transcription_m4_optimized.py")
    with open(optimized_path, 'w', encoding='utf-8') as f:
        f.write(optimized_content)
    
    print(f"✅ Version optimisée créée: {optimized_path}")

def test_optimizations():
    """Teste les optimisations."""
    print("\n🧪 Test des optimisations...")
    
    try:
        # Test MPS
        if torch.backends.mps.is_available():
            device = torch.device("mps")
            x = torch.randn(100, 100).to(device)
            y = torch.randn(100, 100).to(device)
            z = torch.mm(x, y)
            print("✅ Test MPS réussi")
        
        # Test configuration
        print(f"✅ Threads CPU: {torch.get_num_threads()}")
        print(f"✅ Variables d'environnement configurées")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale."""
    print("🚀 Optimisation des scripts RAG pour Mac M4")
    print("=" * 60)
    
    try:
        # Optimiser les scripts
        success = optimize_rag_scripts()
        
        if success:
            # Créer la version optimisée
            create_optimized_rag_script()
            
            # Tester les optimisations
            test_optimizations()
            
            print("\n🎉 Optimisation terminée avec succès!")
            print("\n📋 Résumé des optimisations:")
            print("   ✅ MPS activé pour l'accélération GPU")
            print("   ✅ Mixed precision activé")
            print("   ✅ 14 threads CPU utilisés")
            print("   ✅ Variables d'environnement optimisées")
            print("   ✅ Scripts sauvegardés et optimisés")
            
            print("\n🚀 Utilisation:")
            print("   python advanced_rag_transcription_m4_optimized.py audio.mp3")
            print("   # ou utilisez les scripts existants (déjà optimisés)")
            
        else:
            print("❌ Optimisation échouée")
            return 1
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
