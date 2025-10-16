#!/usr/bin/env python3
"""
Script principal pour créer un document corps humain avec images multi-sources
Version simplifiée utilisant les téléchargeurs existants
"""

from telecharger_images_multi_sources_simple import MultiSourceImageDownloaderSimple
from convertir_images import convertir_images_pour_docx
import json
import os
import subprocess
import time

def main():
    """Télécharge les images multi-sources et crée la configuration"""

    start_time = time.time()

    # Configuration du thème
    theme_dir = "themes/corps_humain"
    photos_dir = os.path.join(theme_dir, "photos")

    # Créer le dossier si nécessaire
    os.makedirs(photos_dir, exist_ok=True)

    # Liste des parties du corps avec mots-clés optimisés
    # Format: (mot_anglais, nom_français, nom_macédonien)
    parties_corps = [
        ("head", "tete", "глава"),
        ("eye", "oeil", "око"),
        ("nose", "nez", "нос"),
        ("mouth", "bouche", "уста"),
        ("hand", "main", "рака"),
        ("leg", "jambe", "нога"),
        ("heart", "coeur", "срце"),
        ("stomach", "estomac", "стомак"),
        ("ear", "oreille", "уво"),
        ("hair", "cheveux", "коса"),
    ]

    print("=" * 80)
    print("🚀 TÉLÉCHARGEMENT MULTI-SOURCES SIMPLIFIÉ - CORPS HUMAIN")
    print("=" * 80)
    print(f"📊 {len(parties_corps)} parties du corps à traiter")
    print(f"📸 10 images par partie = {len(parties_corps) * 10} images au total")
    print(f"⚡ Parallélisme: {min(10, len(parties_corps))} téléchargements simultanés")
    print("=" * 80)

    # Télécharger les images en parallèle
    downloader = MultiSourceImageDownloaderSimple(max_workers=10)
    results = downloader.download_multiple_words_parallel(parties_corps, photos_dir)

    # Convertir les images en JPEG baseline compatible python-docx
    print("\n" + "=" * 80)
    print("🔄 CONVERSION DES IMAGES")
    print("=" * 80)

    conversions = convertir_images_pour_docx(photos_dir)

    # Créer la configuration finale
    elements = []
    for word, french, macedonian in parties_corps:
        image_file = results.get(french)

        if image_file:
            # Mettre à jour le nom si converti
            if image_file in conversions:
                image_file = conversions[image_file]

            elements.append({
                "nom_macedonien": macedonian,
                "nom_francais": french,
                "image_selectionnee": image_file
            })
        else:
            print(f"⚠️  {french}: Aucune image trouvée")

    # Sauvegarder la configuration
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

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    end_time = time.time()
    total_time = end_time - start_time

    if result.returncode == 0:
        print("\n" + "=" * 80)
        print("✅ TERMINÉ AVEC SUCCÈS !")
        print("=" * 80)
        print(f"\n⏱️  Temps total: {total_time:.1f} secondes")
        print(f"📁 Dossier: {theme_dir}/")
        print(f"📸 Images: {photos_dir}/")
        print(f"📄 Document: {theme_dir}/Corps Humain.docx")

        # Statistiques
        total_images = len([f for f in os.listdir(photos_dir) if f.endswith(('.jpg', '.png'))])
        print(f"📊 {total_images} images téléchargées au total")
        print(f"🎯 {len(elements)} images sélectionnées pour le document")
        print(f"📂 {total_images - len(elements)} images alternatives disponibles")

        print(f"\n🚀 Performance: {len(parties_corps)/total_time:.1f} mots/seconde")
        print(f"📈 Vitesse: {total_images/total_time:.1f} images/seconde")

        print(f"\n💡 Tu peux maintenant:")
        print(f"   - Ouvrir le document Word généré")
        print(f"   - Comparer les images alternatives dans {photos_dir}/")
        print(f"   - Modifier selection.json pour changer les images")
        print(f"   - Régénérer le document avec python generer_document_theme.py corps_humain")

    else:
        print(f"\n❌ Erreur lors de la génération du document (code {result.returncode})")
        print(f"⏱️  Temps écoulé: {total_time:.1f} secondes")


if __name__ == "__main__":
    main()
