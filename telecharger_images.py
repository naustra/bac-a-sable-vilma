#!/usr/bin/env python3
"""
Téléchargeur d'images unifié multi-sources avec scoring CLIP
Combine téléchargement + conversion + scoring en un seul module
"""

import requests
import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
import io
from config_api import API_URLS, API_HEADERS, get_available_sources, check_api_keys
from convertir_images import convertir_images_pour_docx
from scorer_images_clip import CLIPImageScorer

class UnifiedImageDownloader:
    """Téléchargeur d'images unifié avec scoring CLIP automatique"""

    def __init__(self, max_workers: int = 20, enable_clip: bool = True):
        self.max_workers = max_workers
        self.enable_clip = enable_clip
        self.session = requests.Session()
        self.session.headers.update({'Connection': 'keep-alive'})
        self.available_sources = get_available_sources()

        # Initialiser CLIP si activé
        self.clip_scorer = None
        if self.enable_clip:
            try:
                self.clip_scorer = CLIPImageScorer()
                print("🧠 Scoring CLIP activé")
            except Exception as e:
                print(f"⚠️  CLIP non disponible: {e}")
                self.enable_clip = False

        print(f"🚀 Sources disponibles: {', '.join(self.available_sources)}")

    def _make_child_friendly_query(self, query: str) -> str:
        """Adapte une requête pour être adaptée aux enfants"""
        # Mots-clés pour rendre les images plus adaptées aux enfants
        child_keywords = [
            "cute", "friendly", "colorful", "bright", "happy", "smiling",
            "cartoon", "illustration", "simple", "clear", "educational",
            "child", "kid", "family", "safe", "innocent", "playful"
        ]

        # Requêtes spécifiques simples et efficaces
        child_specific_queries = {
            "dog": "cute cartoon dog for children",
            "cat": "cute cartoon cat for kids",
            "bird": "colorful cartoon bird for children",
            "fish": "colorful cartoon fish for kids",
            "horse": "friendly cartoon horse for children",
            "cow": "friendly cartoon cow for kids",
            "pig": "cute cartoon pig for children",
            "sheep": "cute cartoon sheep for kids",
            "head": "friendly cartoon face for children",
            "eye": "friendly cartoon eye for kids",
            "nose": "friendly cartoon nose for children",
            "mouth": "smiling cartoon mouth for kids",
            "hand": "friendly cartoon hand for children",
            "leg": "friendly cartoon leg for kids",
            "heart": "cartoon heart for children",
            "stomach": "friendly cartoon body part for kids",
            "ear": "friendly cartoon ear for children",
            "hair": "colorful cartoon hair for kids",
            "sun": "bright cartoon sun for children",
            "cloud": "white cartoon cloud for kids",
            "rain": "cartoon rainbow for children",
            "snow": "white cartoon snow for kids",
            "wind": "cartoon windmill for children",
            "storm": "cartoon thunderstorm for kids",
            "lightning": "cartoon lightning for children",
            "rainbow": "colorful cartoon rainbow for kids"
        }

        # Utiliser une requête spécifique si disponible
        if query.lower() in child_specific_queries:
            return child_specific_queries[query.lower()]

        # Sinon, ajouter des mots-clés adaptés aux enfants (simple et efficace)
        child_query = f"cartoon {query} for children"
        return child_query

    def download_from_unsplash(self, query: str, count: int = 5) -> List[Dict]:
        """Télécharge des images depuis Unsplash"""
        if 'unsplash' not in self.available_sources:
            return []

        try:
            headers = API_HEADERS['unsplash'].copy()
            if not headers.get('Authorization'):
                return []

            # Adapter la requête pour les enfants
            child_friendly_query = self._make_child_friendly_query(query)

            params = {
                'query': child_friendly_query,
                'per_page': count,
                'orientation': 'squarish',
                'content_filter': 'high'  # Filtre de contenu élevé
            }

            response = self.session.get(
                f"{API_URLS['unsplash']}/search/photos",
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            results = []

            for photo in data.get('results', []):
                if photo.get('urls', {}).get('regular'):
                    results.append({
                        'url': photo['urls']['regular'],
                        'source': 'unsplash',
                        'description': photo.get('description', ''),
                        'author': photo.get('user', {}).get('name', ''),
                        'width': photo.get('width', 0),
                        'height': photo.get('height', 0)
                    })

            return results

        except Exception as e:
            print(f"⚠️  Erreur Unsplash: {e}")
            return []

    def download_from_pexels(self, query: str, count: int = 5) -> List[Dict]:
        """Télécharge des images depuis Pexels"""
        if 'pexels' not in self.available_sources:
            return []

        try:
            headers = API_HEADERS['pexels'].copy()
            if not headers.get('Authorization'):
                return []

            # Adapter la requête pour les enfants
            child_friendly_query = self._make_child_friendly_query(query)

            params = {
                'query': child_friendly_query,
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
            results = []

            for photo in data.get('photos', []):
                if photo.get('src', {}).get('large2x'):
                    results.append({
                        'url': photo['src']['large2x'],
                        'source': 'pexels',
                        'description': photo.get('alt', ''),
                        'author': photo.get('photographer', ''),
                        'width': photo.get('width', 0),
                        'height': photo.get('height', 0)
                    })

            return results

        except Exception as e:
            print(f"⚠️  Erreur Pexels: {e}")
            return []

    def download_from_wikipedia(self, query: str, count: int = 5) -> List[Dict]:
        """Télécharge des images depuis Wikipedia en utilisant l'API REST"""
        try:
            # Adapter la requête pour les enfants
            child_friendly_query = self._make_child_friendly_query(query)

            # Utiliser l'API REST de MediaWiki (selon la documentation officielle)
            search_url = "https://en.wikipedia.org/w/rest.php/v1/search/page"
            search_params = {
                'q': child_friendly_query,
                'limit': 3
            }

            # Headers selon la documentation MediaWiki
            headers = {
                'User-Agent': 'EducationalImageDownloader/2.0 (https://github.com/educational-tools; educational use) requests/2.31.0',
                'Accept': 'application/json'
            }

            response = self.session.get(search_url, params=search_params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for page in data.get('pages', []):
                title = page['title']

                # Utiliser l'API REST pour récupérer les images de la page
                page_url = f"https://en.wikipedia.org/w/rest.php/v1/page/{title.replace(' ', '_')}"
                page_response = self.session.get(page_url, headers=headers, timeout=10)

                if page_response.status_code == 200:
                    page_data = page_response.json()

                    # Chercher les images dans le contenu de la page
                    if 'source' in page_data:
                        content = page_data['source']
                        # Extraire les liens d'images (format [[File:...]])
                        import re
                        image_matches = re.findall(r'\[\[File:([^\]]+\.(?:jpg|jpeg|png))', content, re.IGNORECASE)

                        for image_filename in image_matches[:count]:
                            # Construire l'URL de l'image
                            image_url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{image_filename[:1]}/{image_filename[:2]}/{image_filename}/1000px-{image_filename}"

                            results.append({
                                'url': image_url,
                                'source': 'wikipedia',
                                'description': f"Image from {title}",
                                'author': 'Wikipedia',
                                'width': 1000,
                                'height': 1000
                            })

                            if len(results) >= count:
                                break

                if len(results) >= count:
                    break

            return results[:count]

        except Exception as e:
            print(f"⚠️  Erreur Wikipedia: {e}")
            return []

    def download_from_wikimedia(self, query: str, count: int = 5) -> List[Dict]:
        """Télécharge des images depuis Wikimedia Commons"""
        try:
            # Adapter la requête pour les enfants
            child_friendly_query = self._make_child_friendly_query(query)

            # Utiliser l'API REST de MediaWiki pour Wikimedia Commons
            search_url = "https://commons.wikimedia.org/w/rest.php/v1/search/page"
            search_params = {
                'q': f'{child_friendly_query} filetype:bitmap',
                'limit': count
            }

            # Headers selon la documentation MediaWiki
            headers = {
                'User-Agent': 'EducationalImageDownloader/2.0 (https://github.com/educational-tools; educational use) requests/2.31.0',
                'Accept': 'application/json'
            }

            response = self.session.get(search_url, params=search_params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for page in data.get('pages', []):
                title = page['title']

                # Vérifier que c'est bien un fichier image
                if title.startswith('File:') and title.lower().endswith(('.jpg', '.jpeg', '.png')):
                    # Construire l'URL de l'image
                    filename = title.replace('File:', '')
                    image_url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{filename[:1]}/{filename[:2]}/{filename}/1000px-{filename}"

                    results.append({
                        'url': image_url,
                        'source': 'wikimedia',
                        'description': page.get('description', ''),
                        'author': 'Wikimedia Commons',
                        'width': 1000,
                        'height': 1000
                    })

            return results[:count]

        except Exception as e:
            print(f"⚠️  Erreur Wikimedia: {e}")
            return []

    def download_image(self, image_info: Dict, output_path: str) -> bool:
        """Télécharge une image depuis son URL"""
        try:
            response = self.session.get(image_info['url'], timeout=15)
            response.raise_for_status()

            # Vérifier la taille
            if len(response.content) > 10 * 1024 * 1024:  # 10 MB max
                return False

            # Vérifier le type MIME
            content_type = response.headers.get('content-type', '')
            if not any(img_type in content_type for img_type in ['image/jpeg', 'image/png', 'image/jpg']):
                return False

            # Sauvegarder l'image
            with open(output_path, 'wb') as f:
                f.write(response.content)

            # Vérifier que l'image est valide et adaptée aux enfants
            try:
                with Image.open(output_path) as img:
                    img.verify()

                    # Vérifications supplémentaires pour les enfants
                    if not self._is_child_friendly_image(output_path, image_info):
                        os.remove(output_path)
                        return False

                return True
            except Exception:
                os.remove(output_path)
                return False

        except Exception as e:
            print(f"      ⚠️  Erreur téléchargement: {e}")
            return False

    def _is_child_friendly_image(self, image_path: str, image_info: Dict) -> bool:
        """Vérifie si une image est adaptée aux enfants et privilégie les illustrations"""
        try:
            # Vérifier les métadonnées de l'image
            description = image_info.get('description', '').lower()
            author = image_info.get('author', '').lower()

            # Mots-clés à éviter pour les enfants
            inappropriate_keywords = [
                'adult', 'mature', 'sexy', 'nude', 'violence', 'blood', 'gore',
                'scary', 'horror', 'frightening', 'terrifying', 'dark', 'evil',
                'weapon', 'gun', 'knife', 'dangerous', 'aggressive', 'angry'
            ]

            # Vérifier la description et l'auteur
            text_to_check = f"{description} {author}"
            for keyword in inappropriate_keywords:
                if keyword in text_to_check:
                    return False

            # BONUS : Privilégier les illustrations et animations
            child_friendly_keywords = [
                'cartoon', 'illustration', 'drawing', 'animated', 'cute', 'friendly',
                'colorful', 'bright', 'happy', 'smiling', 'child', 'kid', 'educational'
            ]

            # Si l'image contient des mots-clés adaptés aux enfants, la privilégier
            has_child_keywords = any(keyword in text_to_check for keyword in child_friendly_keywords)

            # Vérifier la taille de l'image (éviter les images trop petites ou trop grandes)
            with Image.open(image_path) as img:
                width, height = img.size

                # Images trop petites (moins de 200x200)
                if width < 200 or height < 200:
                    return False

                # Images trop grandes (plus de 5000x5000) - peuvent être inappropriées
                if width > 5000 or height > 5000:
                    return False

            # Privilégier les images avec des mots-clés adaptés aux enfants
            return True

        except Exception:
            # En cas d'erreur, considérer l'image comme valide
            return True

    def download_for_element(self, nom_francais: str, mot_anglais: str, output_dir: str, images_par_element: int = 20) -> List[str]:
        """Télécharge des images pour un élément spécifique"""
        print(f"\n🔍 {nom_francais.upper()} ({mot_anglais})")
        print("=" * 60)

        # Calculer le nombre d'images par source (limité pour éviter la surcharge)
        num_sources = len(self.available_sources)
        # Limiter à 3 images par source maximum pour éviter trop d'images
        images_per_source = min(3, max(1, images_par_element // num_sources))

        # Collecter toutes les URLs d'images
        all_images = []

        # Unsplash
        print("📸 Unsplash...")
        unsplash_images = self.download_from_unsplash(mot_anglais, images_per_source)
        all_images.extend(unsplash_images)

        # Pexels
        print("📸 Pexels...")
        pexels_images = self.download_from_pexels(mot_anglais, images_per_source)
        all_images.extend(pexels_images)

        # Wikipedia (temporairement désactivé - problème 403)
        if 'wikipedia' in self.available_sources:
            print("📸 Wikipedia...")
            wikipedia_images = self.download_from_wikipedia(mot_anglais, images_per_source)
            all_images.extend(wikipedia_images)

        # Wikimedia Commons (temporairement désactivé - problème 403)
        if 'wikimedia' in self.available_sources:
            print("📸 Wikimedia Commons...")
            wikimedia_images = self.download_from_wikimedia(mot_anglais, images_per_source)
            all_images.extend(wikimedia_images)

        if not all_images:
            print(f"   ⚠️  Aucune image trouvée pour '{mot_anglais}'")
            return []

        print(f"📊 {len(all_images)} images trouvées au total")

        # Télécharger les images en parallèle
        downloaded_files = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_info = {}

            for i, image_info in enumerate(all_images[:images_par_element]):
                filename = f"{nom_francais}_{image_info['source']}_{i+1}.jpg"
                output_path = os.path.join(output_dir, filename)

                future = executor.submit(self.download_image, image_info, output_path)
                future_to_info[future] = (image_info, output_path)

            for future in as_completed(future_to_info):
                image_info, output_path = future_to_info[future]
                try:
                    success = future.result()
                    if success:
                        downloaded_files.append(os.path.basename(output_path))
                        print(f"   ✅ {image_info['source']} #{len(downloaded_files)}: {os.path.basename(output_path)} ({image_info.get('width', 0)}x{image_info.get('height', 0)} px)")
                except Exception as e:
                    print(f"   ❌ Erreur: {e}")

        return downloaded_files

    def download_for_theme(self, theme_name: str, images_par_element: int = 20) -> None:
        """Télécharge des images pour un thème complet"""
        config_path = f"themes/{theme_name}/config.json"
        if not os.path.exists(config_path):
            print(f"❌ Configuration non trouvée: {config_path}")
            return

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        photos_dir = f"themes/{theme_name}/photos"
        os.makedirs(photos_dir, exist_ok=True)

        print("=" * 80)
        print(f"🚀 TÉLÉCHARGEMENT UNIFIÉ - {config['titre'].upper()}")
        print("=" * 80)
        print(f"📊 {len(config['elements'])} éléments à traiter")
        print(f"📸 {images_par_element} images par élément")
        print(f"⚡ Parallélisme: {self.max_workers} téléchargements simultanés")
        print("=" * 80)

        # Vérifier les clés API
        check_api_keys()

        print(f"\n🚀 TÉLÉCHARGEMENT PARALLÈLE DE {len(config['elements'])} MOTS")
        print("=" * 80)

        all_downloaded = []
        start_time = time.time()

        for element in config['elements']:
            nom_francais = element['nom_francais']
            mot_anglais = element['mot_anglais']

            downloaded = self.download_for_element(nom_francais, mot_anglais, photos_dir, images_par_element)
            all_downloaded.extend(downloaded)

        # Conversion des images
        print(f"\n🔄 CONVERSION DES IMAGES")
        print("=" * 40)
        convertir_images_pour_docx(photos_dir)

        # Scoring CLIP si activé
        if self.enable_clip and self.clip_scorer:
            print(f"\n🧠 SCORING CLIP AUTOMATIQUE")
            print("=" * 40)
            self.clip_scorer.select_best_images_for_theme(theme_name)
        else:
            # Créer un fichier selection.json basique
            self.create_basic_selection(theme_name, config)

        # Statistiques finales
        end_time = time.time()
        total_time = end_time - start_time

        print(f"\n" + "=" * 80)
        print(f"✅ TÉLÉCHARGEMENT UNIFIÉ TERMINÉ !")
        print("=" * 80)
        print(f"⏱️  Temps total: {total_time:.1f} secondes")
        print(f"📊 {len(config['elements'])} éléments traités avec succès")
        print(f"📈 Vitesse: {len(all_downloaded)/total_time:.1f} images/seconde")
        print(f"💡 Prochaine étape:")
        print(f"   python generer_document.py {theme_name}")

    def create_basic_selection(self, theme_name: str, config: dict) -> None:
        """Crée un fichier selection.json basique sans CLIP"""
        photos_dir = f"themes/{theme_name}/photos"
        elements = []

        for element in config['elements']:
            nom_francais = element['nom_francais']
            nom_macedonien = element['nom_macedonien']

            # Trouver la première image disponible
            for file in os.listdir(photos_dir):
                if file.startswith(nom_francais) and file.endswith('.jpg'):
                    elements.append({
                        "nom_macedonien": nom_macedonien,
                        "nom_francais": nom_francais,
                        "image_selectionnee": file
                    })
                    break

        selection_config = {
            "theme": theme_name,
            "titre": config['titre'],
            "colonnes": config.get('colonnes', 3),
            "elements": elements
        }

        selection_path = f"themes/{theme_name}/selection.json"
        with open(selection_path, 'w', encoding='utf-8') as f:
            json.dump(selection_config, f, ensure_ascii=False, indent=2)

        print(f"✅ Configuration basique sauvegardée: {selection_path}")


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='Téléchargeur d\'images unifié avec scoring CLIP')
    parser.add_argument('theme', help='Nom du thème (ex: corps_humain, meteo)')
    parser.add_argument('--images', type=int, default=20, help='Images par élément (défaut: 20)')
    parser.add_argument('--no-clip', action='store_true', help='Désactiver le scoring CLIP')
    parser.add_argument('--workers', type=int, default=20, help='Nombre de workers parallèles (défaut: 20)')

    args = parser.parse_args()

    # Vérifier que le thème existe
    config_path = f"themes/{args.theme}/config.json"
    if not os.path.exists(config_path):
        print(f"❌ Thème '{args.theme}' non trouvé")
        print(f"💡 Créez d'abord le thème avec: python create_theme.py {args.theme}")
        return

    # Initialiser le téléchargeur
    downloader = UnifiedImageDownloader(
        max_workers=args.workers,
        enable_clip=not args.no_clip
    )

    # Lancer le téléchargement
    downloader.download_for_theme(args.theme, args.images)


if __name__ == "__main__":
    main()