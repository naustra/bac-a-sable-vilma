#!/usr/bin/env python3
"""
Version simplifiée du téléchargeur multi-sources
Utilise les téléchargeurs existants qui fonctionnent
"""

from telecharger_images_wikipedia_optimized import WikipediaImageDownloaderOptimized
from telecharger_images_wikimedia import WikimediaDownloader
from convertir_images import convertir_images_pour_docx
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

class MultiSourceImageDownloaderSimple:
    """Téléchargeur multi-sources simplifié utilisant les téléchargeurs existants"""
    
    def __init__(self, max_workers: int = 20):
        self.max_workers = max_workers
        self.wikipedia_downloader = WikipediaImageDownloaderOptimized(max_workers=10)
        self.wikimedia_downloader = WikimediaDownloader()
    
    def download_from_wikipedia(self, article_title: str, output_dir: str, prefix: str, count: int = 3) -> list:
        """Télécharge des images depuis Wikipedia"""
        try:
            files = self.wikipedia_downloader.download_article_images_parallel(
                article_title, output_dir, count, prefix
            )
            return files
        except Exception as e:
            print(f"      ⚠️  Erreur Wikipedia: {e}")
            return []
    
    def download_from_wikimedia(self, query: str, output_dir: str, prefix: str, count: int = 3) -> list:
        """Télécharge des images depuis Wikimedia Commons"""
        try:
            # Créer un dossier temporaire pour cette source
            temp_dir = os.path.join(output_dir, f"{prefix}_temp")
            os.makedirs(temp_dir, exist_ok=True)
            
            self.wikimedia_downloader.search_and_download(
                query=query,
                output_dir=temp_dir,
                count=count,
                filename_prefix=prefix
            )
            
            # Déplacer les fichiers vers le dossier principal
            files = []
            for filename in os.listdir(temp_dir):
                if filename.endswith(('.jpg', '.png')):
                    old_path = os.path.join(temp_dir, filename)
                    new_path = os.path.join(output_dir, f"{prefix}_wikimedia_{filename}")
                    os.rename(old_path, new_path)
                    files.append(new_path)
            
            # Nettoyer le dossier temporaire
            os.rmdir(temp_dir)
            
            return files
        except Exception as e:
            print(f"      ⚠️  Erreur Wikimedia: {e}")
            return []
    
    def select_best_image(self, image_list: list) -> str:
        """Sélectionne la meilleure image selon les critères"""
        if not image_list:
            return None
        
        best_image = None
        best_score = -1
        
        for image_path in image_list:
            try:
                with Image.open(image_path) as img:
                    width, height = img.size
                    
                    # Score basé sur les critères
                    score = 0
                    
                    # Résolution (>800px = bonus)
                    if width >= 800:
                        score += 2
                    
                    # Ratio d'aspect proche de 1:1
                    aspect_ratio = min(width, height) / max(width, height)
                    if aspect_ratio > 0.8:  # Proche du carré
                        score += 3
                    elif aspect_ratio > 0.6:
                        score += 1
                    
                    # Priorité par source
                    filename = os.path.basename(image_path)
                    if 'wikipedia' in filename:
                        score += 2
                    elif 'wikimedia' in filename:
                        score += 1
                    
                    # Taille de fichier (pas trop gros)
                    file_size = os.path.getsize(image_path) / (1024 * 1024)  # MB
                    if file_size < 5:
                        score += 1
                    
                    if score > best_score:
                        best_score = score
                        best_image = image_path
                        
            except Exception:
                continue
        
        return best_image
    
    def download_10_images_for_word(self, word: str, french_name: str, macedonian_name: str, output_dir: str) -> tuple:
        """
        Télécharge 10 images pour un mot depuis toutes les sources
        
        Args:
            word: Mot en anglais pour la recherche
            french_name: Nom en français
            macedonian_name: Nom en macédonien
            output_dir: Dossier de destination
            
        Returns:
            (liste_des_images_téléchargées, meilleure_image)
        """
        print(f"\n🔍 {french_name.upper()} ({macedonian_name})")
        print("=" * 60)
        
        all_files = []
        
        # Wikipedia (5 images)
        print("📸 Wikipedia...")
        wikipedia_files = self.download_from_wikipedia(
            f"Human {word}", output_dir, f"{french_name}_wikipedia", 5
        )
        all_files.extend(wikipedia_files)
        
        # Wikimedia Commons (5 images)
        print("📸 Wikimedia Commons...")
        wikimedia_files = self.download_from_wikimedia(
            f"human {word} close up", output_dir, f"{french_name}_wikimedia", 5
        )
        all_files.extend(wikimedia_files)
        
        print(f"📊 {len(all_files)} images téléchargées au total")
        
        # Sélectionner la meilleure image
        best_image = self.select_best_image(all_files)
        
        if best_image:
            print(f"🏆 Meilleure image: {os.path.basename(best_image)}")
        else:
            print(f"⚠️  Aucune image valide pour {french_name}")
        
        return all_files, best_image
    
    def download_multiple_words_parallel(self, words_data: list, output_dir: str) -> dict:
        """
        Télécharge des images pour plusieurs mots en parallèle
        
        Args:
            words_data: Liste de (word_en, french_name, macedonian_name)
            output_dir: Dossier de destination
            
        Returns:
            Dictionnaire {french_name: meilleure_image}
        """
        print(f"\n🚀 TÉLÉCHARGEMENT PARALLÈLE DE {len(words_data)} MOTS")
        print("=" * 80)
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(words_data))) as executor:
            # Soumettre toutes les tâches
            futures = {}
            for word, french, macedonian in words_data:
                future = executor.submit(
                    self.download_10_images_for_word,
                    word, french, macedonian, output_dir
                )
                futures[future] = french
            
            # Traiter les résultats
            for future in as_completed(futures):
                french_name = futures[future]
                try:
                    downloaded_files, best_image = future.result()
                    if best_image:
                        results[french_name] = os.path.basename(best_image)
                        print(f"✅ {french_name}: {len(downloaded_files)} images → {os.path.basename(best_image)}")
                    else:
                        print(f"❌ {french_name}: Aucune image valide")
                except Exception as e:
                    print(f"❌ {french_name}: Erreur - {e}")
        
        return results


def main():
    """Test avec quelques mots"""
    downloader = MultiSourceImageDownloaderSimple(max_workers=10)
    
    # Test avec des parties du corps
    words = [
        ("eye", "oeil", "око"),
        ("hand", "main", "рака"),
        ("heart", "coeur", "срце"),
    ]
    
    output_dir = "themes/corps_humain/photos"
    
    start_time = time.time()
    results = downloader.download_multiple_words_parallel(words, output_dir)
    end_time = time.time()
    
    print(f"\n⏱️  Temps total: {end_time - start_time:.1f} secondes")
    print(f"📊 {len(results)} mots traités avec succès")


if __name__ == "__main__":
    main()
