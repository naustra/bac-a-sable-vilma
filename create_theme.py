#!/usr/bin/env python3
"""
Créateur de thèmes générique
Permet de créer facilement de nouveaux thèmes
"""

import json
import os
import argparse

def create_theme_config(theme_name: str, elements: list, titre: str = None, colonnes: int = 3, images_par_element: int = 20) -> str:
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
        {"mot_anglais": "fog", "nom_francais": "brouillard", "nom_macedonien": "магла"},
        {"mot_anglais": "mist", "nom_francais": "brume", "nom_macedonien": "измаглица"},
        {"mot_anglais": "hail", "nom_francais": "grêle", "nom_macedonien": "град"},
        {"mot_anglais": "thunder", "nom_francais": "tonnerre", "nom_macedonien": "грмотевица"},
        {"mot_anglais": "rainbow", "nom_francais": "arc-en-ciel", "nom_macedonien": "виножито"},
        {"mot_anglais": "temperature", "nom_francais": "température", "nom_macedonien": "температура"},
        {"mot_anglais": "hot", "nom_francais": "chaud", "nom_macedonien": "топло"},
        {"mot_anglais": "cold", "nom_francais": "froid", "nom_macedonien": "студено"},
        {"mot_anglais": "stormy", "nom_francais": "orageux", "nom_macedonien": "бурано"},
        {"mot_anglais": "sunny", "nom_francais": "ensoleillé", "nom_macedonien": "сончево"},
        {"mot_anglais": "cloudy", "nom_francais": "nuageux", "nom_macedonien": "облачно"},
    ]

    return create_theme_config("meteo", elements, "Времето", colonnes=3)

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

def create_salon_theme():
    """Crée le thème salon (living room) - Version enrichie avec éléments macédoniens"""
    elements = [
        # Meubles principaux
        {"mot_anglais": "sofa", "nom_francais": "canapé", "nom_macedonien": "кауч"},
        {"mot_anglais": "armchair", "nom_francais": "fauteuil", "nom_macedonien": "фотелја"},
        {"mot_anglais": "coffee table", "nom_francais": "table basse", "nom_macedonien": "мала маса"},
        {"mot_anglais": "side table", "nom_francais": "table d'appoint", "nom_macedonien": "странична маса"},
        {"mot_anglais": "bookshelf", "nom_francais": "bibliothèque", "nom_macedonien": "библиотека"},
        {"mot_anglais": "display cabinet", "nom_francais": "vitrine", "nom_macedonien": "витрина"},

        # Électronique et éclairage
        {"mot_anglais": "television", "nom_francais": "télévision", "nom_macedonien": "телевизор"},
        {"mot_anglais": "floor lamp", "nom_francais": "lampe sur pied", "nom_macedonien": "подна лампа"},
        {"mot_anglais": "table lamp", "nom_francais": "lampe de table", "nom_macedonien": "маса лампа"},
        {"mot_anglais": "ceiling light", "nom_francais": "plafonnier", "nom_macedonien": "таванска лампа"},

        # Textiles et décoration
        {"mot_anglais": "carpet", "nom_francais": "tapis", "nom_macedonien": "тепих"},
        {"mot_anglais": "traditional carpet", "nom_francais": "tapis traditionnel", "nom_macedonien": "традиционален тепих"},
        {"mot_anglais": "curtain", "nom_francais": "rideau", "nom_macedonien": "завеса"},
        {"mot_anglais": "embroidered curtain", "nom_francais": "rideau brodé", "nom_macedonien": "везена завеса"},
        {"mot_anglais": "cushion", "nom_francais": "coussin", "nom_macedonien": "перница"},
        {"mot_anglais": "throw blanket", "nom_francais": "plaid", "nom_macedonien": "покривка"},

        # Éléments traditionnels macédoniens
        {"mot_anglais": "fireplace", "nom_francais": "cheminée", "nom_macedonien": "камин"},
        {"mot_anglais": "icon", "nom_francais": "icône", "nom_macedonien": "икона"},
        {"mot_anglais": "family photo", "nom_francais": "photo de famille", "nom_macedonien": "семејна фотографија"},
        {"mot_anglais": "wall clock", "nom_francais": "horloge murale", "nom_macedonien": "ѕиден часовник"},
        {"mot_anglais": "traditional pottery", "nom_francais": "poterie traditionnelle", "nom_macedonien": "традиционална грнчарија"},
        {"mot_anglais": "Ohrid pottery", "nom_francais": "poterie d'Ohrid", "nom_macedonien": "охридска грнчарија"},

        # Objets décoratifs et artisanaux
        {"mot_anglais": "vase", "nom_francais": "vase", "nom_macedonien": "ваза"},
        {"mot_anglais": "wooden sculpture", "nom_francais": "sculpture en bois", "nom_macedonien": "дрвена скулптура"},
        {"mot_anglais": "silver filigree", "nom_francais": "filigrane d'argent", "nom_macedonien": "сребрен филигран"},
        {"mot_anglais": "wicker basket", "nom_francais": "panier en osier", "nom_macedonien": "кошница од врба"},
        {"mot_anglais": "copper tray", "nom_francais": "plateau en cuivre", "nom_macedonien": "бакарни тацни"},

        # Instruments de musique traditionnels
        {"mot_anglais": "tambura", "nom_francais": "tambura", "nom_macedonien": "тамбура"},
        {"mot_anglais": "kaval", "nom_francais": "kaval", "nom_macedonien": "кавал"},
        {"mot_anglais": "accordion", "nom_francais": "accordéon", "nom_macedonien": "хармоника"},

        # Plantes et nature
        {"mot_anglais": "indoor plant", "nom_francais": "plante d'intérieur", "nom_macedonien": "собна растение"},
        {"mot_anglais": "geranium", "nom_francais": "géranium", "nom_macedonien": "здравец"},
        {"mot_anglais": "flower pot", "nom_francais": "pot de fleurs", "nom_macedonien": "саксија за цвеќе"},

        # Boissons et service
        {"mot_anglais": "rakija bottle", "nom_francais": "bouteille de rakija", "nom_macedonien": "шише ракија"},
        {"mot_anglais": "coffee set", "nom_francais": "service à café", "nom_macedonien": "комплет за кафе"},
        {"mot_anglais": "tea set", "nom_francais": "service à thé", "nom_macedonien": "комплет за чај"},

        # Nappes et textiles brodés
        {"mot_anglais": "embroidered tablecloth", "nom_francais": "nappe brodée", "nom_macedonien": "везена чаршав"},
        {"mot_anglais": "doily", "nom_francais": "napperon", "nom_macedonien": "мал чаршав"},

        # Objets de rangement
        {"mot_anglais": "magazine rack", "nom_francais": "porte-revues", "nom_macedonien": "држи за списанија"},
        {"mot_anglais": "storage basket", "nom_francais": "panier de rangement", "nom_macedonien": "кошница за чување"},
    ]

    return create_theme_config("salon", elements, "Дневна соба", colonnes=4)

