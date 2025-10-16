#!/usr/bin/env python3
"""
Script pour créer un document sur le corps humain
avec images téléchargées depuis Wikimedia Commons
"""

from telecharger_images_wikimedia import WikimediaDownloader
import json
import os

def main():
    """Télécharge les images et crée la configuration"""

    # Configuration du thème
    theme_dir = "themes/corps_humain"
    photos_dir = os.path.join(theme_dir, "photos")

    # Créer le dossier si nécessaire
    os.makedirs(photos_dir, exist_ok=True)

    # Liste des parties du corps à télécharger
    parties_corps = [
        {
            "nom_macedonien": "глава",
            "nom_francais": "tête",
            "requete_wikimedia": "head",
            "prefix": "tete"
        },
        {
            "nom_macedonien": "око",
            "nom_francais": "œil",
            "requete_wikimedia": "eye",
            "prefix": "oeil"
        },
        {
            "nom_macedonien": "нос",
            "nom_francais": "nez",
            "requete_wikimedia": "nose",
            "prefix": "nez"
        },
        {
            "nom_macedonien": "уста",
            "nom_francais": "bouche",
            "requete_wikimedia": "mouth",
            "prefix": "bouche"
        },
        {
            "nom_macedonien": "рака",
            "nom_francais": "main",
            "requete_wikimedia": "hand",
            "prefix": "main"
        },
        {
            "nom_macedonien": "нога",
            "nom_francais": "jambe",
            "requete_wikimedia": "leg",
            "prefix": "jambe"
        },
        {
            "nom_macedonien": "срце",
            "nom_francais": "cœur",
            "requete_wikimedia": "heart",
            "prefix": "coeur"
        },
        {
            "nom_macedonien": "стомак",
            "nom_francais": "estomac",
            "requete_wikimedia": "stomach",
            "prefix": "estomac"
        },
        {
            "nom_macedonien": "уво",
            "nom_francais": "oreille",
            "requete_wikimedia": "ear",
            "prefix": "oreille"
        },
        {
            "nom_macedonien": "коса",
            "nom_francais": "cheveux",
            "requete_wikimedia": "hair",
            "prefix": "cheveux"
        }
    ]

    # Télécharger les images
    downloader = WikimediaDownloader()

    print("=" * 80)
    print("📚 TÉLÉCHARGEMENT DES IMAGES DEPUIS WIKIMEDIA COMMONS")
    print("=" * 80)

    for partie in parties_corps:
        print(f"\n{'='*80}")
        print(f"🔍 {partie['nom_francais'].upper()} ({partie['nom_macedonien']})")
        print(f"{'='*80}")

        downloader.search_and_download(
            query=partie['requete_wikimedia'],
            output_dir=photos_dir,
            count=3,
            filename_prefix=partie['prefix']
        )

    # Créer le fichier selection.json
    print("\n" + "=" * 80)
    print("📝 CRÉATION DU FICHIER DE CONFIGURATION")
    print("=" * 80)

    # Lister les images téléchargées et sélectionner la première de chaque série
    elements = []
    for partie in parties_corps:
        # Chercher la première image de cette partie
        image_selectionnee = None
        for ext in ['jpg', 'jpeg', 'png']:
            possible_file = f"{partie['prefix']}_1.{ext}"
            if os.path.exists(os.path.join(photos_dir, possible_file)):
                image_selectionnee = possible_file
                break

        if image_selectionnee:
            elements.append({
                "nom_macedonien": partie["nom_macedonien"],
                "nom_francais": partie["nom_francais"],
                "image_selectionnee": image_selectionnee
            })
            print(f"✅ {partie['nom_francais']}: {image_selectionnee}")
        else:
            print(f"⚠️  {partie['nom_francais']}: Aucune image trouvée")

    # Créer le fichier de configuration
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

    # Générer le document
    print("\n" + "=" * 80)
    print("📄 GÉNÉRATION DU DOCUMENT WORD")
    print("=" * 80)

    import subprocess
    result = subprocess.run(
        ['python', 'generer_document_theme.py', 'corps_humain'],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    if result.returncode == 0:
        print("\n" + "=" * 80)
        print("✅ TERMINÉ !")
        print("=" * 80)
        print(f"\n📁 Dossier: {theme_dir}/")
        print(f"📸 Images: {photos_dir}/")
        print(f"📄 Document: {theme_dir}/Corps Humain.docx")
        print("\n💡 Tu peux maintenant uploader le .docx sur Google Drive")
    else:
        print(f"\n❌ Erreur lors de la génération du document (code {result.returncode})")


if __name__ == "__main__":
    main()

