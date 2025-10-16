#!/usr/bin/env python3
"""
Créateur de thèmes générique
Permet de créer facilement de nouveaux thèmes
"""

import json
import os
import argparse

def create_theme_config(theme_name: str, elements: list, titre: str = None, colonnes: int = 3, images_par_element: int = 6) -> str:
    """
    Crée la configuration d'un nouveau thème

    Args:
        theme_name: Nom du thème
        elements: Liste des éléments [{"mot_anglais": "eye", "nom_francais": "œil", "nom_macedonien": "око"}]
        titre: Titre du document (optionnel)
        colonnes: Nombre de colonnes dans le tableau
        images_par_element: Nombre d'images à télécharger par élément

    Returns:
        Chemin du fichier de configuration créé
    """
    # Créer le dossier du thème
    theme_dir = f"themes/{theme_name}"
    os.makedirs(theme_dir, exist_ok=True)
    os.makedirs(f"{theme_dir}/photos", exist_ok=True)

    # Configuration par défaut
    config = {
        "theme": theme_name,
        "titre": titre or theme_name.replace('_', ' ').title(),
        "colonnes": colonnes,
        "images_par_element": images_par_element,
        "max_workers": 20,
        "elements": elements
    }

    # Sauvegarder la configuration
    config_path = f"{theme_dir}/config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    return config_path

def create_corps_humain_theme():
    """Crée le thème corps humain"""
    elements = [
        {"mot_anglais": "head", "nom_francais": "tete", "nom_macedonien": "глава"},
        {"mot_anglais": "eye", "nom_francais": "oeil", "nom_macedonien": "око"},
        {"mot_anglais": "nose", "nom_francais": "nez", "nom_macedonien": "нос"},
        {"mot_anglais": "mouth", "nom_francais": "bouche", "nom_macedonien": "уста"},
        {"mot_anglais": "hand", "nom_francais": "main", "nom_macedonien": "рака"},
        {"mot_anglais": "leg", "nom_francais": "jambe", "nom_macedonien": "нога"},
        {"mot_anglais": "heart", "nom_francais": "coeur", "nom_macedonien": "срце"},
        {"mot_anglais": "stomach", "nom_francais": "estomac", "nom_macedonien": "стомак"},
        {"mot_anglais": "ear", "nom_francais": "oreille", "nom_macedonien": "уво"},
        {"mot_anglais": "hair", "nom_francais": "cheveux", "nom_macedonien": "коса"},
    ]

    return create_theme_config("corps_humain", elements, "Делови на телото")

def create_meteo_theme():
    """Crée le thème météo"""
    elements = [
        {"mot_anglais": "sun", "nom_francais": "soleil", "nom_macedonien": "сонце"},
        {"mot_anglais": "cloud", "nom_francais": "nuage", "nom_macedonien": "облак"},
        {"mot_anglais": "rain", "nom_francais": "pluie", "nom_macedonien": "дожд"},
        {"mot_anglais": "snow", "nom_francais": "neige", "nom_macedonien": "снег"},
        {"mot_anglais": "wind", "nom_francais": "vent", "nom_macedonien": "ветер"},
        {"mot_anglais": "storm", "nom_francais": "orage", "nom_macedonien": "бура"},
        {"mot_anglais": "lightning", "nom_francais": "eclair", "nom_macedonien": "молња"},
        {"mot_anglais": "rainbow", "nom_francais": "arc-en-ciel", "nom_macedonien": "виножито"},
    ]

    return create_theme_config("meteo", elements, "Времето", colonnes=4)

def create_animaux_theme():
    """Crée le thème animaux"""
    elements = [
        {"mot_anglais": "dog", "nom_francais": "chien", "nom_macedonien": "куче"},
        {"mot_anglais": "cat", "nom_francais": "chat", "nom_macedonien": "мачка"},
        {"mot_anglais": "bird", "nom_francais": "oiseau", "nom_macedonien": "птица"},
        {"mot_anglais": "fish", "nom_francais": "poisson", "nom_macedonien": "риба"},
        {"mot_anglais": "horse", "nom_francais": "cheval", "nom_macedonien": "коњ"},
        {"mot_anglais": "cow", "nom_francais": "vache", "nom_macedonien": "крава"},
        {"mot_anglais": "pig", "nom_francais": "cochon", "nom_macedonien": "свиња"},
        {"mot_anglais": "sheep", "nom_francais": "mouton", "nom_macedonien": "овца"},
    ]

    return create_theme_config("animaux", elements, "Животни")

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='Crée un nouveau thème')
    parser.add_argument('theme', help='Nom du thème ou "list" pour voir les thèmes disponibles')
    parser.add_argument('--titre', help='Titre du document')
    parser.add_argument('--colonnes', type=int, default=3, help='Nombre de colonnes (défaut: 3)')
    parser.add_argument('--images', type=int, default=6, help='Images par élément (défaut: 6)')

    args = parser.parse_args()

    if args.theme == "list":
        print("📋 Thèmes disponibles:")
        print("   - corps_humain : Parties du corps humain")
        print("   - meteo : Éléments météorologiques")
        print("   - animaux : Animaux domestiques et sauvages")
        print("\n💡 Utilisation:")
        print("   python create_theme.py corps_humain")
        print("   python create_theme.py meteo --colonnes 4")
        return

    try:
        # Thèmes prédéfinis
        if args.theme == "corps_humain":
            config_path = create_corps_humain_theme()
        elif args.theme == "meteo":
            config_path = create_meteo_theme()
        elif args.theme == "animaux":
            config_path = create_animaux_theme()
        else:
            print(f"❌ Thème '{args.theme}' non reconnu.")
            print("💡 Utilisez 'python create_theme.py list' pour voir les thèmes disponibles.")
            return

        print(f"✅ Thème '{args.theme}' créé avec succès !")
        print(f"📁 Configuration: {config_path}")
        print(f"\n💡 Prochaines étapes:")
        print(f"   1. python telecharger_images.py {args.theme}")
        print(f"   2. python generer_document.py {args.theme}")

    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()
