#!/usr/bin/env python3
"""
Script pour extraire les mots-clés inconnus/techniques d'une transcription
Identifie les termes qui pourraient nécessiter d'être ajoutés aux mots-clés personnalisés
"""

import json
import re
import argparse
from pathlib import Path
from collections import Counter
from typing import List, Dict, Set
import spacy

class UnknownKeywordExtractor:
    """Extracteur de mots-clés inconnus/techniques."""
    
    def __init__(self):
        """Initialise l'extracteur."""
        print("🔧 Initialisation de l'extracteur de mots-clés...")
        
        # Charger le modèle spaCy français si disponible
        try:
            self.nlp = spacy.load("fr_core_news_sm")
            print("✅ Modèle spaCy français chargé")
        except OSError:
            print("⚠️  Modèle spaCy non trouvé, utilisation de filtres basiques")
            self.nlp = None
        
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
            "votre", "vos", "leur", "leurs", "celui", "celle", "ceux", "celles"
        }
        
        # Acronymes techniques connus
        self.known_acronyms = {
            "API", "URL", "HTTP", "HTTPS", "SQL", "XML", "JSON", "PDF", "CSV", "HTML",
            "CSS", "JS", "JSX", "TS", "TSX", "PHP", "ASP", "JSP", "REST", "SOAP",
            "OAuth", "JWT", "SSL", "TLS", "DNS", "IP", "TCP", "UDP", "FTP", "SFTP",
            "SSH", "VPN", "LDAP", "AD", "SAML", "OIDC", "GDPR", "RGPD", "GDPR",
            "GDPR", "ISO", "IEEE", "ANSI", "ASCII", "UTF", "Unicode", "ASCII",
            "CPU", "RAM", "ROM", "SSD", "HDD", "GPU", "USB", "HDMI", "VGA", "DVI",
            "CD", "DVD", "BD", "MP3", "MP4", "AVI", "MOV", "WMV", "FLV", "MKV",
            "JPEG", "JPG", "PNG", "GIF", "SVG", "BMP", "TIFF", "RAW", "PSD", "AI",
            "EPS", "PDF", "DOC", "DOCX", "XLS", "XLSX", "PPT", "PPTX", "TXT", "RTF"
        }
        
        # Mots techniques connus
        self.known_technical_terms = {
            "application", "système", "développement", "architecture", "code", "programme",
            "logiciel", "matériel", "réseau", "serveur", "client", "base", "données",
            "base de données", "interface", "utilisateur", "admin", "administrateur",
            "configuration", "paramètre", "variable", "fonction", "méthode", "classe",
            "objet", "héritage", "polymorphisme", "encapsulation", "abstraction",
            "algorithme", "structure", "données", "table", "champ", "enregistrement",
            "requête", "insertion", "mise à jour", "suppression", "sélection", "jointure",
            "index", "contrainte", "clé primaire", "clé étrangère", "trigger", "procédure",
            "stockée", "vue", "transaction", "commit", "rollback", "backup", "restore",
            "migration", "déploiement", "environnement", "production", "test", "développement",
            "staging", "intégration", "continue", "délivrance", "continue", "pipeline",
            "build", "release", "version", "branche", "merge", "pull", "request",
            "commit", "push", "clone", "fork", "repository", "repository", "git",
            "github", "gitlab", "bitbucket", "jenkins", "docker", "kubernetes",
            "microservice", "service", "orchestration", "container", "image",
            "registry", "deployment", "scaling", "load", "balancing", "monitoring",
            "logging", "metrics", "alerting", "dashboard", "grafana", "prometheus",
            "elk", "stack", "elasticsearch", "logstash", "kibana", "fluentd",
            "redis", "memcached", "rabbitmq", "kafka", "mongodb", "postgresql",
            "mysql", "oracle", "sqlite", "cassandra", "neo4j", "influxdb"
        }
        
        print("✅ Extracteur initialisé")
    
    def extract_unknown_keywords(self, text: str, min_length: int = 2, max_length: int = 20) -> List[Dict]:
        """
        Extrait les mots-clés potentiellement inconnus/techniques du texte.
        
        Args:
            text (str): Texte à analyser
            min_length (int): Longueur minimale des mots
            max_length (int): Longueur maximale des mots
            
        Returns:
            List[Dict]: Liste des mots-clés avec métadonnées
        """
        print("🔍 Extraction des mots-clés inconnus...")
        
        # Nettoyer le texte
        cleaned_text = self._clean_text(text)
        
        # Extraire les mots
        words = self._extract_words(cleaned_text, min_length, max_length)
        
        # Analyser chaque mot
        unknown_keywords = []
        
        for word, count in words.most_common():
            if self._is_potential_unknown_keyword(word):
                confidence = self._calculate_confidence(word, count, len(words))
                
                unknown_keywords.append({
                    "word": word,
                    "count": count,
                    "confidence": confidence,
                    "category": self._categorize_word(word),
                    "examples": self._find_examples(word, text)
                })
        
        # Trier par confiance décroissante
        unknown_keywords.sort(key=lambda x: x["confidence"], reverse=True)
        
        print(f"✅ {len(unknown_keywords)} mots-clés potentiels trouvés")
        return unknown_keywords
    
    def _clean_text(self, text: str) -> str:
        """Nettoie le texte pour l'analyse."""
        # Supprimer la ponctuation excessive
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_words(self, text: str, min_length: int, max_length: int) -> Counter:
        """Extrait et compte les mots du texte."""
        words = []
        
        # Diviser en mots
        tokens = text.split()
        
        for token in tokens:
            # Nettoyer le token
            word = token.strip().lower()
            
            # Filtrer par longueur
            if min_length <= len(word) <= max_length:
                # Vérifier que ce n'est pas un nombre pur
                if not word.isdigit():
                    words.append(word)
        
        return Counter(words)
    
    def _is_potential_unknown_keyword(self, word: str) -> bool:
        """Détermine si un mot est potentiellement un mot-clé inconnu."""
        # Exclure les mots français courants
        if word in self.common_french_words:
            return False
        
        # Exclure les acronymes connus
        if word.upper() in self.known_acronyms:
            return False
        
        # Exclure les termes techniques connus
        if word in self.known_technical_terms:
            return False
        
        # Critères pour les mots-clés potentiels
        
        # 1. Acronymes (tout en majuscules, 2-6 caractères)
        if re.match(r'^[A-Z]{2,6}$', word):
            return True
        
        # 2. Mots avec majuscules au milieu (CamelCase)
        if re.search(r'[A-Z][a-z]+[A-Z]', word):
            return True
        
        # 3. Mots avec chiffres
        if re.search(r'\d', word):
            return True
        
        # 4. Mots très courts (2-3 caractères) qui ne sont pas des mots courants
        if len(word) <= 3 and word not in {"oui", "non", "ok", "pas", "que", "qui", "le", "la", "de", "du", "un", "et"}:
            return True
        
        # 5. Mots avec tirets
        if '-' in word:
            return True
        
        # 6. Mots avec underscores
        if '_' in word:
            return True
        
        # 7. Noms propres potentiels (commençant par majuscule, 3+ caractères)
        if word[0].isupper() and len(word) >= 3:
            return True
        
        # 8. Mots techniques (finissant par des suffixes techniques)
        technical_suffixes = ['ing', 'tion', 'sion', 'ment', 'age', 'isme', 'iste', 'eur', 'euse']
        if any(word.endswith(suffix) for suffix in technical_suffixes):
            return True
        
        # 9. Mots composés avec majuscules (comme "go-live", "code-review")
        if '-' in word and any(c.isupper() for c in word):
            return True
        
        # 10. Mots avec des patterns techniques (comme "v1", "v2", "api", etc.)
        if re.match(r'^v\d+$', word.lower()) or re.match(r'^[a-z]+\d+$', word.lower()):
            return True
        
        return False
    
    def _calculate_confidence(self, word: str, count: int, total_words: int) -> float:
        """Calcule la confiance qu'un mot soit un mot-clé inconnu."""
        confidence = 0.0
        
        # Fréquence relative
        frequency = count / total_words
        if frequency > 0.001:  # Plus de 0.1% du texte
            confidence += 0.3
        
        # Type de mot
        if re.match(r'^[A-Z]{2,6}$', word):  # Acronyme
            confidence += 0.4
        elif re.search(r'[A-Z][a-z]+[A-Z]', word):  # CamelCase
            confidence += 0.3
        elif re.search(r'\d', word):  # Contient des chiffres
            confidence += 0.2
        elif len(word) <= 3:  # Court
            confidence += 0.1
        elif '-' in word or '_' in word:  # Avec tirets/underscores
            confidence += 0.2
        elif word[0].isupper():  # Commence par majuscule
            confidence += 0.1
        
        # Limiter à 1.0
        return min(confidence, 1.0)
    
    def _categorize_word(self, word: str) -> str:
        """Catégorise un mot-clé."""
        if re.match(r'^[A-Z]{2,6}$', word):
            return "Acronyme"
        elif re.search(r'[A-Z][a-z]+[A-Z]', word):
            return "CamelCase"
        elif re.search(r'\d', word):
            return "Avec chiffres"
        elif len(word) <= 3:
            return "Court"
        elif '-' in word or '_' in word:
            return "Composé"
        elif word[0].isupper():
            return "Nom propre"
        else:
            return "Technique"
    
    def _find_examples(self, word: str, text: str, max_examples: int = 3) -> List[str]:
        """Trouve des exemples d'utilisation du mot dans le texte."""
        examples = []
        sentences = text.split('.')
        
        for sentence in sentences:
            if word.lower() in sentence.lower() and len(examples) < max_examples:
                # Nettoyer la phrase
                clean_sentence = sentence.strip()
                if len(clean_sentence) > 10:  # Éviter les phrases trop courtes
                    examples.append(clean_sentence)
        
        return examples
    
    def save_results(self, unknown_keywords: List[Dict], output_file: str):
        """Sauvegarde les résultats dans un fichier."""
        results = {
            "total_keywords": len(unknown_keywords),
            "keywords": unknown_keywords,
            "summary": {
                "acronyms": len([k for k in unknown_keywords if k["category"] == "Acronyme"]),
                "camel_case": len([k for k in unknown_keywords if k["category"] == "CamelCase"]),
                "with_numbers": len([k for k in unknown_keywords if k["category"] == "Avec chiffres"]),
                "short": len([k for k in unknown_keywords if k["category"] == "Court"]),
                "composed": len([k for k in unknown_keywords if k["category"] == "Composé"]),
                "proper_nouns": len([k for k in unknown_keywords if k["category"] == "Nom propre"]),
                "technical": len([k for k in unknown_keywords if k["category"] == "Technique"])
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Résultats sauvegardés: {output_file}")
    
    def print_summary(self, unknown_keywords: List[Dict]):
        """Affiche un résumé des mots-clés trouvés."""
        print(f"\n📊 Résumé des mots-clés inconnus trouvés:")
        print(f"   Total: {len(unknown_keywords)}")
        
        # Par catégorie
        categories = {}
        for keyword in unknown_keywords:
            category = keyword["category"]
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        print(f"\n📋 Par catégorie:")
        for category, count in sorted(categories.items()):
            print(f"   - {category}: {count}")
        
        # Top 10
        print(f"\n🏆 Top 10 des mots-clés les plus probables:")
        for i, keyword in enumerate(unknown_keywords[:10], 1):
            print(f"   {i:2d}. {keyword['word']} ({keyword['category']}) - "
                  f"Confiance: {keyword['confidence']:.2f} - "
                  f"Occurrences: {keyword['count']}")


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Extrait les mots-clés inconnus/techniques d'une transcription",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s fichier.json                           # Analyser un fichier JSON
  %(prog)s fichier.json --min-length 3            # Mots de 3+ caractères
  %(prog)s fichier.json --output mots_cles.json   # Sortie personnalisée
  %(prog)s fichier.json --top 20                  # Top 20 seulement
        """
    )
    
    parser.add_argument("input", help="Fichier JSON de transcription à analyser")
    parser.add_argument("--output", "-o", help="Fichier de sortie (défaut: mots_cles_inconnus.json)")
    parser.add_argument("--min-length", type=int, default=2, help="Longueur minimale des mots (défaut: 2)")
    parser.add_argument("--max-length", type=int, default=20, help="Longueur maximale des mots (défaut: 20)")
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
            output_file = f"mots_cles_inconnus_{input_file.stem}.json"
        
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
        extractor = UnknownKeywordExtractor()
        
        # Extraire les mots-clés
        unknown_keywords = extractor.extract_unknown_keywords(
            text, 
            min_length=args.min_length,
            max_length=args.max_length
        )
        
        if not unknown_keywords:
            print("✅ Aucun mot-clé inconnu détecté")
            return 0
        
        # Limiter les résultats si demandé
        if args.top:
            unknown_keywords = unknown_keywords[:args.top]
        
        # Supprimer les exemples si non demandés
        if not args.save_examples:
            for keyword in unknown_keywords:
                keyword.pop('examples', None)
        
        # Afficher le résumé
        extractor.print_summary(unknown_keywords)
        
        # Sauvegarder les résultats
        extractor.save_results(unknown_keywords, output_file)
        
        # Afficher quelques exemples
        print(f"\n💡 Exemples de mots-clés trouvés:")
        for keyword in unknown_keywords[:5]:
            print(f"   - '{keyword['word']}' ({keyword['category']}) - "
                  f"Confiance: {keyword['confidence']:.2f}")
            if args.save_examples and keyword.get('examples'):
                print(f"     Exemple: '{keyword['examples'][0][:60]}...'")
        
        print(f"\n🎯 Recommandations:")
        print(f"   1. Vérifiez les mots-clés avec une confiance > 0.5")
        print(f"   2. Ajoutez les acronymes et noms propres à votre liste")
        print(f"   3. Utilisez: python advanced_rag_transcription_with_keywords.py --keywords \"mot1,mot2,mot3\"")
        
        return 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
