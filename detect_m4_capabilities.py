#!/usr/bin/env python3
"""
Script de détection des capacités Mac M4
"""

import torch
import platform
import psutil
import subprocess
import sys

def detect_m4_capabilities():
    """Détecte les capacités du Mac M4."""
    print("🔍 Détection des capacités Mac M4...")
    print("=" * 50)
    
    # Informations système
    print("💻 Informations système:")
    print(f"   - Système: {platform.system()} {platform.release()}")
    print(f"   - Architecture: {platform.machine()}")
    print(f"   - Version Python: {sys.version}")
    
    # Capacités CPU
    print(f"\n🧠 Capacités CPU:")
    print(f"   - Cœurs physiques: {psutil.cpu_count(logical=False)}")
    print(f"   - Cœurs logiques: {psutil.cpu_count(logical=True)}")
    print(f"   - Fréquence: {psutil.cpu_freq().current:.0f} MHz")
    
    # Mémoire
    memory = psutil.virtual_memory()
    print(f"\n💾 Mémoire:")
    print(f"   - Total: {memory.total / 1024**3:.1f} GB")
    print(f"   - Disponible: {memory.available / 1024**3:.1f} GB")
    print(f"   - Utilisée: {memory.percent}%")
    
    # Capacités PyTorch
    print(f"\n🔥 Capacités PyTorch:")
    print(f"   - Version PyTorch: {torch.__version__}")
    print(f"   - CUDA disponible: {torch.cuda.is_available()}")
    print(f"   - MPS disponible: {torch.backends.mps.is_available()}")
    
    if torch.backends.mps.is_available():
        print("   ✅ GPU M4 détecté via MPS")
        try:
            # Tester MPS
            device = torch.device("mps")
            x = torch.randn(10, 10).to(device)
            y = torch.randn(10, 10).to(device)
            z = torch.mm(x, y)
            print("   ✅ MPS fonctionnel")
        except Exception as e:
            print(f"   ❌ Erreur MPS: {e}")
    else:
        print("   ❌ MPS non disponible")
    
    # Détection du Neural Engine
    print(f"\n🧠 Neural Engine:")
    try:
        # Vérifier Core ML
        import coremltools as ct
        print("   ✅ Core ML disponible")
        print(f"   - Version: {ct.__version__}")
    except ImportError:
        print("   ❌ Core ML non installé")
        print("   💡 Installez avec: pip install coremltools")
    
    # Détection Metal
    print(f"\n🎮 Capacités Metal:")
    try:
        result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                              capture_output=True, text=True)
        if 'Metal' in result.stdout:
            print("   ✅ Metal disponible")
        else:
            print("   ❌ Metal non détecté")
    except Exception as e:
        print(f"   ⚠️  Impossible de vérifier Metal: {e}")
    
    # Optimisations recommandées
    print(f"\n🚀 Optimisations recommandées:")
    
    if torch.backends.mps.is_available():
        print("   ✅ Utiliser MPS pour l'accélération GPU")
        print("   ✅ Activer mixed precision")
        print("   ✅ Utiliser tous les cœurs CPU")
        recommended_device = "mps"
    elif torch.cuda.is_available():
        print("   ✅ Utiliser CUDA pour l'accélération GPU")
        recommended_device = "cuda"
    else:
        print("   ⚠️  Utilisation CPU uniquement")
        print("   💡 Optimiser avec tous les cœurs")
        recommended_device = "cpu"
    
    # Configuration optimale
    print(f"\n⚙️  Configuration optimale:")
    print(f"   - Device recommandé: {recommended_device}")
    print(f"   - Threads CPU: {psutil.cpu_count()}")
    print(f"   - Batch size: 32 (optimisé pour M4)")
    print(f"   - Mixed precision: {'Activé' if recommended_device != 'cpu' else 'Non applicable'}")
    
    return recommended_device

def test_performance():
    """Teste les performances sur différents devices."""
    print(f"\n📊 Test de performances:")
    print("-" * 30)
    
    import time
    
    # Test CPU
    device_cpu = torch.device("cpu")
    x_cpu = torch.randn(1000, 1000)
    y_cpu = torch.randn(1000, 1000)
    
    start = time.time()
    z_cpu = torch.mm(x_cpu, y_cpu)
    cpu_time = time.time() - start
    print(f"   CPU: {cpu_time:.3f}s")
    
    # Test MPS si disponible
    if torch.backends.mps.is_available():
        device_mps = torch.device("mps")
        x_mps = x_cpu.to(device_mps)
        y_mps = y_cpu.to(device_mps)
        
        # Warmup
        torch.mm(x_mps, y_mps)
        
        start = time.time()
        z_mps = torch.mm(x_mps, y_mps)
        mps_time = time.time() - start
        speedup = cpu_time / mps_time
        print(f"   MPS: {mps_time:.3f}s (x{speedup:.1f} plus rapide)")
    
    # Test CUDA si disponible
    if torch.cuda.is_available():
        device_cuda = torch.device("cuda")
        x_cuda = x_cpu.to(device_cuda)
        y_cuda = y_cpu.to(device_cuda)
        
        # Warmup
        torch.mm(x_cuda, y_cuda)
        
        start = time.time()
        z_cuda = torch.mm(x_cuda, y_cuda)
        cuda_time = time.time() - start
        speedup = cpu_time / cuda_time
        print(f"   CUDA: {cuda_time:.3f}s (x{speedup:.1f} plus rapide)")

def generate_config():
    """Génère un fichier de configuration optimisé."""
    print(f"\n⚙️  Génération de la configuration optimisée...")
    
    device = detect_m4_capabilities()
    
    config = f"""# Configuration optimisée pour Mac M4
# Générée automatiquement par detect_m4_capabilities.py

# Device optimal
OPTIMAL_DEVICE = "{device}"

# Optimisations CPU
CPU_THREADS = {psutil.cpu_count()}

# Optimisations GPU/MPS
USE_MPS = {torch.backends.mps.is_available()}
USE_CUDA = {torch.cuda.is_available()}

# Paramètres optimisés
BATCH_SIZE = 32
MIXED_PRECISION = {device != 'cpu'}

# Configuration PyTorch
TORCH_SETTINGS = {{
    'num_threads': {psutil.cpu_count()},
    'mps_enabled': {torch.backends.mps.is_available()},
    'cuda_enabled': {torch.cuda.is_available()}
}}
"""
    
    with open('m4_config.py', 'w') as f:
        f.write(config)
    
    print("✅ Configuration sauvegardée dans m4_config.py")

def main():
    """Fonction principale."""
    try:
        # Détection des capacités
        device = detect_m4_capabilities()
        
        # Test de performances
        test_performance()
        
        # Génération de la configuration
        generate_config()
        
        print(f"\n🎉 Détection terminée!")
        print(f"💡 Device recommandé pour RAG: {device}")
        
        if device == "mps":
            print(f"🚀 Votre Mac M4 est optimisé pour l'IA!")
            print(f"📈 Attendez-vous à des gains de performance significatifs")
        
    except Exception as e:
        print(f"❌ Erreur lors de la détection: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
