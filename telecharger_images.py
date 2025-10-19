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
from config_api import API_URLS, API_HEADERS, API_KEYS, get_available_sources, check_api_keys
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
                print("Scoring CLIP active")
            except Exception as e:
                print(f"ATTENTION CLIP non disponible: {e}")
                self.enable_clip = False

        print(f"Sources disponibles: {', '.join(self.available_sources)}")

    def _make_child_friendly_query(self, query: str) -> str:
        """Retourne la requête telle quelle, sans modification"""
        return query

    def download_from_unsplash(self, query: str, count: int = 5) -> List[Dict]:
        """Télécharge des images depuis Unsplash"""
        if 'unsplash' not in self.available_sources:
            return []

        try:
            headers = API_HEADERS['unsplash'].copy()
            if not headers.get('Authorization'):
                return []

            # Utiliser la requête telle quelle
            query_to_use = self._make_child_friendly_query(query)

            params = {
                'query': query_to_use,
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
            print(f"ATTENTION Erreur Unsplash: {e}")
            return []

    def download_from_pexels(self, query: str, count: int = 5) -> List[Dict]:
        """Télécharge des images depuis Pexels"""
        if 'pexels' not in self.available_sources:
            return []

        try:
            headers = API_HEADERS['pexels'].copy()
            if not headers.get('Authorization'):
                return []

            # Utiliser la requête telle quelle
            query_to_use = self._make_child_friendly_query(query)

            params = {
                'query': query_to_use,
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
            print(f"ATTENTION Erreur Pexels: {e}")
            return []

    def download_from_wikipedia(self, query: str, count: int = 5) -> List[Dict]:
        """Télécharge des images depuis Wikipedia en utilisant l'API MediaWiki"""
        try:
            # Utiliser la requête telle quelle
            query_to_use = self._make_child_friendly_query(query)

            # Utiliser l'API MediaWiki standard
            api_url = "https://en.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': query_to_use,
                'srlimit': 3,
                'srnamespace': 0  # Articles seulement
            }

            headers = {
                'User-Agent': 'EducationalImageDownloader/2.0 (https://github.com/educational-tools; educational use) requests/2.31.0'
            }

            response = self.session.get(api_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            search_results = data.get('query', {}).get('search', [])

            for page in search_results:
                title = page['title']

                # Récupérer les images de cette page
                image_params = {
                    'action': 'query',
                    'format': 'json',
                    'titles': title,
                    'prop': 'images',
                    'imlimit': count
                }

                image_response = self.session.get(api_url, params=image_params, headers=headers, timeout=10)
                if image_response.status_code == 200:
                    image_data = image_response.json()
                    pages = image_data.get('query', {}).get('pages', {})

                    for page_id, page_info in pages.items():
                        images = page_info.get('images', [])

                        for img in images[:count]:
                            img_title = img['title']
                            if img_title.lower().endswith(('.jpg', '.jpeg', '.png')):
                                # Utiliser l'API pour obtenir l'URL directe de l'image
                                img_params = {
                                    'action': 'query',
                                    'format': 'json',
                                    'titles': img_title,
                                    'prop': 'imageinfo',
                                    'iiprop': 'url|size',
                                    'iiurlwidth': 640
                                }

                                img_response = self.session.get(api_url, params=img_params, headers=headers, timeout=10)
                                if img_response.status_code == 200:
                                    img_data = img_response.json()
                                    img_pages = img_data.get('query', {}).get('pages', {})

                                    for img_page_id, img_page_info in img_pages.items():
                                        if 'imageinfo' in img_page_info:
                                            imageinfo = img_page_info['imageinfo'][0]
                                            image_url = imageinfo.get('thumburl', imageinfo.get('url'))

                                            if image_url:
                                                results.append({
                                                    'url': image_url,
                                                    'source': 'wikipedia',
                                                    'description': f"Image from {title}",
                                                    'author': 'Wikipedia',
                                                    'width': 640,
                                                    'height': 640
                                                })

                                                if len(results) >= count:
                                                    break

                                if len(results) >= count:
                                    break

                if len(results) >= count:
                    break

            return results[:count]

        except Exception as e:
            print(f"ATTENTION Erreur Wikipedia: {e}")
            return []

    def download_from_wikimedia(self, query: str, count: int = 5) -> List[Dict]:
        """Télécharge des images depuis Wikimedia Commons avec l'API authentifiée"""
        try:
            query_to_use = self._make_child_friendly_query(query)

            # Essayer d'abord l'API Wikimedia authentifiée
            if 'wikimedia' in self.available_sources:
                try:
                    api_url = "https://api.wikimedia.org/core/v1/commons/search/file"
                    headers = {
                        'Authorization': f'Bearer {API_KEYS["wikimedia"]}',
                        'User-Agent': 'EducationalImageDownloader/2.0 (https://github.com/educational-tools; educational use) requests/2.31.0'
                    }

                    params = {
                        'q': query_to_use,
                        'limit': count,
                        'filetype': 'bitmap'
                    }

                    response = self.session.get(api_url, params=params, headers=headers, timeout=10)
                    response.raise_for_status()
                    data = response.json()

                    if 'pages' in data:
                        results = []
                        for page in data['pages']:
                            if 'thumbnail' in page and 'source' in page['thumbnail']:
                                # Utiliser l'URL de l'image complète
                                image_url = page['thumbnail']['source']
                                # Remplacer les paramètres de taille pour obtenir l'image complète
                                # Supprimer les paramètres de thumbnail tout en préservant le nom de fichier
                                if '/thumb/' in image_url:
                                    # Extraire le nom de fichier (dernière partie après le dernier '/')
                                    filename = image_url.split('/')[-1]
                                    # Remplacer /thumb/ par / et reconstruire l'URL sans les paramètres de taille
                                    base_url = image_url.replace('/thumb/', '/')
                                    # Supprimer les paramètres de taille (tout après le nom de fichier)
                                    if 'px-' in filename:
                                        filename = filename.split('px-')[-1]
                                    # Reconstruire l'URL complète
                                    image_url = '/'.join(base_url.split('/')[:-1]) + '/' + filename

                                results.append({
                                    'url': image_url,
                                    'width': page['thumbnail'].get('width', 0),
                                    'height': page['thumbnail'].get('height', 0),
                                    'source': 'wikimedia',
                                    'description': page.get('title', query_to_use),
                                    'author': 'Wikimedia Commons'
                                })

                        if results:
                            print(f"✅ Téléchargé {len(results)} images depuis Wikimedia Commons (API authentifiée)")
                            return results[:count]
                except Exception as e:
                    print(f"⚠️  API Wikimedia authentifiée échouée: {e}, tentative avec l'API standard")

            # Fallback vers l'API MediaWiki standard
            api_url = "https://commons.wikimedia.org/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': f'{query_to_use} filetype:bitmap',
                'srnamespace': 6,  # Namespace des fichiers
                'srlimit': count
            }

            headers = {
                'User-Agent': 'EducationalImageDownloader/2.0 (https://github.com/educational-tools; educational use) requests/2.31.0'
            }

            response = self.session.get(api_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            search_results = data.get('query', {}).get('search', [])

            for page in search_results:
                title = page['title']

                # Vérifier que c'est bien un fichier image
                if title.startswith('File:') and title.lower().endswith(('.jpg', '.jpeg', '.png')):
                    # Utiliser l'API pour obtenir l'URL directe de l'image
                    file_params = {
                        'action': 'query',
                        'format': 'json',
                        'titles': title,
                        'prop': 'imageinfo',
                        'iiprop': 'url|size',
                        'iiurlwidth': 640
                    }

                    file_response = self.session.get(api_url, params=file_params, headers=headers, timeout=10)
                    if file_response.status_code == 200:
                        file_data = file_response.json()
                        pages = file_data.get('query', {}).get('pages', {})

                        for page_id, page_info in pages.items():
                            if 'imageinfo' in page_info:
                                imageinfo = page_info['imageinfo'][0]
                                image_url = imageinfo.get('thumburl', imageinfo.get('url'))

                                if image_url:
                                    results.append({
                                        'url': image_url,
                                        'source': 'wikimedia',
                                        'description': f"Image from Wikimedia Commons: {title}",
                                        'author': 'Wikimedia Commons',
                                        'width': 640,
                                        'height': 640
                                    })

                                    if len(results) >= count:
                                        break

                if len(results) >= count:
                    break

            print(f"✅ Téléchargé {len(results)} images depuis Wikimedia Commons (API standard)")
            return results[:count]

        except Exception as e:
            print(f"❌ Erreur Wikimedia Commons: {e}")
            return []

    def download_from_pixabay(self, query: str, count: int = 5) -> List[Dict]:
        """Télécharge des images depuis Pixabay"""
        if 'pixabay' not in self.available_sources:
            return []

        try:
            # Utiliser la requête telle quelle
            query_to_use = self._make_child_friendly_query(query)

            params = {
                'key': API_KEYS['pixabay'],
                'q': query_to_use,
                'image_type': 'photo',
                'orientation': 'all',
                'category': 'all',
                'min_width': 200,
                'min_height': 200,
                'safesearch': 'true',
                'order': 'popular',
                'per_page': count
            }

            response = self.session.get(
                API_URLS['pixabay'],
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            results = []

            for hit in data.get('hits', []):
                if hit.get('webformatURL'):
                    results.append({
                        'url': hit['webformatURL'],
                        'source': 'pixabay',
                        'description': hit.get('tags', ''),
                        'author': hit.get('user', ''),
                        'width': hit.get('webformatWidth', 0),
                        'height': hit.get('webformatHeight', 0)
                    })

            return results

        except Exception as e:
            print(f"ATTENTION Erreur Pixabay: {e}")
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
            print(f"      ATTENTION Erreur telechargement: {e}")
            return False

    def _is_child_friendly_image(self, image_path: str, image_info: Dict) -> bool:
        """Vérifie si une image est appropriée en filtrant seulement le contenu inapproprié"""
        try:
            # Vérifier les métadonnées de l'image
            description = image_info.get('description', '').lower()
            author = image_info.get('author', '').lower()

            # Mots-clés à éviter (contenu inapproprié)
            inappropriate_keywords = [
                'adult', 'mature', 'sexy', 'nude', 'naked', 'violence', 'blood', 'gore',
                'scary', 'horror', 'frightening', 'terrifying', 'dark', 'evil',
                'weapon', 'gun', 'knife', 'dangerous', 'aggressive', 'angry'
            ]

            # Vérifier la description et l'auteur
            text_to_check = f"{description} {author}"
            for keyword in inappropriate_keywords:
                if keyword in text_to_check:
                    return False

            # Vérifier la taille de l'image (éviter les images trop petites)
            with Image.open(image_path) as img:
                width, height = img.size

                # Images trop petites (moins de 200x200)
                if width < 200 or height < 200:
                    return False

            # Accepter toutes les autres images
            return True

        except Exception:
            # En cas d'erreur, considérer l'image comme valide
            return True

    def download_for_element(self, nom_francais: str, mot_anglais: str, output_dir: str, images_par_element: int = 20) -> List[str]:
        """Télécharge des images pour un élément spécifique"""
        print(f"\n{nom_francais.upper()} ({mot_anglais})")
        print("=" * 60)

        # Calculer le nombre d'images par source (limité pour éviter la surcharge)
        num_sources = len(self.available_sources)
        # Limiter à 3 images par source maximum pour éviter trop d'images
        images_per_source = min(3, max(1, images_par_element // num_sources))

        # Collecter toutes les URLs d'images
        all_images = []

        # Unsplash
        print("Unsplash...")
        unsplash_images = self.download_from_unsplash(mot_anglais, images_per_source)
        all_images.extend(unsplash_images)

        # Pexels
        print("Pexels...")
        pexels_images = self.download_from_pexels(mot_anglais, images_per_source)
        all_images.extend(pexels_images)

        # Pixabay
        print("Pixabay...")
        pixabay_images = self.download_from_pixabay(mot_anglais, images_per_source)
        all_images.extend(pixabay_images)

        # Wikipedia (temporairement désactivé - problème 403)
        if 'wikipedia' in self.available_sources:
            print("Wikipedia...")
            wikipedia_images = self.download_from_wikipedia(mot_anglais, images_per_source)
            all_images.extend(wikipedia_images)

        # Wikimedia Commons (temporairement désactivé - problème 403)
        if 'wikimedia' in self.available_sources:
            print("Wikimedia Commons...")
            wikimedia_images = self.download_from_wikimedia(mot_anglais, images_per_source)
            all_images.extend(wikimedia_images)

        if not all_images:
            print(f"   ATTENTION Aucune image trouvee pour '{mot_anglais}'")
            return []

        print(f"{len(all_images)} images trouvees au total")

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
                        print(f"   OK {image_info['source']} #{len(downloaded_files)}: {os.path.basename(output_path)} ({image_info.get('width', 0)}x{image_info.get('height', 0)} px)")
                except Exception as e:
                    print(f"   ERREUR: {e}")

        return downloaded_files

    def download_for_theme(self, theme_name: str, images_par_element: int = 20) -> None:
        """Télécharge des images pour un thème complet"""
        config_path = f"themes/{theme_name}/config.json"
        if not os.path.exists(config_path):
            print(f"ERREUR Configuration non trouvee: {config_path}")
            return

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        photos_dir = f"themes/{theme_name}/photos"
        os.makedirs(photos_dir, exist_ok=True)

        print("=" * 80)
        print(f"TELECHARGEMENT UNIFIE - METEO")
        print("=" * 80)
        print(f"{len(config['elements'])} elements a traiter")
        print(f"{images_par_element} images par element")
        print(f"Parallelisme: {self.max_workers} telechargements simultanes")
        print("=" * 80)

        # Vérifier les clés API
        check_api_keys()

        print(f"\nTELECHARGEMENT PARALLELE DE {len(config['elements'])} MOTS")
        print("=" * 80)

        all_downloaded = []
        start_time = time.time()

        for element in config['elements']:
            nom_francais = element['nom_francais']
            mot_anglais = element['mot_anglais']

            downloaded = self.download_for_element(nom_francais, mot_anglais, photos_dir, images_par_element)
            all_downloaded.extend(downloaded)

        # Conversion des images
        print(f"\nCONVERSION DES IMAGES")
        print("=" * 40)
        convertir_images_pour_docx(photos_dir)

        # Scoring CLIP si activé
        if self.enable_clip and self.clip_scorer:
            print(f"\nSCORING CLIP AUTOMATIQUE")
            print("=" * 40)
            self.clip_scorer.select_best_images_for_theme(theme_name)
        else:
            # Créer un fichier selection.json basique
            self.create_basic_selection(theme_name, config)

        # Statistiques finales
        end_time = time.time()
        total_time = end_time - start_time

        print(f"\n" + "=" * 80)
        print(f"SUCCES TELECHARGEMENT UNIFIE TERMINE !")
        print("=" * 80)
        print(f"Temps total: {total_time:.1f} secondes")
        print(f"{len(config['elements'])} elements traites avec succes")
        print(f"Vitesse: {len(all_downloaded)/total_time:.1f} images/seconde")
        print(f"Prochaine etape:")
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

        print(f"SUCCES Configuration basique sauvegardee: {selection_path}")


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
        print(f"ERREUR Theme '{args.theme}' non trouve")
        print(f"Creez d'abord le theme avec: python create_theme.py {args.theme}")
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