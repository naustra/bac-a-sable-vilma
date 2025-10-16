#!/usr/bin/env python3
"""
Script pour télécharger l'image principale d'articles Wikipedia
Utilise l'API Wikipedia (pas besoin de clé API)
"""

import requests
import json
import os
from pathlib import Path
from typing import Dict, Optional
import time

class WikipediaImageDownloader:
    """Téléchargeur d'images principales depuis Wikipedia"""

    API_URL = "https://en.wikipedia.org/w/api.php"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EducationalImageDownloader/1.0 (educational use)'
        })

    def get_main_image(self, article_title: str) -> Optional[Dict]:
        """
        Récupère l'image principale d'un article Wikipedia

        Args:
            article_title: Titre de l'article (ex: "Human eye")

        Returns:
            Dictionnaire avec les infos de l'image ou None
        """
        # Étape 1 : Récupérer le titre de l'image principale
        params = {
            'action': 'query',
            'format': 'json',
            'titles': article_title,
            'prop': 'pageimages',
            'piprop': 'original',
            'pithumbsize': 1000
        }

        response = self.session.get(self.API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        pages = data.get('query', {}).get('pages', {})
        page = next(iter(pages.values()))

        if 'original' not in page:
            print(f"⚠️  Pas d'image principale trouvée pour '{article_title}'")
            return None

        image_url = page['original']['source']
        image_width = page['original']['width']
        image_height = page['original']['height']

        return {
            'url': image_url,
            'width': image_width,
            'height': image_height,
            'article': article_title
        }

    def download_image(self, url: str, save_path: str) -> tuple[bool, Optional[str]]:
        """
        Télécharge une image depuis une URL et détecte le vrai format

        Args:
            url: URL de l'image
            save_path: Chemin où sauvegarder l'image

        Returns:
            (succès, chemin_final) - Le chemin peut changer si l'extension était incorrecte
        """
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()

            # Lire les premiers bytes pour détecter le format
            content = response.content

            # Détecter le vrai format
            if content.startswith(b'<svg') or content.startswith(b'<?xml'):
                print(f"⚠️  Format SVG détecté, ignoré (pas compatible Word)")
                return False, None
            elif content.startswith(b'\x89PNG'):
                extension = '.png'
            elif content.startswith(b'\xff\xd8\xff'):
                extension = '.jpg'
            else:
                print(f"⚠️  Format non reconnu")
                return False, None

            # Ajuster l'extension si nécessaire
            base_path = os.path.splitext(save_path)[0]
            final_path = base_path + extension

            # Créer le dossier parent si nécessaire
            Path(final_path).parent.mkdir(parents=True, exist_ok=True)

            # Sauvegarder l'image
            with open(final_path, 'wb') as f:
                f.write(content)

            return True, final_path

        except Exception as e:
            print(f"❌ Erreur lors du téléchargement: {e}")
            return False, None

    def download_article_image(self, article_title: str, output_path: str) -> tuple[bool, Optional[str]]:
        """
        Télécharge l'image principale d'un article Wikipedia

        Args:
            article_title: Titre de l'article Wikipedia
            output_path: Chemin de destination pour l'image

        Returns:
            (succès, chemin_final) - Le chemin peut différer si l'extension était incorrecte
        """
        print(f"\n📖 Article: {article_title}")

        # Récupérer l'info de l'image
        image_info = self.get_main_image(article_title)

        if not image_info:
            return False, None

        print(f"📸 Image trouvée: {image_info['width']}x{image_info['height']} px")

        # Télécharger
        success, final_path = self.download_image(image_info['url'], output_path)
        if success:
            print(f"✅ Téléchargé: {final_path}")
            return True, final_path

        return False, None


def main():
    """Test avec quelques articles"""
    downloader = WikipediaImageDownloader()

    # Test avec des articles sur le corps humain
    articles = [
        ("Human eye", "themes/corps_humain/photos/oeil_wiki.jpg"),
        ("Human nose", "themes/corps_humain/photos/nez_wiki.jpg"),
        ("Human hand", "themes/corps_humain/photos/main_wiki.jpg"),
        ("Heart", "themes/corps_humain/photos/coeur_wiki.jpg"),
    ]

    for article, output in articles:
        downloader.download_article_image(article, output)
        time.sleep(0.5)  # Pause pour ne pas surcharger l'API


if __name__ == "__main__":
    main()

