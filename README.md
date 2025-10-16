# 📚 Générateur de documents éducatifs en macédonien

Créer des documents Word avec grilles d'images et noms en **macédonien cyrillique**, pour n'importe quel thème !

## 🚀 Quick Start

```bash
# Installer les dépendances
pip install -r requirements.txt

# 1. Créer un thème (ex: corps humain)
python create_theme.py corps_humain

# 2. Télécharger les images
python telecharger_images.py corps_humain

# 3. Générer le document Word
python generer_document.py corps_humain

# Résultat : themes/corps_humain/Делови на телото.docx
```

### ⚡ Performance

- **Multi-sources** : 4.3 secondes pour 10 mots × 6 images = 60 images
- **Parallélisme** : 20+ téléchargements simultanés
- **Sources variées** : Unsplash + Pexels + Wikipedia + Wikimedia Commons 🚀

## 🔑 Sources d'images disponibles

Le script utilise **4 sources** automatiquement :

- **🎯 Unsplash** : Photos modernes de haute qualité (priorité)
- **📸 Pexels** : Photos variées et professionnelles
- **📚 Wikipedia** : Images éducatives et anatomiques
- **🌐 Wikimedia Commons** : Images libres de droits

**✅ Clés API déjà intégrées** - Aucune configuration nécessaire !

## 🎯 Résultats obtenus

Le script multi-sources a téléchargé avec succès :

- **✅ 58 images** au total (10 mots × ~6 images en moyenne)
- **🎯 10 images sélectionnées** automatiquement pour le document Word
- **📂 48 images alternatives** disponibles pour choix manuel
- **⏱️ 4.3 secondes** de traitement total
- **📈 13.6 images/seconde** de vitesse de téléchargement

### 📁 Structure des images téléchargées

Pour chaque partie du corps, tu obtiens :

```
themes/corps_humain/photos/
├── oeil_unsplash_1.jpg           # 🏆 Image sélectionnée (haute qualité)
├── oeil_unsplash_2.jpg           # Alternative Unsplash
├── oeil_pexels_1.jpg             # Alternative Pexels
├── oeil_wikipedia_1.jpg          # Alternative Wikipedia
└── ...                           # Plus d'alternatives
```

Tu peux ensuite modifier `selection.json` pour choisir une autre image et régénérer le document !

## 📸 Comment ça marche ?

### 1. Télécharger des images depuis Wikimedia Commons

```python
from telecharger_images_wikimedia import WikimediaDownloader

d = WikimediaDownloader()
d.search_and_download(
    query="human eye close up",
    output_dir="themes/mon_theme/photos",
    count=3,
    filename_prefix="oeil"
)
```

**Avantages :**

- ✅ **Gratuit** - Pas de clé API
- ✅ **Libre de droits** - Domaine public / Creative Commons
- ✅ **Filtre automatique** - Seulement JPG/PNG < 10 MB

### 2. Configurer le thème

Créer `themes/mon_theme/selection.json` :

```json
{
  "theme": "mon_theme",
  "titre": "Мој наслов",
  "colonnes": 3,
  "elements": [
    {
      "nom_macedonien": "око",
      "nom_francais": "œil",
      "image_selectionnee": "oeil_1.jpg"
    }
  ]
}
```

### 3. Générer le document

```bash
python generer_document_theme.py mon_theme
```

## 🎨 Thèmes disponibles

### Corps Humain
```bash
python create_theme.py corps_humain
python telecharger_images.py corps_humain
python generer_document.py corps_humain
```
**Éléments :** глава (tête), око (œil), нос (nez), уста (bouche), рака (main), нога (jambe), срце (cœur), стомак (estomac), уво (oreille), коса (cheveux)

### Météo
```bash
python create_theme.py meteo
python telecharger_images.py meteo
python generer_document.py meteo
```
**Éléments :** сонце (soleil), облак (nuage), дожд (pluie), снег (neige), ветер (vent), бура (orage), молња (éclair), виножито (arc-en-ciel)

### Animaux
```bash
python create_theme.py animaux
python telecharger_images.py animaux
python generer_document.py animaux
```
**Éléments :** куче (chien), мачка (chat), птица (oiseau), риба (poisson), коњ (cheval), крава (vache), свиња (cochon), овца (mouton)

## 🎯 Bonnes pratiques

**Requêtes simples et descriptives :**

- ✅ `"human eye close up"` → photos naturelles
- ✅ `"human hand fingers"` → images claires
- ❌ `"anatomy medical diagram"` → trop médical

## 📁 Structure du projet

```
bac-a-sable-vilma/
├── create_theme.py                            # 🎨 Créateur de thèmes
├── telecharger_images.py                      # 📸 Téléchargeur multi-sources
├── generer_document.py                        # 📄 Générateur Word
├── telecharger_images_multi_sources.py        # 🔧 Module téléchargement
├── config_api.py                              # 🔑 Configuration APIs
├── convertir_images.py                        # 🔄 Conversion JPEG
├── requirements.txt                           # 📦 Dépendances Python
└── themes/
    └── {theme}/
        ├── config.json                        # Configuration du thème
        ├── photos/                            # Images téléchargées
        ├── selection.json                     # Images sélectionnées
        └── {Theme}.docx                       # Document généré
```

## 🚀 Système modulaire

Le système est maintenant **100% générique** et réutilisable :

| Script | Usage |
|--------|-------|
| `create_theme.py` | 🎨 Créer un nouveau thème |
| `telecharger_images.py` | 📸 Télécharger les images (4 sources) |
| `generer_document.py` | 📄 Générer le document Word |

**Performance :** 4.1 secondes pour 8 mots × 6 images = 48 images

## 🎯 Créer un nouveau thème

```bash
# Voir les thèmes disponibles
python create_theme.py list

# Créer un thème personnalisé
python create_theme.py mon_theme --titre "Mon Titre" --colonnes 4

# Ou utiliser un thème prédéfini
python create_theme.py meteo
```

### 📝 Structure d'un thème

Chaque thème a sa propre configuration dans `themes/{nom}/config.json` :

```json
{
  "theme": "meteo",
  "titre": "Времето",
  "colonnes": 4,
  "images_par_element": 6,
  "elements": [
    {
      "mot_anglais": "sun",
      "nom_francais": "soleil", 
      "nom_macedonien": "сонце"
    }
  ]
}
```

## 📝 Licence

Projet éducatif personnel. Images depuis Wikimedia Commons (domaine public / Creative Commons).
