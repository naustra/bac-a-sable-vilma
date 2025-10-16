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
        print("🔄 Chargement du modèle CLIP...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   📱 Device: {self.device}")

        try:
            self.model = CLIPModel.from_pretrained(model_name)
            self.processor = CLIPProcessor.from_pretrained(model_name)
            self.model.to(self.device)
            print("✅ Modèle CLIP chargé avec succès")
        except Exception as e:
            print(f"❌ Erreur lors du chargement du modèle CLIP: {e}")
            raise

    def score_image(self, image_path: str, text_query: str) -> float:
        """
        Calcule le score de similarité entre une image et une requête textuelle

        Args:
            image_path: Chemin vers l'image
            text_query: Requête textuelle (ex: "human eye close up")

        Returns:
            Score de similarité entre 0 et 1
        """
        try:
            # Charger et traiter l'image
            image = Image.open(image_path).convert("RGB")
            inputs = self.processor(
                text=[text_query],
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
                probs = logits_per_image.softmax(dim=-1)

            return float(probs[0][0])

        except Exception as e:
            print(f"⚠️  Erreur lors du scoring de {image_path}: {e}")
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

        for image_path in image_paths:
            if not os.path.exists(image_path):
                print(f"⚠️  Image introuvable: {image_path}")
                continue

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

    def select_best_images(self, theme_dir: str, parties_corps_config: List[Dict]) -> None:
        """
        Sélectionne les meilleures images pour chaque partie du corps et génère selection.json

        Args:
            theme_dir: Dossier du thème (ex: "themes/corps_humain")
            parties_corps_config: Configuration des parties du corps
        """
        photos_dir = os.path.join(theme_dir, "photos")

        if not os.path.exists(photos_dir):
            print(f"❌ Dossier photos introuvable: {photos_dir}")
            return

        print("\n" + "=" * 80)
        print("🎯 SCORING DES IMAGES AVEC CLIP")
        print("=" * 80)

        elements = []

        for partie in parties_corps_config:
            nom_francais = partie['nom_francais']
            nom_macedonien = partie['nom_macedonien']
            requete = partie['requete_wikimedia']
            prefix = partie['prefix']

            print(f"\n🔍 Scoring images pour {nom_francais} ({nom_macedonien})")
            print(f"   📝 Requête: '{requete}'")

            # Trouver toutes les images pour ce préfixe
            image_paths = self.find_images_for_prefix(photos_dir, prefix)

            if not image_paths:
                print(f"   ⚠️  Aucune image trouvée pour le préfixe '{prefix}'")
                continue

            print(f"   📸 {len(image_paths)} images trouvées")

            # Scorer toutes les images
            scored_images = self.score_batch(image_paths, requete)

            if not scored_images:
                print(f"   ❌ Aucune image scorable")
                continue

            # Trier par score décroissant
            scored_images.sort(key=lambda x: x['score'], reverse=True)

            # Afficher les scores
            for i, img in enumerate(scored_images):
                status = "⭐ MEILLEURE" if i == 0 else ""
                print(f"   📸 {img['filename']} → Score: {img['score']:.3f} {status}")

            # Sélectionner la meilleure
            best_image = scored_images[0]
            elements.append({
                "nom_macedonien": nom_macedonien,
                "nom_francais": nom_francais,
                "image_selectionnee": best_image['filename']
            })

            print(f"   ✅ Sélectionnée: {best_image['filename']}")

        # Générer le fichier selection.json
        config = {
            "theme": "corps_humain",
            "titre": "Делови на телото - Македонски",
            "colonnes": 3,
            "elements": elements
        }

        config_path = os.path.join(theme_dir, "selection.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Configuration sauvegardée: {config_path}")
        print(f"📊 {len(elements)} éléments sélectionnés")


def main():
    """Fonction de test du module"""
    scorer = CLIPImageScorer()

    # Test avec une image
    test_image = "themes/corps_humain/photos/oeil_1.jpg"
    if os.path.exists(test_image):
        score = scorer.score_image(test_image, "human eye close up")
        print(f"Score de test: {score:.3f}")
    else:
        print("Image de test introuvable")


if __name__ == "__main__":
    main()
