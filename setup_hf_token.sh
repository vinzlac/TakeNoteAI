#!/bin/bash
# Script pour configurer le token Hugging Face

echo "🔑 Configuration du token Hugging Face pour pyannote.audio"
echo "============================================================"
echo ""
echo "📋 Étapes à suivre :"
echo "1. Allez sur https://huggingface.co/settings/tokens"
echo "2. Créez un nouveau token (type: Read)"
echo "3. Copiez le token"
echo ""
echo "🔑 Collez votre token Hugging Face ici :"
read -s HF_TOKEN

if [ -z "$HF_TOKEN" ]; then
    echo "❌ Token vide, configuration annulée"
    exit 1
fi

# Configurer le token
export HUGGINGFACE_HUB_TOKEN="$HF_TOKEN"
echo "export HUGGINGFACE_HUB_TOKEN=\"$HF_TOKEN\"" >> ~/.bashrc
echo "export HUGGINGFACE_HUB_TOKEN=\"$HF_TOKEN\"" >> ~/.zshrc

echo "✅ Token configuré avec succès!"
echo "💡 Le token a été ajouté à votre profil shell"
echo "🔄 Redémarrez votre terminal ou exécutez: source ~/.bashrc"
echo ""
echo "🧪 Test du token..."
python -c "from huggingface_hub import whoami; print('✅ Token valide pour:', whoami()['name'])"
