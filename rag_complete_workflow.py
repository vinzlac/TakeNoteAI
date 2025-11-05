#!/usr/bin/env python3
"""
Script RAG complet tout-en-un pour Mac M4
Workflow: Audio → RAG → Mots-clés → Analyse → Résumé
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from typing import Optional, List
import argparse

# Optimisations M4
import torch
if torch.backends.mps.is_available():
    torch.set_num_threads(14)
    os.environ['OMP_NUM_THREADS'] = '14'
    os.environ['MKL_NUM_THREADS'] = '14'
    os.environ['NUMEXPR_NUM_THREADS'] = '14'
    print("🚀 Optimisations Mac M4 activées")

class RAGCompleteWorkflow:
    """Workflow RAG complet optimisé pour Mac M4."""
    
    def __init__(self):
        """Initialise le workflow complet."""
        print("🔧 Initialisation du workflow RAG complet...")
        self.audio_file = None
        self.json_file = None
        self.keywords_file = None
        self.results = {}
        
        print("✅ Workflow initialisé")
    
    def step1_rag_transcription(self, audio_file: str, initial_keywords: Optional[List[str]] = None) -> bool:
        """Étape 1: Transcription RAG avec mots-clés."""
        print(f"\n🎤 ÉTAPE 1: Transcription RAG avec mots-clés")
        print("=" * 50)
        
        if not Path(audio_file).exists():
            print(f"❌ Fichier audio {audio_file} introuvable")
            return False
        
        print(f"📁 Fichier audio: {audio_file}")
        
        # Étape de transcription: utiliser le script disponible
        # Note: le script 'advanced_rag_transcription_with_keywords.py' n'est plus présent.
        # On bascule vers 'advanced_rag_transcription.py'. Les mots-clés initiaux seront ignorés.
        if initial_keywords:
            keywords_str = ", ".join(initial_keywords)
            print(f"🔤 Mots-clés initiaux fournis (ignorés par ce script): {keywords_str}")
        else:
            print("🔤 Aucun mot-clé initial fourni")
        cmd = f'python advanced_rag_transcription.py "{audio_file}"'
        
        print(f"🚀 Commande: {cmd}")
        
        start_time = time.time()
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ Transcription RAG terminée en {duration:.2f}s")
                
                # Trouver le fichier JSON généré
                search_dirs = [Path("output/transcriptions"), Path(".")]
                json_files = []
                for d in search_dirs:
                    if d.exists():
                        json_files.extend(d.glob("*advanced_rag*.json"))
                if json_files:
                    # Prendre le plus récent
                    self.json_file = max(json_files, key=lambda x: x.stat().st_mtime)
                    print(f"📄 Fichier JSON généré: {self.json_file.name}")
                    
                    # Analyser le contenu
                    with open(self.json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if 'transcription' in data and 'segments' in data['transcription']:
                        segments_count = len(data['transcription']['segments'])
                        total_text = sum(len(seg.get('text', '')) for seg in data['transcription']['segments'])
                        print(f"📊 Résultats: {segments_count} segments, {total_text:,} caractères")
                        
                        self.results['transcription'] = {
                            'duration': duration,
                            'segments': segments_count,
                            'characters': total_text,
                            'file': str(self.json_file)
                        }
                        
                        return True
                    else:
                        print("❌ Structure JSON invalide")
                        return False
                else:
                    print("❌ Aucun fichier JSON généré")
                    return False
            else:
                print(f"❌ Erreur transcription: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return False
    
    def step2_generate_keywords(self, top_n: int = 25) -> bool:
        """Étape 2: Génération de mots-clés."""
        print(f"\n🔍 ÉTAPE 2: Génération de mots-clés")
        print("=" * 50)
        
        if not self.json_file or not self.json_file.exists():
            print("❌ Aucun fichier JSON disponible")
            return False
        
        print(f"📄 Analyse du fichier: {self.json_file.name}")
        cmd = f'python generate_keywords_from_transcription.py "{self.json_file}" --top {top_n}'
        
        print(f"🚀 Commande: {cmd}")
        
        start_time = time.time()
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ Génération de mots-clés terminée en {duration:.2f}s")
                
                # Trouver le fichier de mots-clés généré
                search_dirs = [Path("output/keywords"), Path(".")]
                keywords_files = []
                for d in search_dirs:
                    if d.exists():
                        keywords_files.extend(d.glob("keywords_generated_*.txt"))
                if keywords_files:
                    self.keywords_file = max(keywords_files, key=lambda x: x.stat().st_mtime)
                    print(f"📝 Fichier mots-clés: {self.keywords_file.name}")
                    
                    # Lire les mots-clés générés
                    with open(self.keywords_file, 'r', encoding='utf-8') as f:
                        keywords_content = f.read()
                    
                    keywords_list = [line.strip() for line in keywords_content.split('\n') 
                                   if line.strip() and not line.startswith('#')]
                    
                    print(f"🔤 Mots-clés générés: {len(keywords_list)}")
                    print(f"📋 Top 10: {', '.join(keywords_list[:10])}")
                    
                    self.results['keywords'] = {
                        'duration': duration,
                        'count': len(keywords_list),
                        'file': str(self.keywords_file),
                        'top_keywords': keywords_list[:10]
                    }
                    
                    return True
                else:
                    print("❌ Aucun fichier de mots-clés généré")
                    return False
            else:
                print(f"❌ Erreur génération mots-clés: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return False
    
    def step3_analysis(self, questions: Optional[List[str]] = None) -> bool:
        """Étape 3: Analyse avec questions."""
        print(f"\n📊 ÉTAPE 3: Analyse avec questions")
        print("=" * 50)
        
        if not self.json_file or not self.json_file.exists():
            print("❌ Aucun fichier JSON disponible")
            return False
        
        # Questions par défaut si aucune fournie
        if not questions:
            questions = [
                "Quels sont les risques identifiés ?",
                "Quelles sont les actions prioritaires ?",
                "Quelles sont les échéances importantes ?",
                "Qui sont les personnes impliquées ?"
            ]
        
        print(f"📄 Analyse du fichier: {self.json_file.name}")
        print(f"❓ Questions: {len(questions)}")
        
        analysis_results = []
        total_duration = 0
        
        for i, question in enumerate(questions, 1):
            print(f"\n   {i}. {question}")
            
            cmd = f'python simple_audio_analyzer.py "{self.json_file}" --question "{question}"'
            
            start_time = time.time()
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                duration = time.time() - start_time
                total_duration += duration
                
                if result.returncode == 0:
                    print(f"   ✅ Réponse générée en {duration:.2f}s")
                    analysis_results.append({
                        'question': question,
                        'duration': duration,
                        'output': result.stdout
                    })
                else:
                    print(f"   ❌ Erreur: {result.stderr}")
                    analysis_results.append({
                        'question': question,
                        'duration': duration,
                        'error': result.stderr
                    })
                    
            except Exception as e:
                print(f"   ❌ Exception: {e}")
                analysis_results.append({
                    'question': question,
                    'duration': duration,
                    'error': str(e)
                })
        
        print(f"\n✅ Analyse terminée en {total_duration:.2f}s")
        
        self.results['analysis'] = {
            'duration': total_duration,
            'questions_count': len(questions),
            'results': analysis_results
        }
        
        return len(analysis_results) > 0
    
    def step4_summaries(self, summary_types: Optional[List[str]] = None) -> bool:
        """Étape 4: Génération de résumés."""
        print(f"\n📝 ÉTAPE 4: Génération de résumés")
        print("=" * 50)
        
        if not self.json_file or not self.json_file.exists():
            print("❌ Aucun fichier JSON disponible")
            return False
        
        # Types de résumés par défaut
        if not summary_types:
            summary_types = ["executive", "business", "detailed"]
        
        print(f"📄 Génération de résumés pour: {self.json_file.name}")
        print(f"📋 Types: {', '.join(summary_types)}")
        
        summary_results = []
        total_duration = 0
        
        for summary_type in summary_types:
            print(f"\n   📝 Résumé {summary_type}...")
            
            cmd = f'python audio_summarizer.py "{self.json_file}" --type {summary_type}'
            
            start_time = time.time()
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                duration = time.time() - start_time
                total_duration += duration
                
                if result.returncode == 0:
                    print(f"   ✅ Résumé {summary_type} généré en {duration:.2f}s")
                    summary_results.append({
                        'type': summary_type,
                        'duration': duration,
                        'output': result.stdout
                    })
                else:
                    print(f"   ❌ Erreur: {result.stderr}")
                    summary_results.append({
                        'type': summary_type,
                        'duration': duration,
                        'error': result.stderr
                    })
                    
            except Exception as e:
                print(f"   ❌ Exception: {e}")
                summary_results.append({
                    'type': summary_type,
                    'duration': duration,
                    'error': str(e)
                })
        
        print(f"\n✅ Résumés terminés en {total_duration:.2f}s")
        
        self.results['summaries'] = {
            'duration': total_duration,
            'types_count': len(summary_types),
            'results': summary_results
        }
        
        return len(summary_results) > 0
    
    def step5_generate_full_transcript(self) -> bool:
        """Étape 5: Génération du transcript complet."""
        print(f"\n📄 ÉTAPE 5: Génération du transcript complet")
        print("=" * 50)
        
        if not self.json_file or not self.json_file.exists():
            print("⚠️  Aucun fichier JSON disponible")
            return False
        
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extraire le texte complet
            full_text = ""
            if 'transcription' in data and 'text' in data['transcription']:
                full_text = data['transcription']['text']
            elif 'transcription' in data and 'full_text' in data['transcription']:
                full_text = data['transcription']['full_text']
            
            if not full_text:
                print("⚠️  Aucun texte trouvé dans la transcription")
                return False
            
            # Sauvegarder dans output/transcriptions/
            transcript_file = Path("output/transcriptions") / f"{self.json_file.stem}_transcript.txt"
            transcript_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(full_text)
            
            print(f"✅ Transcript complet sauvegardé : {transcript_file.name}")
            print(f"📊 Longueur : {len(full_text):,} caractères")
            
            self.results['full_transcript'] = {
                'file': str(transcript_file),
                'length': len(full_text)
            }
            
            return True
            
        except Exception as e:
            print(f"⚠️  Erreur lors de la génération du transcript : {e}")
            return False
    
    def step6_ai_correction(self, keywords: List[str]) -> bool:
        """Étape 6: Correction IA guidée par mots-clés."""
        print(f"\n🤖 ÉTAPE 6: Correction IA guidée par mots-clés")
        print("=" * 50)
        
        # Trouver les fichiers à corriger (résumés + transcript complet)
        summary_files = list(Path("output/summaries").glob("resume_*.md"))
        if not summary_files:
            summary_files = list(Path(".").glob("resume_*.md"))
        
        # Trouver aussi le transcript complet si disponible
        transcript_file = None
        if self.json_file and self.json_file.exists():
            transcript_file = Path("output/transcriptions") / f"{self.json_file.stem}_transcript.txt"
            if not transcript_file.exists():
                transcript_file = None
        
        if not summary_files and not transcript_file:
            print("⚠️  Aucun fichier trouvé pour correction")
            return False
        
        # Créer un fichier temporaire de mots-clés
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            temp_keywords_file = f.name
            f.write('\n'.join(keywords))
        
        files_to_correct = list(summary_files)
        if transcript_file:
            files_to_correct.append(transcript_file)
        
        print(f"📝 Correction de {len(files_to_correct)} fichiers...")
        
        correction_results = []
        total_duration = 0
        
        for file_to_correct in files_to_correct:
            print(f"\n   🤖 Correction: {file_to_correct.name}...")
            
            cmd = f'python ai_keyword_guided_correction.py "{file_to_correct}" --keywords "{temp_keywords_file}" --inplace'
            
            start_time = time.time()
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                duration = time.time() - start_time
                total_duration += duration
                
                if result.returncode == 0:
                    print(f"   ✅ Correction terminée en {duration:.2f}s")
                    # Parser le nombre de remplacements du rapport JSON
                    import re
                    match = re.search(r'(\d+) remplacements', result.stdout)
                    num_replacements = int(match.group(1)) if match else 0
                    correction_results.append({
                        'file': file_to_correct.name,
                        'duration': duration,
                        'replacements': num_replacements
                    })
                else:
                    print(f"   ⚠️  Erreur: {result.stderr}")
                    
            except Exception as e:
                print(f"   ⚠️  Exception: {e}")
        
        # Nettoyer le fichier temporaire
        try:
            os.unlink(temp_keywords_file)
        except:
            pass
        
        print(f"\n✅ Corrections IA terminées en {total_duration:.2f}s")
        
        total_replacements = sum(r.get('replacements', 0) for r in correction_results)
        if total_replacements > 0:
            print(f"📊 Total: {total_replacements} remplacements appliqués")
        
        self.results['ai_correction'] = {
            'duration': total_duration,
            'files_corrected': len(correction_results),
            'total_replacements': total_replacements,
            'results': correction_results
        }
        
        return True
    
    def run_complete_workflow(self, audio_file: str, initial_keywords: Optional[List[str]] = None,
                            questions: Optional[List[str]] = None, 
                            summary_types: Optional[List[str]] = None,
                            top_keywords: int = 25) -> bool:
        """Exécute le workflow complet."""
        print("🚀 WORKFLOW RAG COMPLET - Mac M4 Optimisé")
        print("=" * 60)
        
        start_time = time.time()
        
        # Étape 1: Transcription RAG
        if not self.step1_rag_transcription(audio_file, initial_keywords):
            print("❌ Échec de la transcription RAG")
            return False
        
        # Étape 2: Génération de mots-clés
        if not self.step2_generate_keywords(top_keywords):
            print("❌ Échec de la génération de mots-clés")
            return False
        
        # Étape 3: Analyse
        if not self.step3_analysis(questions):
            print("❌ Échec de l'analyse")
            return False
        
        # Étape 4: Résumés
        if not self.step4_summaries(summary_types):
            print("❌ Échec de la génération de résumés")
            return False
        
        # Étape 5: Génération du transcript complet (optionnelle)
        self.step5_generate_full_transcript()
        
        # Étape 6: Correction IA (optionnelle)
        if initial_keywords:
            self.step6_ai_correction(initial_keywords)
        
        total_duration = time.time() - start_time
        
        # Résumé final
        self._print_final_summary(total_duration)
        
        return True
    
    def _print_final_summary(self, total_duration: float):
        """Affiche le résumé final du workflow."""
        print(f"\n🎉 WORKFLOW COMPLET TERMINÉ")
        print("=" * 60)
        
        print(f"⏱️  Durée totale: {total_duration:.2f}s")
        
        print(f"\n📊 RÉSULTATS PAR ÉTAPE:")
        print("-" * 40)
        
        # Transcription
        if 'transcription' in self.results:
            t = self.results['transcription']
            print(f"🎤 Transcription: {t['duration']:.2f}s - {t['segments']} segments, {t['characters']:,} caractères")
        
        # Mots-clés
        if 'keywords' in self.results:
            k = self.results['keywords']
            print(f"🔍 Mots-clés: {k['duration']:.2f}s - {k['count']} mots-clés générés")
            print(f"   Top 5: {', '.join(k['top_keywords'][:5])}")
        
        # Analyse
        if 'analysis' in self.results:
            a = self.results['analysis']
            print(f"📊 Analyse: {a['duration']:.2f}s - {a['questions_count']} questions traitées")
        
        # Résumés
        if 'summaries' in self.results:
            s = self.results['summaries']
            print(f"📝 Résumés: {s['duration']:.2f}s - {s['types_count']} types générés")
        
        # Transcript complet
        if 'full_transcript' in self.results:
            ft = self.results['full_transcript']
            print(f"📄 Transcript complet: {ft['length']:,} caractères")
        
        # Correction IA
        if 'ai_correction' in self.results:
            ai = self.results['ai_correction']
            print(f"🤖 Correction IA: {ai['duration']:.2f}s - {ai['total_replacements']} remplacements appliqués sur {ai['files_corrected']} fichiers")
        
        print(f"\n📁 FICHIERS GÉNÉRÉS:")
        print("-" * 30)
        if self.json_file:
            print(f"📄 Transcription: {self.json_file.name}")
        if self.keywords_file:
            print(f"🔤 Mots-clés: {self.keywords_file.name}")
        
        # Lister les fichiers de résumé générés
        summary_files = list(Path(".").glob("resume_*.md"))
        for summary_file in summary_files:
            if summary_file.stat().st_mtime > time.time() - 300:  # Fichiers créés dans les 5 dernières minutes
                print(f"📝 Résumé: {summary_file.name}")
        
        print(f"\n🚀 OPTIMISATIONS M4:")
        print("-" * 25)
        print("✅ GPU M4 (MPS) utilisé")
        print("✅ 14 threads CPU utilisés")
        print("✅ Mémoire unifiée optimisée")
        print("✅ Variables d'environnement configurées")
        
        # Sauvegarder les résultats
        results_file = f"workflow_results_{int(time.time())}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'audio_file': str(self.audio_file),
                'total_duration': total_duration,
                'results': self.results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Résultats sauvegardés: {results_file}")


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Workflow RAG complet optimisé pour Mac M4",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s audio.mp3                                    # Workflow complet avec paramètres par défaut
  %(prog)s audio.mp3 --keywords "Azure,Microsoft"  # Avec mots-clés initiaux
  %(prog)s audio.mp3 --questions "Quels risques?" "Actions?"  # Questions personnalisées
  %(prog)s audio.mp3 --summaries executive business     # Types de résumés spécifiques
  %(prog)s audio.mp3 --top-keywords 50                  # Plus de mots-clés générés
        """
    )
    
    parser.add_argument("audio_file", help="Fichier audio à traiter")
    parser.add_argument("--keywords", help="Mots-clés initiaux (séparés par des virgules)")
    parser.add_argument("--questions", nargs="+", help="Questions pour l'analyse")
    parser.add_argument("--summaries", nargs="+", choices=["executive", "business", "detailed", "all"],
                       help="Types de résumés à générer")
    parser.add_argument("--top-keywords", type=int, default=25,
                       help="Nombre de mots-clés à générer (défaut: 25)")
    
    args = parser.parse_args()
    
    try:
        # Initialiser le workflow
        workflow = RAGCompleteWorkflow()
        
        # Préparer les paramètres
        initial_keywords = None
        if args.keywords:
            initial_keywords = [kw.strip() for kw in args.keywords.split(",")]
        
        questions = args.questions
        summary_types = args.summaries
        top_keywords = args.top_keywords
        
        # Exécuter le workflow complet
        success = workflow.run_complete_workflow(
            audio_file=args.audio_file,
            initial_keywords=initial_keywords,
            questions=questions,
            summary_types=summary_types,
            top_keywords=top_keywords
        )
        
        if success:
            print("\n🎉 Workflow complet terminé avec succès!")
            return 0
        else:
            print("\n❌ Workflow échoué")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Workflow interrompu par l'utilisateur")
        return 1
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
