# Relevé de Notes

**Gérez facilement les relevés de notes scolaires - 100% hors-ligne et gratuit**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-yellow)
![License](https://img.shields.io/badge/licence-Freeware-green)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

> Développé par **Maryson SEGLA** - Abomey-Calavi, Bénin

## 🎓 Présentation

Relevé de Notes est une application de bureau moderne et intuitive pour la saisie, le calcul et la gestion des bulletins scolaires. Conçue pour les enseignants, les directeurs et les parents.

- ✅ Calcul automatique des moyennes avec coefficients
- ✅ Gestion des mentions (Excellent, Très Bien, Bien...)
- ✅ Interface moderne et claire
- ✅ Fonctionne **sans internet** - toutes les données restent sur votre PC
- ✅ Export facile

## 📥 Téléchargement

Téléchargez la dernière version pour Windows :

**[📦 Télécharger ReleveDeNotes-Setup-v1.0.0.exe](../../releases/latest)**

> Ou allez dans l'onglet [Releases](../../releases)

## 🖼️ Captures d'écran

| Interface Principale | Saisie des notes |
|---|---|
| ![screenshot](docs/screenshot-main.png) | ![screenshot](docs/screenshot-edit.png) |

## 🚀 Installation

1. Téléchargez `ReleveDeNotes-Setup-v1.0.0.exe`
2. Double-cliquez dessus
3. Suivez l'assistant (Acceptez la licence)
4. Lancez depuis le menu Démarrer ou le raccourci Bureau

Aucune autre installation requise !

## 🛠️ Pour les développeurs

Si vous voulez lancer depuis le code source :

```bash
# Cloner
git clone https://github.com/seglamaryson/releve-de-notes.git
cd releve-de-notes

# Installer les dépendances
pip install PyQt6 Pillow

# Lancer
python releve_notes.py
```

Pour compiler l'installateur :

```bash
pyinstaller --onedir --windowed --name ReleveDeNotes --icon=icone.ico --add-data "icone.png;." --add-data "logo.png;." --add-data "icone.ico;." releve_notes.py
# Puis compiler avec Inno Setup
```

## 📁 Structure

```
releve-de-notes/
├── releve_notes.py      # Code principal
├── icone.ico             # Icône exe
├── icone.png             # Icône fenêtre
├── logo.png              # Logo application
├── LICENSE.txt           # Licence CLUF
├── setup.iss             # Script Inno Setup
└── README.md
```

## 📄 Licence

Ce logiciel est distribué en tant que **Freeware** sous Contrat de Licence Utilisateur Final (CLUF). Utilisation gratuite, personnelle et scolaire. Voir `LICENSE.txt`.


