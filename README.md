# 📚 Générateur de documents éducatifs en macédonien

Créer des documents Word avec grilles d'images et noms en **macédonien cyrillique**, en utilisant des images gratuites depuis Wikimedia Commons.

## 🚀 Quick Start

```bash
# Installer les dépendances
pip install python-docx requests Pillow

# Option 1: Multi-sources (RECOMMANDÉ - 10 images par mot !)
python creer_corps_humain_multi_sources_simple.py

# Option 2: Wikipedia optimisé (rapide)
python creer_corps_humain_optimized.py

# Résultat : themes/corps_humain/Corps Humain.docx
```

### ⚡ Performance

- **Multi-sources** : 20 secondes pour 10 mots × 10 images = 100 images
- **Wikipedia optimisé** : 4.8 secondes pour 10 mots × 3 images = 30 images
- **Parallélisme** : 10+ téléchargements simultanés
- **Sources variées** : Wikipedia + Wikimedia Commons (gratuits) 🚀

## 🔑 Configuration des APIs (Multi-sources)

Pour utiliser toutes les sources, obtenir les clés API gratuites :

### 1. Unsplash (photos modernes)

1. Aller sur https://unsplash.com/developers
2. Créer un compte développeur
3. Créer une nouvelle application
4. Copier la clé "Access Key"

### 2. Pexels (photos variées)

1. Aller sur https://pexels.com/api
2. Créer un compte
3. Générer une clé API
4. Copier la clé

### 3. Configuration

```bash
# Définir les variables d'environnement
export UNSPLASH_API_KEY='votre_cle_unsplash'
export PEXELS_API_KEY='votre_cle_pexels'

# Ou créer un fichier .env (optionnel)
echo "UNSPLASH_API_KEY=votre_cle" > .env
echo "PEXELS_API_KEY=votre_cle" >> .env
```

**Note** : Sans clés API, le script utilisera seulement Wikipedia et Wikimedia Commons (gratuits).

## 🎯 Résultats obtenus

Le script multi-sources a téléchargé avec succès :

- **✅ 65 images** au total (10 mots × ~6.5 images en moyenne)
- **🎯 10 images sélectionnées** automatiquement pour le document Word
- **📂 55 images alternatives** disponibles pour choix manuel
- **⏱️ 20 secondes** de traitement total
- **📈 3.2 images/seconde** de vitesse de téléchargement

### 📁 Structure des images téléchargées

Pour chaque partie du corps, tu obtiens :

```
themes/corps_humain/photos/
├── oeil_wikipedia_1.jpg          # Image principale Wikipedia
├── oeil_wikipedia_2.jpg          # Image secondaire Wikipedia
├── oeil_wikimedia_1.jpg          # Image Wikimedia Commons
├── oeil_wikimedia_2.jpg          # Autre image Wikimedia
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

## 🎨 Exemple : Corps Humain

Le script `creer_corpus_humain_wikimedia.py` fait tout automatiquement :

1. Télécharge 3 images par partie du corps depuis Wikimedia
2. Crée le fichier `selection.json`
3. Génère le document Word

**Parties du corps incluses :**

- глава (tête), око (œil), нос (nez), уста (bouche)
- рака (main), нога (jambe), срце (cœur), стомак (estomac)
- уво (oreille), коса (cheveux)

## 🎯 Bonnes pratiques

**Requêtes simples et descriptives :**

- ✅ `"human eye close up"` → photos naturelles
- ✅ `"human hand fingers"` → images claires
- ❌ `"anatomy medical diagram"` → trop médical

## 📁 Structure du projet

```
bac-a-sable-vilma/
├── telecharger_images_wikipedia_optimized.py  # ⚡ Téléchargeur parallèle
├── creer_corps_humain_optimized.py            # 🚀 Script ultra-rapide
├── convertir_images.py                        # 🔄 Conversion JPEG baseline
├── generer_document_theme.py                  # 📄 Générateur .docx
└── themes/
    └── {theme}/
        ├── photos/                            # Images téléchargées
        ├── selection.json                     # Configuration
        └── {Theme}.docx                       # Document généré
```

## 🚀 Versions disponibles

| Script                                       | Performance | Images/mot | Usage                                        |
| -------------------------------------------- | ----------- | ---------- | -------------------------------------------- |
| `creer_corps_humain_multi_sources_simple.py` | **20s**     | **10**     | 🎯 **RECOMMANDÉ** - 2 sources, choix maximum |
| `creer_corps_humain_optimized.py`            | **4.8s**    | 3          | ⚡ Rapide - Wikipedia seulement              |
| `creer_corpus_humain_wikimedia.py`           | ~35s        | 3          | 📚 Classique - Wikimedia Commons seulement   |

## 📝 Licence

Projet éducatif personnel. Images depuis Wikimedia Commons (domaine public / Creative Commons).
