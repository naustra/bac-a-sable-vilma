#!/usr/bin/env python3
"""
Script pour télécharger des images depuis Wikimedia Commons
Utilise l'API MediaWiki (pas besoin de clé API)
"""

import requests
import json
import os
from pathlib import Path
from typing import List, Dict
import time

class WikimediaDownloader:
    """Téléchargeur d'images depuis Wikimedia Commons"""

    API_URL = "https://commons.wikimedia.org/w/api.php"

    def __init__(self):
        self.session = requests.Session()
        # User-Agent requis pour l'API Wikimedia
        self.session.headers.update({
            'User-Agent': 'EducationalImageDownloader/1.0 (pierre.lebihan@example.com)'
        })

    def search_images(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Recherche des images sur Wikimedia Commons

        Args:
            query: Terme de recherche
            limit: Nombre maximum de résultats

        Returns:
            Liste de dictionnaires avec les informations des fichiers
        """
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': f'File:{query}',
            'srnamespace': 6,  # Namespace 6 = Files
            'srlimit': limit,
            'srprop': 'snippet|titlesnippet'
        }

        response = self.session.get(self.API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        if 'query' in data and 'search' in data['query']:
            for item in data['query']['search']:
                results.append({
                    'title': item['title'],
                    'snippet': item.get('snippet', ''),
                    'pageid': item['pageid']
                })

        return results

    def get_image_info(self, filename: str) -> Dict:
        """
        Récupère les informations d'une image (URL, dimensions, etc.)

        Args:
            filename: Nom du fichier (ex: "File:Human eye.jpg" ou juste "Human eye.jpg")

        Returns:
            Dictionnaire avec les infos de l'image
        """
        # S'assurer que le filename commence par "File:"
        if not filename.startswith('File:'):
            filename = f'File:{filename}'

        params = {
            'action': 'query',
            'format': 'json',
            'titles': filename,
            'prop': 'imageinfo',
            'iiprop': 'url|size|mime|extmetadata',
            'iiurlwidth': 1000  # Largeur max pour la thumbnail
        }

        response = self.session.get(self.API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Extraire les infos
        pages = data.get('query', {}).get('pages', {})
        page = next(iter(pages.values()))

        if 'imageinfo' in page:
            info = page['imageinfo'][0]
            return {
                'url': info.get('url'),
                'thumburl': info.get('thumburl'),
                'width': info.get('width'),
                'height': info.get('height'),
                'size': info.get('size'),
                'mime': info.get('mime'),
                'description': info.get('extmetadata', {}).get('ImageDescription', {}).get('value', '')
            }

        return None

    def download_image(self, url: str, save_path: str) -> bool:
        """
        Télécharge une image depuis une URL

        Args:
            url: URL de l'image
            save_path: Chemin où sauvegarder l'image

        Returns:
            True si réussi, False sinon
        """
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()

            # Créer le dossier parent si nécessaire
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)

            # Sauvegarder l'image
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"✅ Téléchargé: {save_path}")
            return True

        except Exception as e:
            print(f"❌ Erreur lors du téléchargement: {e}")
            return False

    def search_and_download(self, query: str, output_dir: str, count: int = 3, filename_prefix: str = None):
        """
        Recherche et télécharge des images

        Args:
            query: Terme de recherche
            output_dir: Dossier de destination
            count: Nombre d'images à télécharger
            filename_prefix: Préfixe pour les noms de fichiers (ex: "oeil")
        """
        print(f"\n🔍 Recherche: '{query}' sur Wikimedia Commons...")

        # Rechercher des images
        results = self.search_images(query, limit=count * 5)  # Chercher plus pour avoir du choix après filtrage

        if not results:
            print(f"❌ Aucune image trouvée pour '{query}'")
            return

        print(f"📸 {len(results)} résultats trouvés")

        # Types MIME acceptés pour les documents Word
        ACCEPTED_MIMES = ['image/jpeg', 'image/png', 'image/jpg']
        MAX_SIZE_MB = 10  # Limite de taille en MB

        # Télécharger les images
        downloaded = 0
        for i, result in enumerate(results):
            if downloaded >= count:
                break

            print(f"\n📥 Candidat {i + 1}: {result['title']}")

            # Récupérer les infos de l'image
            info = self.get_image_info(result['title'])

            if not info or not info.get('url'):
                print(f"   ⚠️  Pas d'URL disponible")
                continue

            # Filtrer par type MIME
            mime = info.get('mime', '')
            if mime not in ACCEPTED_MIMES:
                print(f"   ⚠️  Format non supporté: {mime} (on veut JPG/PNG)")
                continue

            # Filtrer par taille
            size_mb = info.get('size', 0) / (1024 * 1024)
            if size_mb > MAX_SIZE_MB:
                print(f"   ⚠️  Fichier trop gros: {size_mb:.1f} MB")
                continue

            # Déterminer le nom du fichier
            if filename_prefix:
                ext = 'jpg' if 'jpeg' in mime else 'png'
                filename = f"{filename_prefix}_{downloaded + 1}.{ext}"
            else:
                filename = result['title'].replace('File:', '').replace(' ', '_')

            save_path = os.path.join(output_dir, filename)

            # Télécharger
            if self.download_image(info['url'], save_path):
                downloaded += 1
                print(f"   ✅ Image {downloaded}/{count} téléchargée")
                print(f"   📐 Dimensions: {info['width']}x{info['height']} px")
                print(f"   💾 Taille: {size_mb:.1f} MB")

            # Pause pour ne pas surcharger l'API
            time.sleep(0.5)

        print(f"\n{'✅' if downloaded > 0 else '❌'} {downloaded} images téléchargées dans {output_dir}")


def main():
    """Fonction principale pour tester"""
    downloader = WikimediaDownloader()

    # Test avec quelques recherches
    test_queries = [
        ("human eye anatomy", "oeil"),
        ("human heart anatomy", "coeur"),
        ("human hand anatomy", "main"),
    ]

    output_dir = "themes/corps_humain_wikimedia/photos"

    for query, prefix in test_queries:
        downloader.search_and_download(
            query=query,
            output_dir=output_dir,
            count=3,
            filename_prefix=prefix
        )
        print("\n" + "="*80)


if __name__ == "__main__":
    main()

