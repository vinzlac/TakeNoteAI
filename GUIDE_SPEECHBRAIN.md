# 🎤 Guide d'utilisation correcte de SpeechBrain

## ✅ **Solution au problème `'ModuleDict' object has no attribute 'decoder'`**

### **🔍 Problème identifié**

L'erreur venait de l'utilisation d'un modèle SpeechBrain obsolète (`speechbrain/asr-wav2vec2-commonvoice-fr`) avec une API qui a changé.

### **🔧 Solution appliquée**

1. **Modèle SpeechBrain fonctionnel** : `speechbrain/asr-crdnn-commonvoice-fr`
2. **API correcte** : `transcribe_file()` au lieu de `transcribe_batch()`
3. **Gestion d'erreur robuste** : Fallback automatique vers Whisper

---

## 🚀 **Utilisation de SpeechBrain**

### **Méthode recommandée**

```python
from speechbrain.pretrained import EncoderDecoderASR

# Charger le modèle fonctionnel
asr_model = EncoderDecoderASR.from_hparams(
    source="speechbrain/asr-crdnn-commonvoice-fr",
    savedir="pretrained_models/asr-crdnn-commonvoice-fr"
)

# Transcription simple
text = asr_model.transcribe_file("audio.mp3")
print(text)
```

### **Modèles SpeechBrain testés**

| Modèle | Statut | Qualité | Langue |
|--------|--------|---------|--------|
| `speechbrain/asr-crdnn-commonvoice-fr` | ✅ Fonctionne | Bonne | Français |
| `speechbrain/asr-wav2vec2-commonvoice-fr` | ❌ Erreur decoder | - | Français |
| `speechbrain/asr-wav2vec2-commonvoice-en` | ❌ Non testé | - | Anglais |

---

## 🛠️ **Intégration dans TakeNoteAI**

### **Utilisation avec le script principal**

```bash
# SpeechBrain (recommandé maintenant)
python advanced_rag_transcription.py audio.mp3

# Whisper (alternative)
python advanced_rag_transcription.py audio.mp3 --transcription-model whisper

# Modèle SpeechBrain spécifique
python advanced_rag_transcription.py audio.mp3 --transcription-model "speechbrain/asr-crdnn-commonvoice-fr"
```

### **Gestion automatique des erreurs**

Le script gère automatiquement :
- ✅ **Chargement du modèle** SpeechBrain
- ✅ **Transcription** avec `transcribe_file()`
- ✅ **Fallback vers Whisper** en cas d'erreur
- ✅ **Messages informatifs** pour l'utilisateur

---

## 📊 **Comparaison des performances**

### **SpeechBrain vs Whisper**

| Critère | SpeechBrain | Whisper |
|---------|-------------|---------|
| **Vitesse** | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Précision français** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Taille modèle** | ⭐⭐⭐⭐ | ⭐⭐ |
| **Stabilité** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Facilité d'usage** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

### **Recommandation**

- **Pour la production** : Whisper (plus stable)
- **Pour l'expérimentation** : SpeechBrain (plus rapide)
- **Pour le français** : Les deux sont excellents

---

## 🔧 **Dépannage**

### **Erreurs courantes**

#### 1. `'ModuleDict' object has no attribute 'decoder'`
**Solution** : Utiliser `speechbrain/asr-crdnn-commonvoice-fr` au lieu de `asr-wav2vec2-commonvoice-fr`

#### 2. `transcribe_batch` ne fonctionne pas
**Solution** : Utiliser `transcribe_file()` à la place

#### 3. Modèle non trouvé
**Solution** : Vérifier la connexion internet et l'authentification Hugging Face

### **Authentification Hugging Face**

```bash
# Se connecter à Hugging Face
huggingface-cli login

# Tester la connexion
python -c "from huggingface_hub import whoami; print(whoami())"
```

---

## 💡 **Bonnes pratiques**

### **1. Choix du modèle**
```python
# Modèles SpeechBrain recommandés
FRENCH_MODELS = [
    "speechbrain/asr-crdnn-commonvoice-fr",  # ✅ Fonctionne
    "speechbrain/asr-wav2vec2-commonvoice-fr"  # ❌ Erreur decoder
]

ENGLISH_MODELS = [
    "speechbrain/asr-crdnn-commonvoice-en",
    "speechbrain/asr-wav2vec2-commonvoice-en"
]
```

### **2. Gestion d'erreur robuste**
```python
try:
    text = asr_model.transcribe_file(audio_path)
except Exception as e:
    print(f"Erreur SpeechBrain: {e}")
    # Fallback vers Whisper
    import whisper
    model = whisper.load_model("base")
    text = model.transcribe(audio_path)["text"]
```

### **3. Optimisation des performances**
```python
# Charger le modèle une seule fois
asr_model = EncoderDecoderASR.from_hparams(...)

# Réutiliser pour plusieurs fichiers
for audio_file in audio_files:
    text = asr_model.transcribe_file(audio_file)
```

---

## 🎯 **Résumé**

✅ **SpeechBrain fonctionne correctement** avec le modèle `asr-crdnn-commonvoice-fr`  
✅ **API moderne** : Utiliser `transcribe_file()` au lieu de `transcribe_batch()`  
✅ **Fallback automatique** vers Whisper en cas d'erreur  
✅ **Intégration complète** dans TakeNoteAI avec RAG  

**Le problème `'ModuleDict' object has no attribute 'decoder'` est maintenant résolu !** 🎉
