#!/usr/bin/env python3
"""
Module de scoring d'images avec CLIP (OpenAI)
Utilise le modèle CLIP pour calculer la pertinence d'images par rapport à des requêtes textuelles
"""

import os
import json
import glob
from pathlib import Path
from typing import List, Dict, Tuple
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import warnings

# Supprimer les warnings de transformers
warnings.filterwarnings("ignore", category=UserWarning)

class CLIPImageScorer:
    """Scorer d'images utilisant le modèle CLIP d'OpenAI"""

    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        """
        Initialise le scorer CLIP

        Args:
            model_name: Nom du modèle CLIP à utiliser
        """
        print("Chargement du modele CLIP...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   Device: {self.device}")

        try:
            self.model = CLIPModel.from_pretrained(model_name)
            self.processor = CLIPProcessor.from_pretrained(model_name)
            self.model.to(self.device)
            print("SUCCES Modele CLIP charge avec succes")
        except Exception as e:
            print(f"ERREUR lors du chargement du modele CLIP: {e}")
            raise

    def score_image(self, image_path: str, text_query: str) -> float:
        """
        Calcule le score de similarité entre une image et une requête textuelle
        Privilégie des images de qualité professionnelle et non trash

        Args:
            image_path: Chemin vers l'image
            text_query: Requête textuelle (ex: "human eye close up")

        Returns:
            Score de similarité entre 0 et 1
        """
        try:
            # Charger et traiter l'image
            image = Image.open(image_path).convert("RGB")

            # Créer des requêtes pour privilégier des images de qualité
            text_queries = [
                # Priorité élevée : photos professionnelles de qualité
                f"professional photo of {text_query}",
                f"high quality image of {text_query}",
                f"clean {text_query}",
                # Priorité moyenne : images génériques mais de bonne qualité
                f"clear {text_query}",
                f"good {text_query}",
                # Priorité faible : générique
                text_query
            ]

            inputs = self.processor(
                text=text_queries,
                images=image,
                return_tensors="pt",
                padding=True
            )

            # Déplacer sur le device approprié
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Calculer les embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image

                # Ponderer les scores pour privilégier la qualité
                weights = torch.tensor([
                    1.3,  # professional photo (priorité élevée)
                    1.2,  # high quality image
                    1.1,  # clean
                    1.0,  # clear
                    1.0,  # good
                    0.9   # générique
                ]).to(self.device)

                # Appliquer les poids et prendre le score maximum
                weighted_scores = logits_per_image * weights
                max_score = torch.max(weighted_scores)

                # Normaliser entre 0 et 1 avec une fonction sigmoid
                normalized_score = 1 / (1 + torch.exp(-max_score / 10))

            return float(normalized_score.item())

        except Exception as e:
            print(f"ATTENTION Erreur lors du scoring de {image_path}: {e}")
            return 0.0


    def score_batch(self, image_paths: List[str], text_query: str) -> List[Dict]:
        """
        Score plusieurs images en batch pour plus d'efficacité

        Args:
            image_paths: Liste des chemins d'images
            text_query: Requête textuelle

        Returns:
            Liste de dictionnaires avec les scores
        """
        results = []

        # Traitement par batch pour optimiser la vitesse
        batch_size = 4  # Traiter 4 images à la fois

        for i in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[i:i + batch_size]
            batch_results = self._score_batch_optimized(batch_paths, text_query)
            results.extend(batch_results)

        return results

    def _score_batch_optimized(self, image_paths: List[str], text_query: str) -> List[Dict]:
        """
        Score un batch d'images de manière optimisée

        Args:
            image_paths: Liste des chemins d'images (max 4)
            text_query: Requête textuelle

        Returns:
            Liste de dictionnaires avec les scores
        """
        try:
            # Charger toutes les images du batch
            images = []
            valid_paths = []

            for image_path in image_paths:
                if not os.path.exists(image_path):
                    print(f"ATTENTION Image introuvable: {image_path}")
                    continue

                try:
                    image = Image.open(image_path).convert("RGB")
                    images.append(image)
                    valid_paths.append(image_path)
                except Exception as e:
                    print(f"ATTENTION Erreur chargement {image_path}: {e}")
                    continue

            if not images:
                return []

            # Créer des requêtes pour privilégier des images de qualité
            text_queries = [
                f"professional photo of {text_query}",
                f"high quality image of {text_query}",
                f"clear {text_query}",
                text_query
            ]

            # Traiter le batch complet
            inputs = self.processor(
                text=text_queries,
                images=images,
                return_tensors="pt",
                padding=True
            )

            # Déplacer sur le device approprié
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Calculer les embeddings pour tout le batch
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image

                # Ponderer les scores pour privilégier la qualité
                weights = torch.tensor([
                    1.3,  # professional photo
                    1.2,  # high quality image
                    1.1,  # clear
                    1.0   # générique
                ]).to(self.device)

                # Pour chaque image, calculer le score pondéré
                batch_scores = []
                for i in range(len(images)):
                    image_logits = logits_per_image[i]
                    weighted_scores = image_logits * weights
                    max_score = torch.max(weighted_scores)
                    # Normaliser entre 0 et 1 avec une fonction sigmoid
                    normalized_score = 1 / (1 + torch.exp(-max_score / 10))
                    batch_scores.append(float(normalized_score.item()))

            # Créer les résultats
            results = []
            for i, (image_path, score) in enumerate(zip(valid_paths, batch_scores)):
                results.append({
                    'path': image_path,
                    'filename': os.path.basename(image_path),
                    'score': score
                })

            return results

        except Exception as e:
            print(f"ATTENTION Erreur batch scoring: {e}")
            # Fallback vers scoring individuel
            results = []
            for image_path in image_paths:
                if os.path.exists(image_path):
                    score = self.score_image(image_path, text_query)
                    results.append({
                        'path': image_path,
                        'filename': os.path.basename(image_path),
                        'score': score
                    })
            return results

    def find_images_for_prefix(self, photos_dir: str, prefix: str) -> List[str]:
        """
        Trouve toutes les images correspondant à un préfixe

        Args:
            photos_dir: Dossier contenant les photos
            prefix: Préfixe des fichiers (ex: "oeil")

        Returns:
            Liste des chemins d'images trouvées
        """
        patterns = [
            os.path.join(photos_dir, f"{prefix}_*.jpg"),
            os.path.join(photos_dir, f"{prefix}_*.jpeg"),
            os.path.join(photos_dir, f"{prefix}_*.png")
        ]

        image_paths = []
        for pattern in patterns:
            image_paths.extend(glob.glob(pattern))

        return sorted(image_paths)

    def select_best_images_for_theme(self, theme_name: str) -> None:
        """
        Sélectionne les meilleures images pour un thème et génère selection.json

        Args:
            theme_name: Nom du thème (ex: "corps_humain", "meteo")
        """
        # Charger la configuration du thème
        config_path = f"themes/{theme_name}/config.json"
        if not os.path.exists(config_path):
            print(f"ERREUR Configuration non trouvee: {config_path}")
            return

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        photos_dir = f"themes/{theme_name}/photos"

        if not os.path.exists(photos_dir):
            print(f"ERREUR Dossier photos introuvable: {photos_dir}")
            return

        print("\n" + "=" * 80)
        print("SCORING DES IMAGES AVEC CLIP")
        print("=" * 80)
        print(f"Theme: METEO")
        print(f"{len(config['elements'])} elements a traiter")

        elements = []

        for element in config['elements']:
            nom_francais = element['nom_francais']
            nom_macedonien = element['nom_macedonien']
            mot_anglais = element['mot_anglais']

            print(f"\nScoring images pour {nom_francais}")
            print(f"   Requete: '{mot_anglais}'")

            # Trouver toutes les images pour ce mot
            image_paths = self.find_images_for_prefix(photos_dir, nom_francais)

            if not image_paths:
                print(f"   ATTENTION Aucune image trouvee pour '{nom_francais}'")
                continue

            print(f"   {len(image_paths)} images trouvees")

            # Scorer toutes les images
            scored_images = self.score_batch(image_paths, mot_anglais)

            if not scored_images:
                print(f"   ERREUR Aucune image scorable")
                continue

            # Trier par score décroissant
            scored_images.sort(key=lambda x: x['score'], reverse=True)

            # Afficher les scores
            for i, img in enumerate(scored_images):
                status = "MEILLEURE" if i == 0 else ""
                print(f"   {img['filename']} -> Score: {img['score']:.3f} {status}")

            # Sélectionner la meilleure
            best_image = scored_images[0]
            elements.append({
                "nom_macedonien": nom_macedonien,
                "nom_francais": nom_francais,
                "image_selectionnee": best_image['filename']
            })

            print(f"   SUCCES Selectionnee: {best_image['filename']}")

        # Générer le fichier selection.json
        final_config = {
            "theme": theme_name,
            "titre": config['titre'],
            "colonnes": config.get('colonnes', 3),
            "elements": elements
        }

        selection_path = f"themes/{theme_name}/selection.json"
        with open(selection_path, 'w', encoding='utf-8') as f:
            json.dump(final_config, f, ensure_ascii=False, indent=2)

        print(f"\nSUCCES Configuration sauvegardee: {selection_path}")
        print(f"{len(elements)} elements selectionnes")

        # Créer un fichier de rapport détaillé
        self.create_scoring_report(theme_name, config, elements)

    def create_scoring_report(self, theme_name: str, config: dict, selected_elements: list) -> None:
        """
        Crée un fichier de rapport détaillé avec tous les scores CLIP

        Args:
            theme_name: Nom du thème
            config: Configuration du thème
            selected_elements: Éléments sélectionnés
        """
        photos_dir = f"themes/{theme_name}/photos"
        report_path = f"themes/{theme_name}/scoring_report.json"

        report = {
            "theme": theme_name,
            "titre": config['titre'],
            "date_analyse": str(os.path.getctime(photos_dir)),
            "elements": []
        }

        print(f"\nCreation du rapport de scoring...")

        for element in config['elements']:
            nom_francais = element['nom_francais']
            nom_macedonien = element['nom_macedonien']
            mot_anglais = element['mot_anglais']

            # Trouver toutes les images pour ce mot
            image_paths = self.find_images_for_prefix(photos_dir, nom_francais)

            if not image_paths:
                continue

            # Scorer toutes les images
            scored_images = self.score_batch(image_paths, mot_anglais)
            scored_images.sort(key=lambda x: x['score'], reverse=True)

            # Trouver l'élément sélectionné
            selected_element = next((e for e in selected_elements if e['nom_francais'] == nom_francais), None)
            selected_image = selected_element['image_selectionnee'] if selected_element else None

            element_report = {
                "nom_francais": nom_francais,
                "nom_macedonien": nom_macedonien,
                "requete_anglais": mot_anglais,
                "image_selectionnee": selected_image,
                "total_images": len(scored_images),
                "scores": []
            }

            for img in scored_images:
                is_selected = img['filename'] == selected_image
                element_report["scores"].append({
                    "filename": img['filename'],
                    "score": round(img['score'], 4),
                    "selected": is_selected,
                    "rank": scored_images.index(img) + 1
                })

            report["elements"].append(element_report)

        # Sauvegarder le rapport
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"Rapport de scoring sauvegarde: {report_path}")


def main():
    """Fonction de test du module"""
    import argparse

    parser = argparse.ArgumentParser(description='Score les images d\'un thème avec CLIP')
    parser.add_argument('theme', help='Nom du thème (ex: corps_humain, meteo)')
    parser.add_argument('--test', action='store_true', help='Test avec une seule image')

    args = parser.parse_args()

    scorer = CLIPImageScorer()

    if args.test:
        # Test avec une image
        test_image = f"themes/{args.theme}/photos/oeil_1.jpg"
        if os.path.exists(test_image):
            score = scorer.score_image(test_image, "eye")
            print(f"Score de test: {score:.3f}")
        else:
            print("Image de test introuvable")
    else:
        # Scoring complet du thème
        scorer.select_best_images_for_theme(args.theme)


if __name__ == "__main__":
    main()
