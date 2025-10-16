#!/usr/bin/env python3
"""
Téléchargeur multi-sources pour récupérer 10 images variées par mot
Sources: Wikipedia, Wikimedia Commons, Unsplash, Pexels
"""

import requests
import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
import io
from config_api import API_URLS, API_HEADERS, get_available_sources

class MultiSourceImageDownloader:
    """Téléchargeur d'images depuis plusieurs sources en parallèle"""

    def __init__(self, max_workers: int = 20):
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({'Connection': 'keep-alive'})
        self.available_sources = get_available_sources()

        print(f"🚀 Sources disponibles: {', '.join(self.available_sources)}")

    def download_from_unsplash(self, query: str, count: int = 3) -> List[Dict]:
        """Télécharge des images depuis Unsplash"""
        if 'unsplash' not in self.available_sources:
            return []

        try:
            headers = API_HEADERS['unsplash'].copy()
            if not headers.get('Authorization'):
                return []

            params = {
                'query': query,
                'per_page': count,
                'orientation': 'squarish'
            }

            response = self.session.get(
                f"{API_URLS['unsplash']}/search/photos",
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            images = []
            for photo in data.get('results', []):
                images.append({
                    'url': photo['urls']['regular'],
                    'width': photo['width'],
                    'height': photo['height'],
                    'source': 'unsplash',
                    'description': photo.get('description', ''),
                    'author': photo['user']['name']
                })

            return images

        except Exception as e:
            print(f"⚠️  Erreur Unsplash: {e}")
            return []

    def download_from_pexels(self, query: str, count: int = 3) -> List[Dict]:
        """Télécharge des images depuis Pexels"""
        if 'pexels' not in self.available_sources:
            return []

        try:
            headers = API_HEADERS['pexels'].copy()
            if not headers.get('Authorization'):
                return []

            params = {
                'query': query,
                'per_page': count,
                'orientation': 'square'
            }

            response = self.session.get(
                f"{API_URLS['pexels']}/search",
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            images = []
            for photo in data.get('photos', []):
                images.append({
                    'url': photo['src']['medium'],
                    'width': photo['width'],
                    'height': photo['height'],
                    'source': 'pexels',
                    'description': '',
                    'author': photo['photographer']
                })

            return images

        except Exception as e:
            print(f"⚠️  Erreur Pexels: {e}")
            return []

    def download_from_wikipedia(self, article_title: str, count: int = 2) -> List[Dict]:
        """Télécharge l'image principale d'un article Wikipedia"""
        try:
            headers = API_HEADERS['wikipedia'].copy()

            params = {
                'action': 'query',
                'format': 'json',
                'titles': article_title,
                'prop': 'pageimages',
                'piprop': 'original',
                'pithumbsize': 1000
            }

            response = self.session.get(
                API_URLS['wikipedia'],
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            pages = data.get('query', {}).get('pages', {})
            page = next(iter(pages.values()))

            if 'original' not in page:
                return []

            image_info = page['original']
            return [{
                'url': image_info['source'],
                'width': image_info['width'],
                'height': image_info['height'],
                'source': 'wikipedia',
                'description': f'Image principale de l\'article {article_title}',
                'author': 'Wikipedia'
            }]

        except Exception as e:
            print(f"⚠️  Erreur Wikipedia: {e}")
            return []

    def download_from_wikimedia(self, query: str, count: int = 3) -> List[Dict]:
        """Télécharge des images depuis Wikimedia Commons"""
        try:
            headers = API_HEADERS['wikimedia'].copy()

            # Rechercher des images
            search_params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': f'File:{query}',
                'srnamespace': 6,
                'srlimit': count * 2
            }

            response = self.session.get(
                API_URLS['wikimedia'],
                headers=headers,
                params=search_params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            results = data.get('query', {}).get('search', [])
            image_files = []

            for item in results[:count * 2]:
                title = item['title']
                if title.startswith('File:') and any(title.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                    image_files.append(title)
                    if len(image_files) >= count:
                        break

            if not image_files:
                return []

            # Récupérer les URLs
            image_params = {
                'action': 'query',
                'format': 'json',
                'titles': '|'.join(image_files),
                'prop': 'imageinfo',
                'iiprop': 'url|size|mime|thumburl',
                'iiurlwidth': 1000
            }

            response = self.session.get(
                API_URLS['wikimedia'],
                headers=headers,
                params=image_params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            images = []
            pages = data.get('query', {}).get('pages', {})

            for page_data in pages.values():
                if 'imageinfo' in page_data:
                    info = page_data['imageinfo'][0]
                    size_mb = info.get('size', 0) / (1024 * 1024)

                    if 0.1 <= size_mb <= 10:  # Entre 100KB et 10MB
                        # Utiliser l'URL de redimensionnement si disponible
                        thumbnail_url = info.get('thumburl', info.get('url'))

                        images.append({
                            'url': thumbnail_url,
                            'width': info.get('width'),
                            'height': info.get('height'),
                            'source': 'wikimedia',
                            'description': page_data['title'],
                            'author': 'Wikimedia Commons'
                        })

                        if len(images) >= count:
                            break

            return images

        except Exception as e:
            print(f"⚠️  Erreur Wikimedia: {e}")
            return []

    def download_image(self, image_info: Dict, save_path: str) -> Tuple[bool, Optional[str]]:
        """Télécharge une image et détecte le format"""
        try:
            response = self.session.get(image_info['url'], stream=True, timeout=15)
            response.raise_for_status()

            content = response.content

            # Détecter le format
            if content.startswith(b'<svg') or content.startswith(b'<?xml'):
                print(f"      ⚠️  SVG détecté, ignoré")
                return False, None
            elif content.startswith(b'\x89PNG'):
                extension = '.png'
            elif content.startswith(b'\xff\xd8\xff'):
                extension = '.jpg'
            else:
                print(f"      ⚠️  Format non reconnu")
                return False, None

            # Ajuster l'extension
            base_path = os.path.splitext(save_path)[0]
            final_path = base_path + extension

            # Créer le dossier
            Path(final_path).parent.mkdir(parents=True, exist_ok=True)

            # Sauvegarder
            with open(final_path, 'wb') as f:
                f.write(content)

            return True, final_path

        except Exception as e:
            print(f"      ⚠️  Erreur téléchargement: {e}")
            return False, None

    def select_best_image(self, image_list: List[str]) -> str:
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
                    if 'unsplash' in filename:
                        score += 4
                    elif 'pexels' in filename:
                        score += 3
                    elif 'wikipedia' in filename:
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

    def download_10_images_for_word(self, word: str, french_name: str, macedonian_name: str, output_dir: str) -> Tuple[List[str], str]:
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

        # Préparer les tâches de téléchargement par source
        all_images = []

        # Unsplash (3 images)
        if 'unsplash' in self.available_sources:
            print("📸 Unsplash...")
            unsplash_images = self.download_from_unsplash(word, 3)
            all_images.extend(unsplash_images)

        # Pexels (3 images)
        if 'pexels' in self.available_sources:
            print("📸 Pexels...")
            pexels_images = self.download_from_pexels(word, 3)
            all_images.extend(pexels_images)

        # Wikipedia (2 images)
        if 'wikipedia' in self.available_sources:
            print("📸 Wikipedia...")
            wikipedia_images = self.download_from_wikipedia(f"Human {word}", 2)
            all_images.extend(wikipedia_images)

        # Wikimedia Commons (2 images)
        if 'wikimedia' in self.available_sources:
            print("📸 Wikimedia Commons...")
            wikimedia_images = self.download_from_wikimedia(f"human {word} close up", 2)
            all_images.extend(wikimedia_images)

        if not all_images:
            print(f"❌ Aucune image trouvée pour {french_name}")
            return [], None

        print(f"📊 {len(all_images)} images trouvées au total")

        # Télécharger toutes les images en parallèle
        downloaded_files = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []

            for i, image_info in enumerate(all_images[:10]):  # Limiter à 10
                source = image_info['source']
                output_path = os.path.join(output_dir, f"{french_name}_{source}_{i+1}.jpg")

                future = executor.submit(self.download_image, image_info, output_path)
                futures.append((future, source, i+1, image_info))

            # Traiter les résultats
            for future, source, num, image_info in futures:
                try:
                    success, final_path = future.result(timeout=30)
                    if success and final_path:
                        downloaded_files.append(final_path)
                        print(f"   ✅ {source} #{num}: {os.path.basename(final_path)} ({image_info['width']}x{image_info['height']} px)")
                    else:
                        print(f"   ❌ {source} #{num}: Échec")
                except Exception as e:
                    print(f"   ❌ {source} #{num}: {e}")

        # Sélectionner la meilleure image
        best_image = self.select_best_image(downloaded_files)

        if best_image:
            print(f"🏆 Meilleure image: {os.path.basename(best_image)}")
        else:
            print(f"⚠️  Aucune image valide pour {french_name}")

        return downloaded_files, best_image

    def download_multiple_words_parallel(self, words_data: List[Tuple], output_dir: str) -> Dict[str, str]:
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
    downloader = MultiSourceImageDownloader(max_workers=20)

    # Test avec des parties du corps
    words = [
        ("eye", "œil", "око"),
        ("hand", "main", "рака"),
        ("heart", "cœur", "срце"),
    ]

    output_dir = "themes/corps_humain/photos"

    start_time = time.time()
    results = downloader.download_multiple_words_parallel(words, output_dir)
    end_time = time.time()

    print(f"\n⏱️  Temps total: {end_time - start_time:.1f} secondes")
    print(f"📊 {len(results)} mots traités avec succès")


if __name__ == "__main__":
    main()
