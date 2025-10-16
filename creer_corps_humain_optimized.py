#!/usr/bin/env python3
"""
Script optimisé pour créer un document sur le corps humain
Téléchargements parallèles + conversion automatique + génération
"""

from telecharger_images_wikipedia_optimized import WikipediaImageDownloaderOptimized
from telecharger_images_wikimedia import WikimediaDownloader
from convertir_images import convertir_images_pour_docx
import json
import os
import subprocess
import time

def main():
    """Télécharge les images et crée la configuration - VERSION OPTIMISÉE"""
    
    start_time = time.time()
    
    # Configuration du thème
    theme_dir = "themes/corps_humain"
    photos_dir = os.path.join(theme_dir, "photos")
    
    # Créer le dossier si nécessaire
    os.makedirs(photos_dir, exist_ok=True)
    
    # Liste des parties du corps avec articles Wikipedia
    # Format: (article_wikipedia, prefix_fichier, nom_francais, nom_macedonien)
    parties_corps = [
        ("Human head", "tete", "tête", "глава"),
        ("Human eye", "oeil", "œil", "око"),
        ("Human nose", "nez", "nez", "нос"),
        ("Mouth", "bouche", "bouche", "уста"),
        ("Hand", "main", "main", "рака"),
        ("Human leg", "jambe", "jambe", "нога"),
        ("Heart", "coeur", "cœur", "срце"),
        ("Stomach", "estomac", "estomac", "стомак"),
        ("Ear", "oreille", "oreille", "уво"),
        ("Hair", "cheveux", "cheveux", "коса"),
    ]
    
    print("=" * 80)
    print("🚀 TÉLÉCHARGEMENT OPTIMISÉ - CORPS HUMAIN")
    print("=" * 80)
    print(f"📊 {len(parties_corps)} parties du corps à traiter")
    print(f"⚡ Parallélisme: {min(8, len(parties_corps))} téléchargements simultanés")
    print("=" * 80)
    
    # Télécharger les images en parallèle
    downloader = WikipediaImageDownloaderOptimized(max_workers=8)
    
    articles_data = [(article, prefix, french) for article, prefix, french, _ in parties_corps]
    results = downloader.download_multiple_articles_parallel(articles_data, photos_dir)
    
    # Fallback pour les articles sans images
    print("\n" + "=" * 80)
    print("🔄 FALLBACK SUR WIKIMEDIA COMMONS")
    print("=" * 80)
    
    wikimedia_downloader = WikimediaDownloader()
    fallback_queries = {
        "tête": "human face portrait",
        "œil": "human eye close up",
        "nez": "human nose close up", 
        "bouche": "human mouth lips",
        "main": "human hand",
        "jambe": "human leg",
        "cœur": "human heart",
        "estomac": "human stomach",
        "oreille": "human ear",
        "cheveux": "human hair"
    }
    
    for article, prefix, french, mac in parties_corps:
        if french not in results:
            print(f"\n⚠️  Fallback pour {french}...")
            wikimedia_downloader.search_and_download(
                query=fallback_queries[french],
                output_dir=photos_dir,
                count=1,
                filename_prefix=prefix
            )
            # Chercher le fichier téléchargé
            for ext in ['jpg', 'png']:
                possible_file = f"{prefix}_1.{ext}"
                if os.path.exists(os.path.join(photos_dir, possible_file)):
                    results[french] = possible_file
                    print(f"✅ {french}: {possible_file}")
                    break
    
    # Convertir les images en JPEG baseline compatible python-docx
    print("\n" + "=" * 80)
    print("🔄 CONVERSION DES IMAGES")
    print("=" * 80)
    
    conversions = convertir_images_pour_docx(photos_dir)
    
    # Créer la configuration finale
    elements = []
    for article, prefix, french, mac in parties_corps:
        image_file = results.get(french)
        
        if image_file:
            # Mettre à jour le nom si converti
            if image_file in conversions:
                image_file = conversions[image_file]
            
            elements.append({
                "nom_macedonien": mac,
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
        print(f"\n🚀 Performance: {len(parties_corps)/total_time:.1f} articles/seconde")
    else:
        print(f"\n❌ Erreur lors de la génération du document (code {result.returncode})")
        print(f"⏱️  Temps écoulé: {total_time:.1f} secondes")


if __name__ == "__main__":
    main()
