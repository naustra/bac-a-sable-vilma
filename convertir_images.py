#!/usr/bin/env python3
"""
Convertit toutes les images PNG/JPEG progressif en JPEG baseline
Compatible avec python-docx
"""

from PIL import Image
import os
from pathlib import Path

def convertir_images_pour_docx(photos_dir: str) -> dict:
    """
    Convertit toutes les images en JPEG baseline compatible python-docx
    
    Args:
        photos_dir: Dossier contenant les images
        
    Returns:
        Dictionnaire {ancien_nom: nouveau_nom} des fichiers renommés
    """
    conversions = {}
    
    for filename in os.listdir(photos_dir):
        if not filename.endswith(('.jpg', '.png', '.jpeg')):
            continue
            
        path = os.path.join(photos_dir, filename)
        
        try:
            img = Image.open(path)
            
            # Convertir en RGB si nécessaire (pour les PNG avec transparence)
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if 'A' in img.mode:
                    rgb_img.paste(img, mask=img.split()[-1])
                else:
                    rgb_img.paste(img)
                img = rgb_img
            
            # Déterminer le nouveau nom de fichier
            if filename.endswith('.png'):
                new_filename = filename.replace('.png', '.jpg')
                new_path = os.path.join(photos_dir, new_filename)
                conversions[filename] = new_filename
            else:
                new_filename = filename
                new_path = path
            
            # Sauvegarder en JPEG baseline (non-progressif, compatible python-docx)
            img.save(new_path, 'JPEG', quality=90, optimize=False, progressive=False)
            
            # Supprimer l'ancien fichier si renommé
            if filename != new_filename:
                os.remove(path)
            
        except Exception as e:
            print(f"⚠️  Erreur conversion {filename}: {e}")
    
    return conversions


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        photos_dir = sys.argv[1]
    else:
        photos_dir = "themes/corps_humain/photos"
    
    print(f"Conversion des images dans {photos_dir}...")
    conversions = convertir_images_pour_docx(photos_dir)
    
    if conversions:
        print(f"\n✅ {len(conversions)} fichiers convertis:")
        for old, new in conversions.items():
            print(f"   {old} → {new}")
    else:
        print("\n✅ Toutes les images sont déjà au bon format")

