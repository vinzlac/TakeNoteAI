#!/usr/bin/env python3
"""
Module commun pour la génération de comptes rendus de réunion par email.
Fonctions mutualisées utilisées par generate_meeting_report_email.py et rag_complete_workflow.py
"""

import os
import json
import subprocess
import tempfile
import re
from pathlib import Path
from typing import Optional


def extract_transcription_text(transcription_file: Path) -> Optional[str]:
    """Extrait le texte de transcription depuis un fichier JSON ou TXT."""
    try:
        if transcription_file.suffix.lower() == '.json':
            with open(transcription_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Essayer différentes structures JSON possibles
            if 'transcription' in data:
                if 'text' in data['transcription']:
                    return data['transcription']['text']
                elif 'full_text' in data['transcription']:
                    return data['transcription']['full_text']
            
            # Si directement dans la racine
            if 'text' in data:
                return data['text']
            
            print(f"⚠️  Structure JSON non reconnue dans {transcription_file}")
            return None
            
        else:
            # Fichier TXT simple
            with open(transcription_file, 'r', encoding='utf-8') as f:
                return f.read()
                
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier: {e}")
        return None


def generate_email_prompt(transcription_text: str, meeting_title: Optional[str] = None) -> str:
    """Génère le prompt pour cursor-agent."""
    
    prompt = f"""Tu es un assistant expert en rédaction de comptes rendus de réunion professionnels.

À partir de la transcription suivante d'une réunion, génère UNIQUEMENT le code HTML complet du compte rendu formaté pour un email professionnel.

**CRITIQUE - Format de sortie :**
- Génère UNIQUEMENT le code HTML brut, SANS balises markdown (pas de ```html, pas de ```)
- Commence DIRECTEMENT par <!DOCTYPE html> suivi de <html>
- Pas de texte avant le HTML, pas de commentaires, pas d'explications
- Le HTML doit être complet et prêt à être copié-collé dans un email

**Structure HTML exacte requise :**
1. <!DOCTYPE html><html><head><meta charset="UTF-8"></head><body>
2. Conteneur principal : <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px;">
3. Titre H1 : <h1 style="color: #2c3e50; font-size: 24px; margin-bottom: 20px; border-bottom: 3px solid #3498db; padding-bottom: 10px;">
4. Section Participants : <div style="background-color: #ecf0f1; padding: 15px; margin-bottom: 20px; border-left: 4px solid #3498db;">
5. Points principaux : <div style="background-color: #ffffff; padding: 15px; margin-bottom: 20px;">
   - Sous-sections H3 : <h3 style="color: #27ae60; font-size: 16px; margin-top: 15px; margin-bottom: 10px;">
   - Listes : <ul style="color: #34495e; line-height: 1.8; padding-left: 20px;">
6. Décisions prises : même style que points principaux
7. Actions à suivre : Tableau avec <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
   - En-tête : <tr style="background-color: #3498db; color: #ffffff;">
   - Lignes alternées : <tr style="background-color: #f8f9fa;"> pour les lignes paires
   - Bordures : style="padding: 10px; border: 1px solid #ecf0f1; color: #34495e;"
8. Points bloquants : <div style="background-color: #fff3cd; padding: 15px; margin-bottom: 20px; border-left: 4px solid #ffc107;">
9. Prochaines étapes : <div style="background-color: #d1ecf1; padding: 15px; margin-bottom: 20px; border-left: 4px solid #17a2b8;">

**Styles HTML précis à utiliser :**
- Body : style="margin: 0; padding: 0; font-family: Arial, Helvetica, sans-serif; background-color: #f4f4f4;"
- Conteneur principal : max-width: 600px, margin: 0 auto, background-color: #ffffff, padding: 20px
- Titre H1 : color: #2c3e50, font-size: 24px, border-bottom: 3px solid #3498db
- Titres H2 : color: #2c3e50, font-size: 18px, border-bottom: 2px solid #ecf0f1, padding-bottom: 8px
- Titres H3 : color: #27ae60, font-size: 16px
- Couleur texte principal : #34495e
- Sections colorées : #ecf0f1 (participants), #fff3cd (bloquants), #d1ecf1 (prochaines étapes)
- Tableau : alternance de couleurs #f8f9fa pour lignes paires

**Ton :** professionnel, clair et concis
**Langue :** français (ou la langue de la transcription)

Si certaines informations ne sont pas disponibles dans la transcription, laisse la section vide ou indique "Non disponible".

**Transcription de la réunion :**
"""
    
    if meeting_title:
        prompt += f"\n**Titre de la réunion :** {meeting_title}\n\n"
    
    prompt += f"\n{transcription_text}\n\n"
    prompt += "\n**Génère MAINTENANT le code HTML complet du compte rendu (commence DIRECTEMENT par <!DOCTYPE html>, SANS balises markdown) :**\n"
    
    return prompt


def clean_html_output(html_content: str) -> str:
    """Nettoie le HTML généré pour supprimer les balises markdown et le texte superflu."""
    # Supprimer les balises markdown au début (```html, ```)
    html_content = re.sub(r'^```html\s*', '', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^```\s*', '', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'```\s*$', '', html_content, flags=re.MULTILINE)
    
    # Trouver le début réel du HTML (<!DOCTYPE ou <html>)
    html_start_pattern = r'(<!DOCTYPE\s+html|<html)'
    match = re.search(html_start_pattern, html_content, re.IGNORECASE)
    if match:
        html_content = html_content[match.start():]
    
    # Trouver la fin du HTML (</html> ou </body>)
    html_end_pattern = r'(</html>|</body>)'
    match = re.search(html_end_pattern, html_content, re.IGNORECASE)
    if match:
        html_content = html_content[:match.end()]
    
    return html_content.strip()


def call_cursor_agent(prompt: str, cursor_agent_path: Optional[str] = None) -> Optional[str]:
    """Appelle cursor-agent avec le prompt fourni."""
    
    # Déterminer le chemin de cursor-agent
    if cursor_agent_path:
        cmd_base = cursor_agent_path
    else:
        cmd_base = 'cursor-agent'
    
    # Vérifier si cursor-agent est disponible
    try:
        result = subprocess.run(
            ['which', cmd_base] if not cursor_agent_path else ['test', '-f', cursor_agent_path],
            capture_output=True,
            text=True
        )
        if result.returncode != 0 and not cursor_agent_path:
            print("⚠️  cursor-agent non trouvé dans le PATH")
            print("💡 Utilisez --cursor-agent-path pour spécifier le chemin complet")
            return None
    except Exception as e:
        print(f"⚠️  Erreur lors de la vérification de cursor-agent: {e}")
    
    # Pour les prompts très longs, utiliser un fichier temporaire
    # Les limites de ligne de commande peuvent être dépassées
    use_temp_file = len(prompt) > 100000  # ~100KB
    temp_prompt_file = None
    
    try:
        if use_temp_file:
            # Créer un fichier temporaire avec le prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                temp_prompt_file = f.name
                f.write(prompt)
            
            # Utiliser le fichier (si cursor-agent supporte --input-file)
            # Sinon, on essaie quand même avec le prompt complet
            cmd = [cmd_base, '--print', prompt]
            print(f"📝 Prompt très long ({len(prompt):,} caractères), utilisation d'un fichier temporaire...")
        else:
            # Appeler cursor-agent avec --print pour mode non-interactif
            # Le prompt est passé comme argument
            cmd = [cmd_base, '--print', prompt]
        
        print("🤖 Appel de cursor-agent...")
        print("   (cela peut prendre quelques instants)")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout (génération peut être longue)
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if output:
                # Nettoyer le HTML : supprimer les balises markdown si présentes
                cleaned_output = clean_html_output(output)
                return cleaned_output
            else:
                print("⚠️  cursor-agent n'a retourné aucun résultat")
                print(f"   Stderr: {result.stderr}")
                return None
        else:
            print(f"❌ Erreur lors de l'appel à cursor-agent:")
            print(f"   Code: {result.returncode}")
            if result.stderr:
                print(f"   Stderr: {result.stderr}")
            if result.stdout:
                print(f"   Stdout: {result.stdout}")
            return None
                
    except subprocess.TimeoutExpired:
        print("❌ Timeout : cursor-agent a pris trop de temps (>10 minutes)")
        print("💡 Essayez avec un fichier de transcription plus court")
        return None
    except FileNotFoundError:
        print(f"❌ cursor-agent non trouvé: {cmd_base}")
        print("💡 Vérifiez l'installation ou utilisez --cursor-agent-path")
        return None
    except Exception as e:
        print(f"❌ Erreur lors de l'appel à cursor-agent: {e}")
        return None
    finally:
        # Nettoyer le fichier temporaire si utilisé
        if temp_prompt_file:
            try:
                os.unlink(temp_prompt_file)
            except:
                pass


def save_email_report(content: str, output_file: Path, meeting_title: Optional[str] = None) -> bool:
    """Sauvegarde le compte rendu dans un fichier."""
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Compte rendu sauvegardé : {output_file}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return False


def generate_meeting_report_email(transcription_file: Path, meeting_title: Optional[str] = None,
                                   output_file: Optional[Path] = None,
                                   cursor_agent_path: Optional[str] = None) -> Optional[Path]:
    """
    Génère un compte rendu de réunion formaté pour email.
    
    Args:
        transcription_file: Fichier de transcription (JSON ou TXT)
        meeting_title: Titre de la réunion (optionnel)
        output_file: Fichier de sortie (optionnel, généré automatiquement si non fourni)
        cursor_agent_path: Chemin vers cursor-agent (optionnel)
    
    Returns:
        Path du fichier généré ou None en cas d'erreur
    """
    if not transcription_file.exists():
        print(f"❌ Fichier introuvable: {transcription_file}")
        return None
    
    print(f"📄 Lecture de la transcription: {transcription_file.name}")
    
    # Extraire le texte
    transcription_text = extract_transcription_text(transcription_file)
    if not transcription_text:
        print("❌ Impossible d'extraire le texte de la transcription")
        return None
    
    print(f"✅ Texte extrait: {len(transcription_text):,} caractères")
    
    # Générer le prompt
    prompt = generate_email_prompt(transcription_text, meeting_title)
    
    # Appeler cursor-agent
    report_content = call_cursor_agent(prompt, cursor_agent_path)
    
    if not report_content:
        print("❌ Échec de la génération du compte rendu")
        return None
    
    # Déterminer le fichier de sortie si non fourni
    if not output_file:
        from datetime import datetime
        transcription_name = transcription_file.stem
        safe_name = transcription_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        output_dir = Path("output") / "meeting_reports" / safe_name
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"compte_rendu_{timestamp}.html"
    
    # Sauvegarder
    if save_email_report(report_content, output_file, meeting_title):
        return output_file
    else:
        return None

