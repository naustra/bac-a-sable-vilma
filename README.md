# 📚 Générateur de documents éducatifs en macédonien

Créer des documents Word avec grilles d'images et noms en **macédonien cyrillique**, en utilisant des images gratuites depuis Wikimedia Commons.

## 🚀 Quick Start

```bash
# Installer les dépendances
pip install python-docx requests Pillow

# Générer un document "Corps Humain" (VERSION OPTIMISÉE - 4.8 secondes !)
python creer_corps_humain_optimized.py

# Résultat : themes/corps_humain/Corps Humain.docx
```

### ⚡ Performance
- **4.8 secondes** pour télécharger 10 parties du corps
- **3 images par partie** depuis Wikipedia
- **Parallélisme** : 8 téléchargements simultanés
- **2.1 articles/seconde** 🚀

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

| Script | Performance | Usage |
|--------|-------------|-------|
| `creer_corps_humain_optimized.py` | **4.8s** | ⚡ **Recommandé** - Ultra-rapide avec parallélisme |
| `creer_corpus_humain_wikimedia.py` | ~35s | 📚 Version classique avec Wikimedia Commons |

## 📝 Licence

Projet éducatif personnel. Images depuis Wikimedia Commons (domaine public / Creative Commons).
