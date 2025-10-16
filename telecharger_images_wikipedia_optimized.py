#!/usr/bin/env python3
"""
Script optimisé pour télécharger plusieurs images d'articles Wikipedia
Utilise le parallélisme pour des téléchargements ultra-rapides
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

class WikipediaImageDownloaderOptimized:
    """Téléchargeur d'images optimisé depuis Wikipedia avec parallélisme"""

    API_URL = "https://en.wikipedia.org/w/api.php"

    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EducationalImageDownloader/2.0 (educational use)',
            'Connection': 'keep-alive'
        })

    def get_article_images(self, article_title: str, count: int = 3) -> List[Dict]:
        """
        Récupère plusieurs images d'un article Wikipedia

        Args:
            article_title: Titre de l'article (ex: "Human eye")
            count: Nombre d'images à récupérer

        Returns:
            Liste de dictionnaires avec les infos des images
        """
        # Étape 1 : Récupérer les images de l'article
        params = {
            'action': 'query',
            'format': 'json',
            'titles': article_title,
            'prop': 'images',
            'imlimit': count * 2  # Récupérer plus pour avoir du choix
        }

        response = self.session.get(self.API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        pages = data.get('query', {}).get('pages', {})
        page = next(iter(pages.values()))

        if 'images' not in page:
            return []

        # Filtrer pour garder seulement les images (pas les sous-pages)
        image_files = []
        for img in page['images'][:count * 2]:
            title = img['title']
            if title.startswith('File:') and any(title.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                image_files.append(title)
                if len(image_files) >= count:
                    break

        if not image_files:
            return []

        # Étape 2 : Récupérer les URLs et métadonnées des images
        image_params = {
            'action': 'query',
            'format': 'json',
            'titles': '|'.join(image_files),
            'prop': 'imageinfo',
            'iiprop': 'url|size|mime',
            'iiurlwidth': 1000
        }

        response = self.session.get(self.API_URL, params=image_params)
        response.raise_for_status()
        data = response.json()

        images = []
        pages = data.get('query', {}).get('pages', {})

        for page_data in pages.values():
            if 'imageinfo' in page_data:
                info = page_data['imageinfo'][0]

                # Filtrer par taille (pas trop petit, pas trop gros)
                size_mb = info.get('size', 0) / (1024 * 1024)
                if 0.1 <= size_mb <= 10:  # Entre 100KB et 10MB
                    images.append({
                        'url': info.get('url'),
                        'width': info.get('width'),
                        'height': info.get('height'),
                        'size': info.get('size'),
                        'mime': info.get('mime'),
                        'title': page_data['title']
                    })

                    if len(images) >= count:
                        break

        return images

    def download_image_fast(self, image_info: Dict, save_path: str) -> Tuple[bool, Optional[str]]:
        """
        Télécharge une image rapidement avec détection de format

        Args:
            image_info: Dictionnaire avec les infos de l'image
            save_path: Chemin de destination

        Returns:
            (succès, chemin_final)
        """
        try:
            response = self.session.get(image_info['url'], stream=True, timeout=10)
            response.raise_for_status()

            # Lire le contenu
            content = response.content

            # Détecter le format et filtrer
            if content.startswith(b'<svg') or content.startswith(b'<?xml'):
                return False, None
            elif content.startswith(b'\x89PNG'):
                extension = '.png'
            elif content.startswith(b'\xff\xd8\xff'):
                extension = '.jpg'
            else:
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
            print(f"⚠️  Erreur téléchargement: {e}")
            return False, None

    def download_article_images_parallel(self, article_title: str, output_dir: str, count: int = 3, filename_prefix: str = None) -> List[str]:
        """
        Télécharge plusieurs images d'un article en parallèle

        Args:
            article_title: Titre de l'article
            output_dir: Dossier de destination
            count: Nombre d'images à télécharger
            filename_prefix: Préfixe pour les noms de fichiers

        Returns:
            Liste des chemins des images téléchargées
        """
        print(f"\n📖 Article: {article_title}")

        # Récupérer les infos des images
        images = self.get_article_images(article_title, count)

        if not images:
            print(f"⚠️  Pas d'images trouvées pour '{article_title}'")
            return []

        print(f"📸 {len(images)} images trouvées")

        # Préparer les tâches de téléchargement
        downloaded_files = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Soumettre toutes les tâches
            futures = []
            for i, image_info in enumerate(images[:count]):
                if filename_prefix:
                    output_path = os.path.join(output_dir, f"{filename_prefix}_{i+1}.jpg")
                else:
                    # Extraire le nom du fichier depuis le titre
                    filename = image_info['title'].replace('File:', '').replace(' ', '_')
                    output_path = os.path.join(output_dir, filename)

                future = executor.submit(self.download_image_fast, image_info, output_path)
                futures.append((future, i+1, image_info))

            # Traiter les résultats au fur et à mesure
            for future, num, image_info in futures:
                try:
                    success, final_path = future.result(timeout=30)
                    if success and final_path:
                        downloaded_files.append(os.path.basename(final_path))
                        print(f"   ✅ Image {num}/{count}: {os.path.basename(final_path)} ({image_info['width']}x{image_info['height']} px)")
                    else:
                        print(f"   ❌ Image {num}: Échec")
                except Exception as e:
                    print(f"   ❌ Image {num}: {e}")

        return downloaded_files

    def download_multiple_articles_parallel(self, articles_data: List[Tuple[str, str, str]], output_dir: str) -> Dict[str, str]:
        """
        Télécharge des images pour plusieurs articles en parallèle

        Args:
            articles_data: Liste de (article_title, filename_prefix, french_name)
            output_dir: Dossier de destination

        Returns:
            Dictionnaire {french_name: image_file}
        """
        print(f"\n🚀 TÉLÉCHARGEMENT PARALLÈLE DE {len(articles_data)} ARTICLES")
        print("=" * 80)

        results = {}

        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(articles_data))) as executor:
            # Soumettre toutes les tâches
            futures = {}
            for article, prefix, french_name in articles_data:
                future = executor.submit(
                    self.download_article_images_parallel,
                    article, output_dir, 3, prefix
                )
                futures[future] = french_name

            # Traiter les résultats
            for future in as_completed(futures):
                french_name = futures[future]
                try:
                    downloaded_files = future.result()
                    if downloaded_files:
                        results[french_name] = downloaded_files[0]  # Prendre la première
                        print(f"✅ {french_name}: {downloaded_files[0]}")
                    else:
                        print(f"❌ {french_name}: Aucune image téléchargée")
                except Exception as e:
                    print(f"❌ {french_name}: Erreur - {e}")

        return results


def main():
    """Test avec plusieurs articles"""
    downloader = WikipediaImageDownloaderOptimized(max_workers=8)

    # Test avec des articles sur le corps humain
    articles = [
        ("Human eye", "oeil", "œil"),
        ("Human nose", "nez", "nez"),
        ("Hand", "main", "main"),
        ("Heart", "coeur", "cœur"),
    ]

    output_dir = "themes/corps_humain/photos"

    start_time = time.time()
    results = downloader.download_multiple_articles_parallel(articles, output_dir)
    end_time = time.time()

    print(f"\n⏱️  Temps total: {end_time - start_time:.1f} secondes")
    print(f"📊 {len(results)} articles traités avec succès")


if __name__ == "__main__":
    main()