def create_toilette_theme():
    """Crée le thème toilette (bathroom)"""
    elements = [
        {"mot_anglais": "toilet", "nom_francais": "toilettes", "nom_macedonien": "тоалет"},
        {"mot_anglais": "sink", "nom_francais": "lavabo", "nom_macedonien": "лавоабо"},
        {"mot_anglais": "bathtub", "nom_francais": "baignoire", "nom_macedonien": "када"},
        {"mot_anglais": "shower", "nom_francais": "douche", "nom_macedonien": "туш"},
        {"mot_anglais": "towel", "nom_francais": "serviette", "nom_macedonien": "пешкир"},
        {"mot_anglais": "mirror", "nom_francais": "miroir", "nom_macedonien": "огледало"},
        {"mot_anglais": "soap", "nom_francais": "savon", "nom_macedonien": "сапун"},
        {"mot_anglais": "toothbrush", "nom_francais": "brosse à dents", "nom_macedonien": "четка за заби"},
        {"mot_anglais": "toothpaste", "nom_francais": "dentifrice", "nom_macedonien": "паста за заби"},
        {"mot_anglais": "shampoo", "nom_francais": "shampoing", "nom_macedonien": "шампон"},
        {"mot_anglais": "toilet paper", "nom_francais": "papier toilette", "nom_macedonien": "тоалетна хартија"},
        {"mot_anglais": "bath mat", "nom_francais": "tapis de bain", "nom_macedonien": "бањски тепих"},
    ]

    return create_theme_config("toilette", elements, "Тоалет")

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='Crée un nouveau thème')
    parser.add_argument('theme', help='Nom du thème ou "list" pour voir les thèmes disponibles')
    parser.add_argument('--titre', help='Titre du document')
    parser.add_argument('--colonnes', type=int, default=3, help='Nombre de colonnes (défaut: 3)')
    parser.add_argument('--images', type=int, default=20, help='Images par élément (défaut: 20)')

    args = parser.parse_args()

    if args.theme == "list":
        print("📋 Thèmes disponibles:")
        print("   - corps_humain : Parties du corps humain")
        print("   - meteo : Éléments météorologiques")
        print("   - animaux : Animaux domestiques et sauvages")
        print("   - salon : Salon et objets du salon")
        print("   - toilette : Toilette et objets de la salle de bain")
        print("\n💡 Utilisation:")
        print("   python create_theme.py corps_humain")
        print("   python create_theme.py meteo --colonnes 4")
        print("   python create_theme.py salon")
        print("   python create_theme.py toilette")
        return

    try:
        # Thèmes prédéfinis
        if args.theme == "corps_humain":
            config_path = create_corps_humain_theme()
        elif args.theme == "meteo":
            config_path = create_meteo_theme()
        elif args.theme == "animaux":
            config_path = create_animaux_theme()
        elif args.theme == "salon":
            config_path = create_salon_theme()
        elif args.theme == "toilette":
            config_path = create_toilette_theme()
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
