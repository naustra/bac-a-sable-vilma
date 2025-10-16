# 📚 Bac à Sable Vilma

Générateur de documents éducatifs en macédonien avec images depuis Wikimedia Commons.

## 🎯 Objectif

Créer des documents Word (.docx) avec :

- Grilles d'images
- Noms en **macédonien cyrillique**
- Images **libres de droits** depuis Wikimedia Commons

## 🚀 Quick Start

### Prérequis

```bash
# Installer les dépendances
pip install python-docx requests
```

### Créer un document "Corps Humain"

```bash
# Tout automatique : téléchargement + génération
python creer_corpus_humain_wikimedia.py

# Résultat : themes/corps_humain/Corps Humain.docx
```

## 📁 Structure

```
bac-a-sable-vilma/
├── telecharger_images_wikimedia.py      # Module de téléchargement Wikimedia
├── creer_corpus_humain_wikimedia.py     # Script automatique corps humain
├── generer_document_theme.py            # Générateur de .docx
├── themes/
│   └── corps_humain/
│       ├── photos/                      # Images téléchargées
│       ├── selection.json               # Configuration
│       └── Corps Humain.docx            # Document généré
```

## 🔧 Créer un nouveau thème

### 1. Télécharger les images

```python
from telecharger_images_wikimedia import WikimediaDownloader

d = WikimediaDownloader()
d.search_and_download(
    query="human eye anatomy",
    output_dir="themes/mon_theme/photos",
    count=3,
    filename_prefix="oeil"
)
```

### 2. Créer la configuration

Fichier `themes/mon_theme/selection.json` :

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

## 🌟 Avantages Wikimedia Commons

- ✅ **100% gratuit** - Pas de clé API
- ✅ **Libres de droits** - Domaine public / Creative Commons
- ✅ **Scientifique** - Images anatomiques, médicales, éducatives
- ✅ **Haute qualité** - Souvent issues d'ouvrages académiques

## 📖 Documentation complète

Voir `.cursor/rules/general.mdc` pour :

- Bonnes pratiques de requêtes
- Exemples par thème
- Workflow détaillé

## 🎨 Thèmes disponibles

- ✅ **Corps humain** (corps_humain) - 10 parties du corps

## 📝 Licence

Projet personnel éducatif. Images depuis Wikimedia Commons (domaine public/CC).
