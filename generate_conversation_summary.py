#!/usr/bin/env python3
"""
Script pour générer un résumé conversationnel depuis un fichier de transcription texte
Résumé de ce qui a été dit, sans risques ni actions
Utilise un modèle Hugging Face multilingue pour le résumé
"""

import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import torch

# Import du gestionnaire de sortie
try:
    from output_manager import OutputManager
    OUTPUT_MANAGER = OutputManager()
except ImportError:
    print("⚠️  output_manager.py non trouvé, utilisation des chemins par défaut")
    OUTPUT_MANAGER = None

# Import des transformers pour le résumé
try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("⚠️  transformers non disponible, utilisation du mode basique (sans modèle)")
    TRANSFORMERS_AVAILABLE = False


def parse_transcript_file(transcript_file: Path) -> Dict:
    """
    Parse un fichier de transcription texte et extrait les informations.
    
    Args:
        transcript_file: Chemin vers le fichier de transcription .txt
    
    Returns:
        Dict avec 'text', 'segments', 'metadata'
    """
    with open(transcript_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraire les métadonnées du header
    metadata = {}
    lines = content.split('\n')
    
    # Parser le header (lignes commençant par #)
    text_lines = []
    in_header = True
    
    for line in lines:
        if line.startswith('#'):
            # Extraire la durée
            if 'Durée:' in line:
                duration_match = re.search(r'Durée:\s*(\d{2}):(\d{2}):(\d{2})', line)
                if duration_match:
                    hours, minutes, secs = map(int, duration_match.groups())
                    metadata['duration'] = hours * 3600 + minutes * 60 + secs
            # Extraire le nom du fichier
            if 'Transcription:' in line:
                filename_match = re.search(r'Transcription:\s*(.+)', line)
                if filename_match:
                    metadata['filename'] = filename_match.group(1).strip()
        elif line.startswith('='):
            in_header = False
            continue
        elif not in_header and line.strip():
            text_lines.append(line)
    
    # Extraire le texte complet (sans les timestamps)
    full_text = ""
    segments = []
    max_timestamp = 0
    
    for line in text_lines:
        # Format: [HH:MM:SS] [Personne:] Texte
        timestamp_match = re.match(r'\[(\d{2}):(\d{2}):(\d{2})\]\s*(?:(\w+):\s*)?(.+)', line)
        if timestamp_match:
            hours, minutes, secs = map(int, timestamp_match.groups()[:3])
            timestamp_seconds = hours * 3600 + minutes * 60 + secs
            speaker = timestamp_match.group(4) if timestamp_match.group(4) else None
            text = timestamp_match.group(5).strip()
            
            # Mettre à jour le timestamp maximum
            max_timestamp = max(max_timestamp, timestamp_seconds)
            
            full_text += text + " "
            segments.append({
                'start': timestamp_seconds,
                'end': timestamp_seconds + 5,  # Estimation
                'text': text,
                'speaker': speaker
            })
        else:
            # Ligne sans timestamp, ajouter au texte
            if line.strip():
                full_text += line.strip() + " "
    
    # Si la durée n'a pas été trouvée dans le header, la calculer depuis le dernier segment
    if metadata.get('duration', 0) == 0 and max_timestamp > 0:
        metadata['duration'] = max_timestamp
    
    return {
        'text': full_text.strip(),
        'segments': segments,
        'metadata': metadata
    }


def identify_main_topics(text: str, segments: List[Dict]) -> List[str]:
    """Identifie les sujets principaux de la conversation."""
    topics = []
    text_lower = text.lower()
    
    # Sujets identifiés par mots-clés
    topic_keywords = {
        "Architecture": ["architecture", "architecte", "archi", "design", "structure"],
        "Développement": ["développer", "développement", "code", "programmation", "java", "spring"],
        "Projet": ["projet", "mission", "client", "équipe"],
        "Technique": ["technique", "technologie", "système", "application"],
        "Sécurité": ["sécurité", "rgpd", "firewall", "token", "authentification"],
        "Infrastructure": ["kubernetes", "cloud", "serveur", "déploiement", "infrastructure"],
        "Management": ["équipe", "responsable", "gestion", "management"],
        "Formation": ["formation", "apprentissage", "compétences"]
    }
    
    for topic, keywords in topic_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            if topic not in topics:
                topics.append(topic)
    
    return topics[:8]  # Limiter à 8 sujets principaux


def extract_key_points(text: str, segments: List[Dict]) -> List[Dict]:
    """Extrait les points clés de la conversation."""
    key_points = []
    
    # Mots-clés indiquant des points importants
    important_keywords = [
        'important', 'essentiel', 'critique', 'clé', 'principal',
        'décision', 'choix', 'solution', 'problème', 'résultat',
        'objectif', 'but', 'stratégie', 'approche', 'méthode'
    ]
    
    text_lower = text.lower()
    
    for segment in segments:
        seg_text = segment.get('text', '').lower()
        if any(keyword in seg_text for keyword in important_keywords):
            # Vérifier que ce n'est pas juste un mot isolé
            if len(seg_text.split()) > 3:  # Au moins 4 mots
                key_points.append({
                    'text': segment.get('text', '').strip(),
                    'timestamp': segment.get('start', 0)
                })
    
    return key_points[:15]  # Limiter à 15 points clés


def load_summarization_model(model_name: str = "moussaKam/barthez-orangesum-abstract") -> Optional[object]:
    """
    Charge le modèle de résumé multilingue.
    
    Args:
        model_name: Nom du modèle Hugging Face à utiliser
    
    Returns:
        Pipeline de résumé ou None si non disponible
    """
    if not TRANSFORMERS_AVAILABLE:
        return None
    
    try:
        print(f"🔄 Chargement du modèle de résumé: {model_name}")
        
        # Déterminer le device
        if torch.backends.mps.is_available():
            device = "mps"
            print("🚀 Utilisation du GPU M4 (MPS)")
        elif torch.cuda.is_available():
            device = "cuda"
            print("🚀 Utilisation du GPU CUDA")
        else:
            device = "cpu"
            print("⚠️  Utilisation du CPU (peut être lent)")
        
        # Créer le pipeline de résumé
        summarizer = pipeline(
            "summarization",
            model=model_name,
            tokenizer=model_name,
            device=device if device != "mps" else -1,  # MPS peut avoir des problèmes avec pipeline
            framework="pt"
        )
        
        print(f"✅ Modèle de résumé chargé: {model_name}")
        return summarizer
        
    except Exception as e:
        print(f"⚠️  Erreur lors du chargement du modèle: {e}")
        print("🔄 Utilisation du mode basique (sans modèle)")
        return None


def generate_summary_with_model(text: str, summarizer: object, max_length: int = 250, min_length: int = 100) -> str:
    """
    Génère un résumé avec un modèle Hugging Face.
    
    Args:
        text: Texte à résumer
        summarizer: Pipeline de résumé
        max_length: Longueur maximale du résumé
        min_length: Longueur minimale du résumé
    
    Returns:
        Résumé généré
    """
    try:
        # Pour BARThez, pas besoin de préfixe spécifique
        # Le modèle est optimisé pour le résumé en français
        prefix = ""  # BARThez n'a pas besoin de préfixe
        
        # Limiter la longueur du texte d'entrée (BARThez peut gérer ~1024 tokens)
        max_input_length = 2000  # caractères approximatifs
        
        # Nettoyer le texte (enlever les répétitions, phrases trop courtes)
        sentences = text.split('.')
        cleaned_sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
        # Prendre plus de phrases pour BARThez (il gère mieux les longs textes)
        cleaned_text = '. '.join(cleaned_sentences[:50])  # Prendre les 50 premières phrases pertinentes
        
        if len(cleaned_text) > max_input_length:
            # Prendre le début et la fin pour garder le contexte
            text_to_summarize = cleaned_text[:max_input_length//2] + " ... " + cleaned_text[-max_input_length//2:]
        else:
            text_to_summarize = cleaned_text
        
        # Utiliser le texte directement (BARThez n'a pas besoin de préfixe)
        input_text = text_to_summarize
        
        # Générer le résumé avec BARThez
        result = summarizer(
            input_text,
            max_length=max_length,
            min_length=min_length,
            do_sample=True,
            temperature=0.6,
            top_p=0.95,
            num_beams=5,
            early_stopping=True,
            no_repeat_ngram_size=3
        )
        
        if isinstance(result, list) and len(result) > 0:
            summary = result[0].get('summary_text', '')
            return summary.strip()
        else:
            return ""
            
    except Exception as e:
        print(f"⚠️  Erreur lors de la génération du résumé: {e}")
        import traceback
        traceback.print_exc()
        return ""


def generate_narrative_summary(text: str, segments: List[Dict], main_topics: List[str], summarizer: Optional[object] = None) -> str:
    """
    Génère un résumé narratif de ce dont on a parlé dans la conversation.
    
    Args:
        text: Texte complet de la transcription
        segments: Liste des segments
        main_topics: Liste des sujets principaux
    
    Returns:
        Résumé narratif en texte
    """
    text_lower = text.lower()
    
    # Extraire des informations clés pour construire le résumé
    summary_parts = []
    
    # Identifier le contexte général
    if any(word in text_lower for word in ['entretien', 'interview', 'recrutement', 'mission', 'poste']):
        summary_parts.append("est un entretien")
        if 'mission' in text_lower or 'poste' in text_lower:
            summary_parts.append("portant sur une mission ou un poste")
    
    # Identifier les participants
    if 'client' in text_lower:
        summary_parts.append("impliquant un client")
    if 'équipe' in text_lower:
        summary_parts.append("et une équipe")
    
    # Identifier les sujets techniques principaux
    tech_topics = []
    if 'architecture' in text_lower or 'architecte' in text_lower:
        tech_topics.append("architecture")
    if 'développement' in text_lower or 'développer' in text_lower:
        tech_topics.append("développement")
    if 'java' in text_lower or 'spring' in text_lower:
        tech_topics.append("technologies Java/Spring")
    if 'kubernetes' in text_lower or 'k8s' in text_lower:
        tech_topics.append("Kubernetes")
    if 'cloud' in text_lower:
        tech_topics.append("cloud")
    
    if tech_topics:
        summary_parts.append(f"abordant les sujets de {', '.join(tech_topics[:3])}")
    
    # Identifier les aspects organisationnels
    if 'projet' in text_lower:
        summary_parts.append("et la gestion de projet")
    if 'sécurité' in text_lower or 'rgpd' in text_lower:
        summary_parts.append("avec des considérations de sécurité")
    
    # Si un modèle de résumé est disponible, l'utiliser
    if summarizer is not None:
        print("🤖 Génération du résumé avec le modèle multilingue...")
        
        # Préparer le texte pour le résumé (combiner les segments importants)
        text_for_summary = text
        
        # Si le texte est trop long, prendre les segments les plus importants
        if len(text_for_summary) > 2000:
            important_segments = []
            for segment in segments:
                seg_text = segment.get('text', '').lower()
                if any(keyword in seg_text for keyword in [
                    'mission', 'poste', 'rôle', 'responsabilité', 'équipe',
                    'projet', 'client', 'architecture', 'développement',
                    'technologie', 'compétence', 'expérience', 'important'
                ]):
                    if len(seg_text.split()) > 5:
                        important_segments.append(segment.get('text', '').strip())
            
            if important_segments:
                # Prendre les segments les plus représentatifs
                text_for_summary = " ".join(important_segments[:30])
        
        # Générer le résumé avec le modèle
        ai_summary = generate_summary_with_model(text_for_summary, summarizer, max_length=250, min_length=100)
        
        if ai_summary:
            narrative = f"{ai_summary}\n\n"
            narrative += "**Points principaux discutés :**\n\n"
            
            # Ajouter quelques segments clés pour compléter
            important_segments = []
            for segment in segments:
                seg_text = segment.get('text', '').lower()
                if any(keyword in seg_text for keyword in [
                    'mission', 'poste', 'rôle', 'responsabilité', 'équipe',
                    'projet', 'client', 'architecture', 'développement'
                ]):
                    if len(seg_text.split()) > 5:
                        important_segments.append(segment.get('text', '').strip())
            
            sample_segments = important_segments[:5]
            for seg in sample_segments:
                if len(seg) > 20:
                    narrative += f"- {seg[:200]}...\n"
            
            return narrative
    
    # Mode basique (sans modèle) - extraction par mots-clés
    narrative = ""
    
    if summary_parts:
        narrative += "Cette conversation " + ", ".join(summary_parts) + ". "
    else:
        narrative += "Cette conversation porte sur plusieurs sujets techniques et organisationnels. "
    
    # Ajouter des détails sur le contenu
    narrative += "\n\n"
    
    # Parcourir les segments pour extraire des informations plus précises
    important_segments = []
    for segment in segments:
        seg_text = segment.get('text', '').lower()
        # Chercher des segments avec des informations structurantes
        if any(keyword in seg_text for keyword in [
            'mission', 'poste', 'rôle', 'responsabilité', 'équipe',
            'projet', 'client', 'architecture', 'développement',
            'technologie', 'compétence', 'expérience'
        ]):
            if len(seg_text.split()) > 5:  # Au moins 6 mots
                important_segments.append(segment.get('text', '').strip())
    
    # Construire un résumé plus détaillé
    if important_segments:
        narrative += "**Points principaux discutés :**\n\n"
        # Prendre les segments les plus représentatifs
        sample_segments = important_segments[:8]
        for i, seg in enumerate(sample_segments, 1):
            if len(seg) > 20:  # Ignorer les segments trop courts
                narrative += f"- {seg[:200]}...\n"
    
    return narrative


def generate_conversation_summary(transcript_data: Dict, summarizer: Optional[object] = None) -> str:
    """
    Génère un résumé conversationnel à partir des données de transcription.
    
    Args:
        transcript_data: Dict avec 'text', 'segments', 'metadata'
    
    Returns:
        Contenu du résumé en Markdown
    """
    text = transcript_data['text']
    segments = transcript_data['segments']
    metadata = transcript_data['metadata']
    
    filename = metadata.get('filename', 'Transcription')
    duration = metadata.get('duration', 0)
    
    # Identifier les sujets principaux
    main_topics = identify_main_topics(text, segments)
    
    # Extraire les points clés
    key_points = extract_key_points(text, segments)
    
    # Générer le résumé narratif (le modèle est passé en paramètre depuis main)
    narrative_summary = generate_narrative_summary(text, segments, main_topics, summarizer)
    
    # Calculer la durée formatée
    hours = duration // 3600
    minutes = (duration % 3600) // 60
    seconds = duration % 60
    duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    # Générer le résumé
    summary = f"""# 📝 RÉSUMÉ DE LA CONVERSATION - {filename}

## 🎯 Informations générales
- **Durée** : {duration_str} ({duration} secondes)
- **Segments** : {len(segments)} segments transcrits
- **Date de génération** : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📖 De quoi on a parlé ?

{narrative_summary}

## 📋 Sujets principaux abordés

"""
    
    if main_topics:
        for i, topic in enumerate(main_topics, 1):
            summary += f"{i}. **{topic}**\n"
    else:
        summary += "Aucun sujet spécifique identifié.\n"
    
    summary += f"""

## 💬 Points clés de la conversation

"""
    
    if key_points:
        for i, point in enumerate(key_points, 1):
            timestamp_str = f"{int(point['timestamp'])//3600:02d}:{(int(point['timestamp'])%3600)//60:02d}:{int(point['timestamp'])%60:02d}"
            summary += f"{i}. (à {timestamp_str}) {point['text'][:200]}...\n\n"
    else:
        summary += "Aucun point clé spécifique identifié.\n\n"
    
    summary += f"""
## 📊 Résumé de la conversation

"""
    
    # Générer un résumé textuel basé sur les segments
    # Prendre des segments représentatifs à différents moments
    total_segments = len(segments)
    sample_indices = [
        0,  # Début
        total_segments // 4,  # Premier quart
        total_segments // 2,  # Milieu
        3 * total_segments // 4,  # Troisième quart
        total_segments - 1  # Fin
    ]
    
    summary += "### Début de la conversation\n\n"
    if segments:
        start_segments = segments[:min(5, len(segments))]
        for seg in start_segments:
            summary += f"- {seg.get('text', '').strip()[:150]}...\n"
    
    summary += "\n### Milieu de la conversation\n\n"
    if len(segments) > 10:
        mid_index = len(segments) // 2
        mid_segments = segments[max(0, mid_index-2):min(len(segments), mid_index+3)]
        for seg in mid_segments:
            summary += f"- {seg.get('text', '').strip()[:150]}...\n"
    
    summary += "\n### Fin de la conversation\n\n"
    if segments:
        end_segments = segments[-min(5, len(segments)):]
        for seg in end_segments:
            text = seg.get('text', '').strip()
            # Ignorer les segments vides ou avec seulement des points
            if text and len(text) > 3 and not text.replace('.', '').replace(' ', '').strip() == '':
                summary += f"- {text[:150]}...\n"
    
    # Calculer la longueur réelle du texte
    full_text_length = len(transcript_data['text'])
    
    summary += f"""

## 📈 Statistiques
- **Durée totale** : {duration_str}
- **Nombre de segments** : {len(segments)}
- **Sujets principaux** : {len(main_topics)}
- **Points clés identifiés** : {len(key_points)}
- **Longueur du texte** : {full_text_length:,} caractères

---
*Résumé généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*
"""
    
    return summary


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Génère un résumé conversationnel depuis un fichier de transcription texte",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s output/readable_transcripts/transcript.txt
  %(prog)s output/transcriptions/transcript.txt -o custom_summary.md
  %(prog)s output/transcriptions/transcript.txt --model moussaKam/barthez-orangesum-abstract
        """
    )
    
    parser.add_argument("transcript_file", help="Fichier de transcription texte (.txt)")
    parser.add_argument("-o", "--output", help="Fichier de sortie (optionnel, défaut: output/summaries/summary.md)")
    parser.add_argument("--model", default="moussaKam/barthez-orangesum-abstract", 
                       help="Modèle Hugging Face pour le résumé (défaut: moussaKam/barthez-orangesum-abstract)")
    parser.add_argument("--no-model", action="store_true", 
                       help="Désactiver l'utilisation du modèle (mode basique uniquement)")
    
    args = parser.parse_args()
    
    try:
        transcript_path = Path(args.transcript_file)
        
        if not transcript_path.exists():
            print(f"❌ Le fichier {transcript_path} n'existe pas")
            return 1
        
        print(f"📄 Lecture de la transcription: {transcript_path.name}")
        
        # Parser le fichier de transcription
        transcript_data = parse_transcript_file(transcript_path)
        
        print(f"✅ Transcription parsée: {len(transcript_data['segments'])} segments")
        
        # Charger le modèle si demandé
        summarizer = None
        if not args.no_model:
            summarizer = load_summarization_model(args.model)
        
        # Générer le résumé
        print("📝 Génération du résumé conversationnel...")
        summary = generate_conversation_summary(transcript_data, summarizer)
        
        # Déterminer le fichier de sortie
        if args.output:
            output_file = Path(args.output)
        else:
            # Générer dans output/summaries/summary.md
            summaries_dir = Path("output/summaries")
            summaries_dir.mkdir(parents=True, exist_ok=True)
            # Utiliser le nom du fichier source pour le résumé
            base_name = transcript_path.stem.replace('_transcript', '').replace('_advanced_rag', '')
            output_file = summaries_dir / f"{base_name}_summary.md"
        
        # Sauvegarder
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"✅ Résumé conversationnel généré: {output_file}")
        print(f"📊 Statistiques:")
        print(f"   - Sujets principaux: {len(identify_main_topics(transcript_data['text'], transcript_data['segments']))}")
        print(f"   - Points clés: {len(extract_key_points(transcript_data['text'], transcript_data['segments']))}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
