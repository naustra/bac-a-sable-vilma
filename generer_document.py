#!/usr/bin/env python3
"""
Générateur de documents Word générique
Peut être utilisé pour n'importe quel thème
"""

import json
import os
import argparse
from docx import Document
from docx.shared import Inches
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH

def load_selection_config(theme_name: str) -> dict:
    """Charge la configuration de sélection d'un thème"""
    config_path = f"themes/{theme_name}/selection.json"
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration de sélection non trouvée: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_word_document(theme_name: str) -> str:
    """
    Crée un document Word pour un thème donné
    
    Args:
        theme_name: Nom du thème
        
    Returns:
        Chemin du document créé
    """
    # Charger la configuration
    config = load_selection_config(theme_name)
    
    print("=" * 80)
    print("📄 GÉNÉRATION DU DOCUMENT WORD")
    print("=" * 80)
    
    # Créer le document
    doc = Document()
    
    # Titre principal
    title = doc.add_heading(config['titre'], 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Espacement
    doc.add_paragraph()
    
    # Créer le tableau
    elements = config['elements']
    colonnes = config.get('colonnes', 3)
    lignes = (len(elements) + colonnes - 1) // colonnes  # Arrondi vers le haut
    
    table = doc.add_table(rows=lignes, cols=colonnes)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Remplir le tableau
    photos_dir = f"themes/{theme_name}/photos"
    
    for i, element in enumerate(elements):
        row = i // colonnes
        col = i % colonnes
        cell = table.cell(row, col)
        
        # Ajouter l'image
        image_path = os.path.join(photos_dir, element['image_selectionnee'])
        
        if os.path.exists(image_path):
            try:
                # Redimensionner l'image pour qu'elle rentre dans la cellule
                cell_paragraph = cell.paragraphs[0]
                run = cell_paragraph.runs[0] if cell_paragraph.runs else cell_paragraph.add_run()
                
                # Ajouter l'image
                picture = run.add_picture(image_path, width=Inches(1.5))
                
                # Centrer l'image
                cell_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                
                # Ajouter les textes
                cell_paragraph = cell.add_paragraph()
                cell_paragraph.add_run(element['nom_macedonien']).bold = True
                cell_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                
                cell_paragraph = cell.add_paragraph()
                cell_paragraph.add_run(f"({element['nom_francais']})").italic = True
                cell_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                
                print(f"   ✅ {element['nom_francais']}: {element['image_selectionnee']}")
                
            except Exception as e:
                print(f"   ❌ Erreur image {element['nom_francais']}: {e}")
                cell.text = f"{element['nom_macedonien']}\n({element['nom_francais']})"
        else:
            print(f"   ⚠️  Image manquante: {image_path}")
            cell.text = f"{element['nom_macedonien']}\n({element['nom_francais']})"
    
    # Sauvegarder le document
    output_path = f"themes/{theme_name}/{config['titre']}.docx"
    doc.save(output_path)
    
    print(f"\n✅ Document créé avec succès !")
    print(f"📄 Titre : {config['titre']}")
    print(f"📊 {len(elements)} éléments")
    print(f"📐 Tableau {lignes} × {colonnes}")
    print(f"📁 Emplacement : {os.path.abspath(output_path)}")
    
    return output_path

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='Génère un document Word pour un thème donné')
    parser.add_argument('theme', help='Nom du thème (ex: corps_humain, meteo)')
    parser.add_argument('--preview', action='store_true', help='Affiche la configuration sans générer')
    
    args = parser.parse_args()
    
    try:
        if args.preview:
            config = load_selection_config(args.theme)
            print(f"📋 Configuration du thème '{args.theme}':")
            print(f"   Titre: {config['titre']}")
            print(f"   Éléments: {len(config['elements'])}")
            print(f"   Colonnes: {config.get('colonnes', 3)}")
            return
        
        output_path = create_word_document(args.theme)
        
        print(f"\n💡 Le document est prêt : {output_path}")
        
    except FileNotFoundError as e:
        print(f"❌ Erreur: {e}")
        print(f"💡 Téléchargez d'abord les images avec:")
        print(f"   python telecharger_images.py {args.theme}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()
