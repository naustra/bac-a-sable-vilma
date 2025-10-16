#!/usr/bin/env python3
"""
Script pour créer un document sur le corps humain
avec images depuis Wikipedia (image principale des articles)
"""

from telecharger_images_wikipedia import WikipediaImageDownloader
from telecharger_images_wikimedia import WikimediaDownloader
from convertir_images import convertir_images_pour_docx
import json
import os
import subprocess

def main():
    """Télécharge les images et crée la configuration"""

    # Configuration du thème
    theme_dir = "themes/corps_humain"
    photos_dir = os.path.join(theme_dir, "photos")

    # Créer le dossier si nécessaire
    os.makedirs(photos_dir, exist_ok=True)

    # Liste des parties du corps
    # Format: (macédonien, français, article_wikipedia, fallback_query_wikimedia)
    parties_corps = [
        ("глава", "tête", "Human head", "human face portrait"),
        ("око", "œil", "Human eye", "human eye close up"),
        ("нос", "nez", "Human nose", "human nose close up"),
        ("уста", "bouche", "Mouth", "human mouth lips"),
        ("рака", "main", "Hand", "human hand"),
        ("нога", "jambe", "Human leg", "human leg"),
        ("срце", "cœur", "Heart", "human heart"),
        ("стомак", "estomac", "Stomach", "human stomach"),
        ("уво", "oreille", "Ear", "human ear"),
        ("коса", "cheveux", "Hair", "human hair"),
    ]

    # Télécharger les images
    wiki_downloader = WikipediaImageDownloader()
    wikimedia_downloader = WikimediaDownloader()

    print("=" * 80)
    print("📚 TÉLÉCHARGEMENT DES IMAGES")
    print("=" * 80)

    elements = []

    for mac, fr, article, fallback_query in parties_corps:
        print(f"\n{'='*80}")
        print(f"🔍 {fr.upper()} ({mac})")
        print(f"{'='*80}")

        # Nom du fichier
        filename_base = fr.lower().replace('œ', 'oe')
        image_file = None

        # Essayer d'abord Wikipedia (image principale de l'article)
        output_path = os.path.join(photos_dir, f"{filename_base}_1.jpg")

        success, final_path = wiki_downloader.download_article_image(article, output_path)
        if success and final_path:
            image_file = os.path.basename(final_path)
        else:
            # Fallback sur Wikimedia Commons
            print(f"⚠️  Pas d'image principale, essai avec Wikimedia Commons...")
            wikimedia_downloader.search_and_download(
                query=fallback_query,
                output_dir=photos_dir,
                count=1,
                filename_prefix=filename_base
            )
            # Vérifier si une image a été téléchargée
            for ext in ['jpg', 'jpeg', 'png']:
                possible_file = f"{filename_base}_1.{ext}"
                if os.path.exists(os.path.join(photos_dir, possible_file)):
                    image_file = possible_file
                    break

        if image_file:
            elements.append({
                "nom_macedonien": mac,
                "nom_francais": fr,
                "image_selectionnee": image_file
            })
            print(f"✅ {fr}: {image_file}")
        else:
            print(f"❌ {fr}: Aucune image trouvée")

    # Convertir les images en JPEG baseline compatible python-docx
    print("\n" + "=" * 80)
    print("🔄 CONVERSION DES IMAGES")
    print("=" * 80)
    
    conversions = convertir_images_pour_docx(photos_dir)
    
    # Mettre à jour les noms de fichiers dans elements
    for element in elements:
        old_name = element["image_selectionnee"]
        if old_name in conversions:
            element["image_selectionnee"] = conversions[old_name]
            print(f"   {old_name} → {conversions[old_name]}")
    
    print(f"✅ {len(conversions)} images converties" if conversions else "✅ Images déjà au bon format")
    
    # Créer le fichier de configuration
    print("\n" + "=" * 80)
    print("📝 CRÉATION DU FICHIER DE CONFIGURATION")
    print("=" * 80)

    config = {
        "theme": "corps_humain",
        "titre": "Делови на телото",
        "colonnes": 3,
        "elements": elements
    }

    config_path = os.path.join(theme_dir, "selection.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"✅ Configuration sauvegardée: {config_path}")
    print(f"📊 {len(elements)} éléments configurés")

    # Générer le document
    print("\n" + "=" * 80)
    print("📄 GÉNÉRATION DU DOCUMENT WORD")
    print("=" * 80)

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
    else:
        print(f"\n❌ Erreur lors de la génération du document (code {result.returncode})")


if __name__ == "__main__":
    main()

