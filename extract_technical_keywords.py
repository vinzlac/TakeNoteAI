#!/usr/bin/env python3
"""
Script spécialisé pour extraire les mots-clés techniques et noms propres
des transcriptions audio
"""

import json
import re
import argparse
from pathlib import Path
from collections import Counter
from typing import List, Dict, Set

class TechnicalKeywordExtractor:
    """Extracteur spécialisé pour les mots-clés techniques."""
    
    def __init__(self):
        """Initialise l'extracteur."""
        print("🔧 Initialisation de l'extracteur de mots-clés techniques...")
        
        # Mots français courants à exclure
        self.common_french_words = {
            "le", "la", "les", "de", "du", "des", "un", "une", "et", "ou", "mais", "donc", "car",
            "je", "tu", "il", "elle", "nous", "vous", "ils", "elles", "ce", "cette", "ces",
            "qui", "que", "quoi", "où", "quand", "comment", "pourquoi", "est", "sont", "être",
            "avoir", "faire", "aller", "venir", "voir", "dire", "savoir", "pouvoir", "vouloir",
            "avec", "sans", "pour", "dans", "sur", "sous", "par", "vers", "entre", "chez",
            "très", "plus", "moins", "bien", "mal", "bon", "mauvais", "grand", "petit",
            "nouveau", "ancien", "premier", "dernier", "autre", "même", "tout", "tous",
            "son", "sa", "ses", "mon", "ma", "mes", "ton", "ta", "tes", "notre", "nos",
            "votre", "vos", "leur", "leurs", "celui", "celle", "ceux", "celles",
            "oui", "non", "ok", "pas", "que", "qui", "comme", "si", "alors", "donc",
            "peut", "être", "avoir", "faire", "aller", "venir", "voir", "dire", "savoir",
            "pouvoir", "vouloir", "devoir", "falloir", "valoir", "venir", "partir",
            "rester", "revenir", "devenir", "parvenir", "convenir", "intervenir",
            "maintenant", "toujours", "jamais", "souvent", "parfois", "rarement",
            "beaucoup", "peu", "assez", "trop", "plus", "moins", "autant", "tant",
            "ici", "là", "là-bas", "partout", "nulle", "part", "ailleurs", "dedans",
            "dehors", "dessus", "dessous", "devant", "derrière", "à", "côté", "près",
            "loin", "haut", "bas", "droite", "gauche", "milieu", "centre", "bord",
            "côté", "partie", "endroit", "lieu", "place", "position", "situation",
            "état", "condition", "manière", "façon", "moyen", "méthode", "technique",
            "système", "procédé", "processus", "opération", "action", "activité",
            "travail", "fonction", "rôle", "mission", "tâche", "objectif", "but",
            "résultat", "effet", "conséquence", "impact", "influence", "importance",
            "valeur", "prix", "coût", "budget", "finance", "argent", "monnaie",
            "temps", "moment", "instant", "période", "durée", "longueur", "largeur",
            "hauteur", "profondeur", "taille", "dimension", "mesure", "quantité",
            "nombre", "chiffre", "pourcentage", "ratio", "proportion", "partie",
            "fraction", "total", "somme", "moyenne", "maximum", "minimum", "limite"
        }
        
        # Patterns techniques connus
        self.technical_patterns = [
            r'\b[A-Z]{2,6}\b',  # Acronymes (JIT, GIT, API, etc.)
            r'\b[A-Z][a-z]+[A-Z][a-z]*\b',  # CamelCase
            r'\bv\d+\b',  # Versions (v1, v2, etc.)
            r'\b[a-z]+\d+[a-z]*\b',  # Mots avec chiffres
            r'\b\w+-\w+\b',  # Mots avec tirets
            r'\b\w+_\w+\b',  # Mots avec underscores
            r'\b[A-Z][a-z]{2,}\b',  # Noms propres (commençant par majuscule)
            r'\b\w*[A-Z]\w*\b',  # Mots avec majuscules
        ]
        
        # Mots techniques spécifiques à rechercher
        self.technical_indicators = [
            "architecture", "développement", "code", "application", "système",
            "infrastructure", "cloud", "azure", "aws", "docker", "kubernetes",
            "api", "database", "server", "client", "frontend", "backend",
            "framework", "library", "tool", "platform", "service", "microservice",
            "deployment", "integration", "testing", "monitoring", "logging",
            "security", "performance", "scalability", "availability", "reliability"
        ]
        
        print("✅ Extracteur initialisé")
    
    def extract_technical_keywords(self, text: str) -> List[Dict]:
        """
        Extrait les mots-clés techniques du texte.
        
        Args:
            text (str): Texte à analyser
            
        Returns:
            List[Dict]: Liste des mots-clés techniques avec métadonnées
        """
        print("🔍 Extraction des mots-clés techniques...")
        
        # Nettoyer le texte
        cleaned_text = self._clean_text(text)
        
        # Extraire les mots-clés techniques
        technical_keywords = []
        
        # 1. Rechercher les acronymes et mots techniques
        for pattern in self.technical_patterns:
            matches = re.findall(pattern, cleaned_text)
            for match in matches:
                if self._is_valid_technical_keyword(match):
                    technical_keywords.append({
                        "word": match,
                        "type": self._categorize_keyword(match),
                        "pattern": pattern,
                        "count": cleaned_text.count(match),
                        "examples": self._find_examples(match, cleaned_text)
                    })
        
        # 2. Rechercher les noms propres potentiels
        proper_nouns = self._extract_proper_nouns(cleaned_text)
        for noun in proper_nouns:
            if self._is_valid_technical_keyword(noun):
                technical_keywords.append({
                    "word": noun,
                    "type": "Nom propre",
                    "pattern": "proper_noun",
                    "count": cleaned_text.count(noun),
                    "examples": self._find_examples(noun, cleaned_text)
                })
        
        # 3. Dédupliquer et trier
        unique_keywords = self._deduplicate_keywords(technical_keywords)
        unique_keywords.sort(key=lambda x: x["count"], reverse=True)
        
        print(f"✅ {len(unique_keywords)} mots-clés techniques trouvés")
        return unique_keywords
    
    def _clean_text(self, text: str) -> str:
        """Nettoie le texte pour l'analyse."""
        # Garder la casse originale pour détecter les majuscules
        # Supprimer seulement la ponctuation excessive
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _is_valid_technical_keyword(self, word: str) -> bool:
        """Vérifie si un mot est un mot-clé technique valide."""
        word_lower = word.lower()
        
        # Exclure les mots français courants
        if word_lower in self.common_french_words:
            return False
        
        # Exclure les mots trop courts (sauf acronymes)
        if len(word) < 2:
            return False
        
        # Exclure les mots trop longs (probablement des phrases)
        if len(word) > 20:
            return False
        
        # Acronymes : 2-6 caractères en majuscules
        if re.match(r'^[A-Z]{2,6}$', word):
            return True
        
        # CamelCase
        if re.search(r'[A-Z][a-z]+[A-Z]', word):
            return True
        
        # Versions (v1, v2, etc.)
        if re.match(r'^v\d+$', word.lower()):
            return True
        
        # Mots avec chiffres
        if re.search(r'\d', word):
            return True
        
        # Noms propres (commençant par majuscule, 3+ caractères)
        if word[0].isupper() and len(word) >= 3:
            return True
        
        # Mots avec tirets ou underscores
        if '-' in word or '_' in word:
            return True
        
        return False
    
    def _categorize_keyword(self, word: str) -> str:
        """Catégorise un mot-clé technique."""
        if re.match(r'^[A-Z]{2,6}$', word):
            return "Acronyme"
        elif re.search(r'[A-Z][a-z]+[A-Z]', word):
            return "CamelCase"
        elif re.match(r'^v\d+$', word.lower()):
            return "Version"
        elif re.search(r'\d', word):
            return "Avec chiffres"
        elif '-' in word or '_' in word:
            return "Composé"
        elif word[0].isupper():
            return "Nom propre"
        else:
            return "Technique"
    
    def _extract_proper_nouns(self, text: str) -> List[str]:
        """Extrait les noms propres du texte."""
        # Rechercher les mots commençant par majuscule
        proper_nouns = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
        
        # Filtrer les noms propres valides
        valid_nouns = []
        for noun in proper_nouns:
            if noun not in {"Le", "La", "Les", "De", "Du", "Des", "Un", "Une", "Et", "Ou", "Mais", "Donc", "Car"}:
                valid_nouns.append(noun)
        
        return list(set(valid_nouns))
    
    def _find_examples(self, word: str, text: str, max_examples: int = 3) -> List[str]:
        """Trouve des exemples d'utilisation du mot dans le texte."""
        examples = []
        sentences = text.split('.')
        
        for sentence in sentences:
            if word in sentence and len(examples) < max_examples:
                clean_sentence = sentence.strip()
                if len(clean_sentence) > 10:
                    examples.append(clean_sentence)
        
        return examples
    
    def _deduplicate_keywords(self, keywords: List[Dict]) -> List[Dict]:
        """Déduplique les mots-clés."""
        seen = set()
        unique_keywords = []
        
        for keyword in keywords:
            word_lower = keyword["word"].lower()
            if word_lower not in seen:
                seen.add(word_lower)
                unique_keywords.append(keyword)
        
        return unique_keywords
    
    def save_results(self, keywords: List[Dict], output_file: str):
        """Sauvegarde les résultats."""
        results = {
            "total_keywords": len(keywords),
            "keywords": keywords,
            "summary": {
                "acronyms": len([k for k in keywords if k["type"] == "Acronyme"]),
                "camel_case": len([k for k in keywords if k["type"] == "CamelCase"]),
                "versions": len([k for k in keywords if k["type"] == "Version"]),
                "with_numbers": len([k for k in keywords if k["type"] == "Avec chiffres"]),
                "composed": len([k for k in keywords if k["type"] == "Composé"]),
                "proper_nouns": len([k for k in keywords if k["type"] == "Nom propre"]),
                "technical": len([k for k in keywords if k["type"] == "Technique"])
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Résultats sauvegardés: {output_file}")
    
    def print_summary(self, keywords: List[Dict]):
        """Affiche un résumé des mots-clés trouvés."""
        print(f"\n📊 Résumé des mots-clés techniques trouvés:")
        print(f"   Total: {len(keywords)}")
        
        # Par catégorie
        categories = {}
        for keyword in keywords:
            category = keyword["type"]
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        print(f"\n📋 Par catégorie:")
        for category, count in sorted(categories.items()):
            print(f"   - {category}: {count}")
        
        # Top 15
        print(f"\n🏆 Top 15 des mots-clés techniques:")
        for i, keyword in enumerate(keywords[:15], 1):
            print(f"   {i:2d}. {keyword['word']} ({keyword['type']}) - "
                  f"Occurrences: {keyword['count']}")


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Extrait les mots-clés techniques d'une transcription",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s fichier.json                           # Analyser un fichier JSON
  %(prog)s fichier.json --output mots_cles.json   # Sortie personnalisée
  %(prog)s fichier.json --top 20                  # Top 20 seulement
        """
    )
    
    parser.add_argument("input", help="Fichier JSON de transcription à analyser")
    parser.add_argument("--output", "-o", help="Fichier de sortie (défaut: mots_cles_techniques.json)")
    parser.add_argument("--top", type=int, help="Afficher seulement les N premiers résultats")
    parser.add_argument("--save-examples", action="store_true", help="Sauvegarder les exemples d'utilisation")
    
    args = parser.parse_args()
    
    try:
        # Vérifier le fichier d'entrée
        input_file = Path(args.input)
        if not input_file.exists():
            print(f"❌ Fichier non trouvé: {input_file}")
            return 1
        
        # Déterminer le fichier de sortie
        if args.output:
            output_file = args.output
        else:
            output_file = f"mots_cles_techniques_{input_file.stem}.json"
        
        print(f"🔍 Analyse du fichier: {input_file}")
        print(f"📄 Sortie: {output_file}")
        
        # Charger le fichier JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extraire le texte
        if 'transcription' in data:
            if isinstance(data['transcription'], dict):
                text = data['transcription'].get('text', '')
            else:
                text = str(data['transcription'])
        else:
            print("❌ Aucune transcription trouvée dans le fichier")
            return 1
        
        if not text:
            print("❌ Texte de transcription vide")
            return 1
        
        print(f"📝 Texte analysé: {len(text)} caractères")
        
        # Initialiser l'extracteur
        extractor = TechnicalKeywordExtractor()
        
        # Extraire les mots-clés techniques
        technical_keywords = extractor.extract_technical_keywords(text)
        
        if not technical_keywords:
            print("✅ Aucun mot-clé technique détecté")
            return 0
        
        # Limiter les résultats si demandé
        if args.top:
            technical_keywords = technical_keywords[:args.top]
        
        # Supprimer les exemples si non demandés
        if not args.save_examples:
            for keyword in technical_keywords:
                keyword.pop('examples', None)
        
        # Afficher le résumé
        extractor.print_summary(technical_keywords)
        
        # Sauvegarder les résultats
        extractor.save_results(technical_keywords, output_file)
        
        # Afficher quelques exemples
        print(f"\n💡 Exemples de mots-clés techniques trouvés:")
        for keyword in technical_keywords[:10]:
            print(f"   - '{keyword['word']}' ({keyword['type']}) - "
                  f"Occurrences: {keyword['count']}")
            if args.save_examples and keyword.get('examples'):
                print(f"     Exemple: '{keyword['examples'][0][:60]}...'")
        
        print(f"\n🎯 Recommandations:")
        print(f"   1. Ajoutez les acronymes et noms propres à votre liste de mots-clés")
        print(f"   2. Utilisez: python advanced_rag_transcription_with_keywords.py --keywords \"mot1,mot2,mot3\"")
        print(f"   3. Les mots-clés techniques améliorent la précision de transcription")
        
        return 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
