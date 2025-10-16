#!/usr/bin/env python3
"""
Téléchargeur d'images générique multi-sources
Peut être utilisé pour n'importe quel thème
"""

from telecharger_images_multi_sources import MultiSourceImageDownloader
from convertir_images import convertir_images_pour_docx
from config_api import check_api_keys
import json
import os
import time
import argparse

def load_theme_config(theme_name: str) -> dict:
    """Charge la configuration d'un thème depuis le fichier JSON"""
    config_path = f"themes/{theme_name}/config.json"
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration non trouvée: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def download_images_for_theme(theme_name: str) -> dict:
    """
    Télécharge les images pour un thème donné
    
    Args:
        theme_name: Nom du thème (ex: "corps_humain", "meteo")
        
    Returns:
        Dictionnaire {nom_francais: meilleure_image}
    """
    # Charger la configuration du thème
    config = load_theme_config(theme_name)
    
    print("=" * 80)
    print(f"🚀 TÉLÉCHARGEMENT MULTI-SOURCES - {config['titre'].upper()}")
    print("=" * 80)
    print(f"📊 {len(config['elements'])} éléments à traiter")
    print(f"📸 {config['images_par_element']} images par élément")
    print(f"⚡ Parallélisme: {config.get('max_workers', 20)} téléchargements simultanés")
    print("=" * 80)
    
    # Vérifier les clés API
    print("🔑 Vérification des clés API...")
    api_ok = check_api_keys()
    if not api_ok:
        print("⚠️  Certaines sources ne seront pas disponibles, mais on continue...")
    
    # Configuration des dossiers
    theme_dir = f"themes/{theme_name}"
    photos_dir = os.path.join(theme_dir, "photos")
    os.makedirs(photos_dir, exist_ok=True)
    
    # Préparer les données pour le téléchargement
    words_data = []
    for element in config['elements']:
        words_data.append((
            element['mot_anglais'],
            element['nom_francais'],
            element['nom_macedonien']
        ))
    
    # Télécharger les images en parallèle
    downloader = MultiSourceImageDownloader(max_workers=config.get('max_workers', 20))
    results = downloader.download_multiple_words_parallel(words_data, photos_dir)
    
    # Convertir les images en JPEG baseline compatible python-docx
    print("\n" + "=" * 80)
    print("🔄 CONVERSION DES IMAGES")
    print("=" * 80)
    
    conversions = convertir_images_pour_docx(photos_dir)
    
    # Créer la configuration finale
    elements = []
    for element in config['elements']:
        french_name = element['nom_francais']
        image_file = results.get(french_name)
        
        if image_file:
            # Mettre à jour le nom si converti
            if image_file in conversions:
                image_file = conversions[image_file]
            
            elements.append({
                "nom_macedonien": element['nom_macedonien'],
                "nom_francais": french_name,
                "image_selectionnee": image_file
            })
        else:
            print(f"⚠️  {french_name}: Aucune image trouvée")
    
    # Sauvegarder la configuration finale
    print("\n" + "=" * 80)
    print("📝 CRÉATION DU FICHIER DE CONFIGURATION")
    print("=" * 80)
    
    final_config = {
        "theme": theme_name,
        "titre": config['titre'],
        "colonnes": config.get('colonnes', 3),
        "elements": elements
    }
    
    config_path = os.path.join(theme_dir, "selection.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(final_config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Configuration sauvegardée: {config_path}")
    print(f"📊 {len(elements)} éléments configurés")
    
    return results

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='Télécharge des images pour un thème donné')
    parser.add_argument('theme', help='Nom du thème (ex: corps_humain, meteo)')
    parser.add_argument('--dry-run', action='store_true', help='Affiche la configuration sans télécharger')
    
    args = parser.parse_args()
    
    try:
        if args.dry_run:
            config = load_theme_config(args.theme)
            print(f"📋 Configuration du thème '{args.theme}':")
            print(f"   Titre: {config['titre']}")
            print(f"   Éléments: {len(config['elements'])}")
            print(f"   Images par élément: {config.get('images_par_element', 6)}")
            return
        
        start_time = time.time()
        results = download_images_for_theme(args.theme)
        end_time = time.time()
        
        total_time = end_time - start_time
        total_images = sum(len(v) if isinstance(v, list) else 1 for v in results.values())
        
        print("\n" + "=" * 80)
        print("✅ TÉLÉCHARGEMENT TERMINÉ !")
        print("=" * 80)
        print(f"\n⏱️  Temps total: {total_time:.1f} secondes")
        print(f"📊 {len(results)} éléments traités avec succès")
        print(f"📈 Vitesse: {total_images/total_time:.1f} images/seconde")
        
        print(f"\n💡 Prochaine étape:")
        print(f"   python generer_document.py {args.theme}")
        
    except FileNotFoundError as e:
        print(f"❌ Erreur: {e}")
        print(f"💡 Créez d'abord la configuration avec:")
        print(f"   python create_theme.py {args.theme}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()
