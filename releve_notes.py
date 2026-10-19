import csv
import ctypes
from datetime import date
import html
import json
from pathlib import Path
from string import Template
import sys

from PIL import Image
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplashScreen,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# ============================================================
# INITIALISATION ET DÉFINITION DE DOSSIER
# ============================================================

NOM_APP = "Relevé de Notes"

if getattr(sys, "frozen", False):
    DOSSIER = Path(sys._MEIPASS)
    DOSSIER_DONNEES = Path.home() / NOM_APP
else:
    DOSSIER = Path(__file__).resolve().parent
    DOSSIER_DONNEES = DOSSIER / NOM_APP

DOSSIER_DONNEES.mkdir(parents=True, exist_ok=True)
FICHIER_NOTES = DOSSIER_DONNEES / "notes.json"

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# CONFIGURATION STYLES (QSS) PAR DÉFAUT (SOMBRE)
POLICE = "Segoe UI"
FOND = "#0b0d10"
CARTE = "#14171c"
CARTE_2 = "#1b2027"
CHAMP = "#1a1e24"
BORDURE = "#2c333d"
TEXTE = "#f1f3f5"
TEXTE_DOUX = "#a5adb8"
ACCENT = "#3b82f6"
ACCENT_HOVER = "#2563eb"
VERT = "#35c97a"
ROUGE = "#ff6b6b"

STYLESHEET_BASE = f"""
QMainWindow {{
    background-color: {FOND};
}}
QWidget {{
    color: {TEXTE};
    font-family: "{POLICE}";
    font-size: 13px;
}}
QLabel {{
    border: none !important;
    background: transparent !important;
    outline: none !important;
}}
QFrame {{
    border: none;
}}
QFrame#carte_principale {{
    background-color: {CARTE};
    border: 1px solid {BORDURE};
    border-radius: 12px;
}}
QFrame#carte_entete {{
    background-color: #111820;
    border: 1px solid #263442;
    border-radius: 14px;
}}
QFrame#bloc_moyenne {{
    background-color: {CARTE};
    border: 1px solid #2b4258;
    border-radius: 12px;
}}
QFrame#stat_card {{
    background-color: {CARTE_2};
    border: 1px solid {BORDURE};
    border-radius: 10px;
}}
QLineEdit {{
    background-color: {CHAMP};
    border: 1px solid {BORDURE};
    border-radius: 8px;
    padding: 8px 12px;
    color: {TEXTE};
    font-size: 13px;
}}
QLineEdit:focus {{
    border: 1px solid {ACCENT};
}}
QPushButton {{
    background-color: {CARTE};
    border: 1px solid {BORDURE};
    border-radius: 8px;
    padding: 10px 20px;
    color: {TEXTE};
    font-weight: bold;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: #252b33;
}}
QPushButton#btn_principal {{
    background-color: {ACCENT};
    border: none;
    color: white;
}}
QPushButton#btn_principal:hover {{
    background-color: {ACCENT_HOVER};
}}
QTableWidget {{
    background-color: {CARTE};
    border: 1px solid {BORDURE};
    border-radius: 10px;
    gridline-color: {BORDURE};
    font-size: 13px;
}}
QHeaderView::section {{
    background-color: #20262d;
    color: {TEXTE};
    font-weight: bold;
    padding: 8px;
    border: 1px solid {BORDURE};
    font-size: 12px;
}}
QDialog {{
    background-color: {FOND};
}}

/* SCROLLBAR STYLE WINDOWS */
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background: #4a525d;
    min-height: 30px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical:hover {{
    background: #687382;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
    height: 0px;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 0px;
}}
QScrollBar::handle:horizontal {{
    background: #4a525d;
    min-width: 30px;
    border-radius: 5px;
}}
QScrollBar::handle:horizontal:hover {{
    background: #687382;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none;
    width: 0px;
}}
"""

# ============================================================
# TRADUCTIONS ET CONSTANTES METIER
# ============================================================

TRADUCTIONS = {
    "fr": {
        "app_titre": "RELEVÉ DE NOTES",
        "fenetre_titre": "Relevé de Notes",
        "infos_eleve": "Informations de l'élève",
        "nom": "NOM",
        "prenom": "PRÉNOM(S)",
        "matricule": "MATRICULE",
        "classe": "CLASSE",
        "filiere": "FILIÈRE",
        "annee": "ANNÉE SCOLAIRE",
        "moyenne_generale": "MOYENNE GÉNÉRALE",
        "vue_ensemble": "Vue d'ensemble",
        "matieres_notees": "MATIÈRES NOTÉES",
        "total_points": "TOTAL DES POINTS",
        "meilleure_matiere": "MEILLEURE MATIÈRE",
        "a_renforcer": "À RENFORCER",
        "resultats": "Résultats par matière",
        "aide_cellule": "Double-cliquez directement sur une cellule pour la modifier.",
        "semestre_libelle": "Semestre :",
        "semestre_1": "1er Semestre",
        "semestre_2": "2ème Semestre",
        "parametres": "⚙ Paramètres",
        "pret": "Prêt.",
        "param_titre": "Paramètres de l'application",
        "param_section_opt": "Paramètres et Options",
        "langue_libelle": "Langue d'affichage :",
        "theme_libelle": "Arrière-plan / Thème :",
        "theme_sombre": "Sombre (Dark)",
        "theme_clair": "Clair (Light)",
        "param_section_actions": "Actions et Exports",
        "btn_html": "Relevé imprimable (HTML)",
        "btn_csv": "Exporter sous Excel (CSV)",
        "btn_reset": "Effacer toutes les notes",
        "btn_apropos": "ℹ️ À propos",
        "aucune_note": "Aucune note",
        "total_libelle": "Total (matières notées)",
        "entetes": ["Coef", "Matière", "Interro 1", "Interro 2", "Interro 3", "Interro 4", "Moy. interros", "Devoir 1", "Devoir 2", "Devoir 3", "Moyenne", "Moy. coef."],
        "mentions": {
            "tb": "Très bien",
            "b": "Bien",
            "ab": "Assez bien",
            "p": "Passable",
            "i": "Insuffisant",
            "aucune": "Aucune note"
        }
    },
    "en": {
        "app_titre": "GRADE REPORT",
        "fenetre_titre": "Grade Report",
        "infos_eleve": "Student Information",
        "nom": "LAST NAME",
        "prenom": "FIRST NAME(S)",
        "matricule": "ID NUMBER",
        "classe": "CLASS",
        "filiere": "MAJOR / TRACK",
        "annee": "SCHOOL YEAR",
        "moyenne_generale": "OVERALL AVERAGE",
        "vue_ensemble": "Overview",
        "matieres_notees": "GRADED SUBJECTS",
        "total_points": "TOTAL POINTS",
        "meilleure_matiere": "BEST SUBJECT",
        "a_renforcer": "TO IMPROVE",
        "resultats": "Results by Subject",
        "aide_cellule": "Double-click directly on a cell to edit it.",
        "semestre_libelle": "Semester:",
        "semestre_1": "1st Semester",
        "semestre_2": "2nd Semester",
        "parametres": "⚙ Settings",
        "pret": "Ready.",
        "param_titre": "Application Settings",
        "param_section_opt": "Settings and Options",
        "langue_libelle": "Display Language:",
        "theme_libelle": "Background / Theme:",
        "theme_sombre": "Dark",
        "theme_clair": "Light",
        "param_section_actions": "Actions and Exports",
        "btn_html": "Printable Report (HTML)",
        "btn_csv": "Export to Excel (CSV)",
        "btn_reset": "Clear all grades",
        "btn_apropos": "ℹ️ About",
        "aucune_note": "No grades",
        "total_libelle": "Total (graded subjects)",
        "entetes": ["Coef", "Subject", "Quiz 1", "Quiz 2", "Quiz 3", "Quiz 4", "Quiz Avg.", "Test 1", "Test 2", "Test 3", "Average", "Weighted Avg."],
        "mentions": {
            "tb": "Excellent",
            "b": "Very Good",
            "ab": "Good",
            "p": "Pass",
            "i": "Fail",
            "aucune": "No grades"
        }
    }
}

MATIERES_DEFAUT = [
    ("Français", "fr", 3),
    ("Anglais", "an", 2),
    ("Mathématiques", "ma", 4),
    ("EST", "es", 5),
    ("PCT", "pc", 4),
    ("Dessin", "de", 4),
    ("Technologie", "te", 2),
    ("Législation", "le", 1),
    ("Philosophie", "ph", 1),
    ("TP", "tp", 6),
    ("MEL", "me", 5),
    ("Électrotechnique", "el", 2),
    ("EPS", "ep", 1),
]

MATIERES = list(MATIERES_DEFAUT)

NB_INTERROS = 4
NB_DEVOIRS = 3
NOTE_MAX = 20
COEF_MAX = 10
SEUIL = 10

SEMESTRES = ["S1", "S2"]
SEMESTRE_LABELS = {"S1": "1er Semestre", "S2": "2ème Semestre"}

COLONNES_CLES = ["coef", "matiere", "i1", "i2", "i3", "i4", "mi", "d1", "d2", "d3", "moy", "mc"]
LARGEURS_COLONNES = [65, 180, 75, 75, 75, 75, 110, 75, 75, 75, 90, 100]
EDITABLES = {"coef", "i1", "i2", "i3", "i4", "d1", "d2", "d3"}

MODELE_HTML = Template("""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<title>Relevé de notes - $eleve</title>
<style>
* { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: "Segoe UI", Arial, sans-serif; color: #202020; margin: 30px; background: #fff; }
header { border: 1px solid #e5e5e5; background: #fdfdfd; padding: 24px; display: flex;
        justify-content: space-between; align-items: center; border-radius: 8px; }
header h1 { margin: 0 0 4px; font-size: 24px; color: #0067b8; }
header p { margin: 2px 0; color: #5f5f5f; }
header .moy { text-align: right; }
header .moy b { display: block; font-size: 36px; color: #202020; }
table { border-collapse: collapse; width: 100%; margin-top: 25px; font-size: 13px; }
th { background: #f5f5f5; color: #202020; padding: 10px 4px; border: 1px solid #e5e5e5; font-weight: bold; }
td { border: 1px solid #e5e5e5; padding: 8px 4px; text-align: center; }
td:nth-child(2) { text-align: left; padding-left: 8px; }
tr:nth-child(even) td { background: #fafafa; }
tr.faible td { color: #a80000; background: #fff5f5 !important; }
tr.total td { background: #f3f3f3; color: #202020; font-weight: bold; }
footer { margin-top: 20px; color: #5f5f5f; font-size: 11px; line-height: 1.5; }
@media print { body { margin: 10mm; } header { border: none; padding: 0; } }
</style></head><body>
<header>
<div>
    <h1>Bulletin de Notes Scolaires</h1>
    <p><b>Élève :</b> $eleve $matricule</p>
    <p><b>Parcours :</b> $classe</p>
</div>
<div class="moy">Moyenne Générale<b>$moyenne / 20</b><span style="font-weight:bold; color: #0067b8;">$mention</span></div>
</header>
<table>
<tr>$entetes</tr>
$lignes
<tr class="total">$total</tr>
</table>
<footer>Généré le $date.<br>
Moyenne Générale = somme (Moyennes Trimestrielles × Coefficients) / somme des Coefficients des matières évaluées.</footer>
</body></html>
""")

# ============================================================
# LOGIQUE ET DONNÉES
# ============================================================

notes = {"S1": {}, "S2": {}}
coefs = {}  # vide au premier démarrage comme demandé
semestre_courant = "S1"


def charger_donnees():
    global semestre_courant, MATIERES, coefs
    if not FICHIER_NOTES.exists():
        MATIERES = list(MATIERES_DEFAUT)
        coefs = {}
        return {}, False, "fr", "S1"
    try:
        with FICHIER_NOTES.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        MATIERES = list(MATIERES_DEFAUT)
        coefs = {}
        return {}, False, "fr", "S1"
    if not isinstance(data, dict):
        MATIERES = list(MATIERES_DEFAUT)
        coefs = {}
        return {}, False, "fr", "S1"

    # Matières personnalisées
    matieres_lues = data.get("matieres")
    if isinstance(matieres_lues, list) and matieres_lues:
        try:
            nouvelles = []
            for m in matieres_lues:
                if isinstance(m, (list, tuple)) and len(m) >= 2:
                    nom = str(m[0])
                    code = str(m[1]).lower().strip()[:10]
                    c_def = m[2] if len(m) > 2 else 0
                    nouvelles.append((nom, code, c_def))
            if nouvelles:
                MATIERES = nouvelles
        except Exception:
            MATIERES = list(MATIERES_DEFAUT)

    notes_lues = data.get("notes", {})
    coefs_lus = data.get("coefs", {})
    eleve = data.get("eleve", {})
    mode_clair = data.get("mode_clair", False)
    langue = data.get("langue", "fr")
    sem = data.get("semestre_courant", "S1")

    if isinstance(notes_lues, dict):
        if "S1" in notes_lues or "S2" in notes_lues:
            for s in SEMESTRES:
                if s in notes_lues and isinstance(notes_lues[s], dict):
                    notes[s].update(notes_lues[s])
        else:
            notes["S1"].update(notes_lues)

    coefs = {}
    if isinstance(coefs_lus, dict):
        for code, valeur in coefs_lus.items():
            try:
                valeur = float(valeur)
            except (TypeError, ValueError):
                continue
            if 0 < valeur <= COEF_MAX:
                coefs[code] = valeur
    return (eleve if isinstance(eleve, dict) else {}), mode_clair, langue, sem


def lire_note(code, cle_court, semestre=None):
    if semestre is None:
        semestre = semestre_courant
    valeur = notes.get(semestre, {}).get(f"{code}{cle_court}")
    if valeur in (None, ""):
        return None
    try:
        return float(str(valeur).replace(",", "."))
    except ValueError:
        return None


def calculer_matiere(code, semestre=None):
    if semestre is None:
        semestre = semestre_courant
    interros = [lire_note(code, f"i{n}", semestre) for n in range(1, NB_INTERROS + 1)]
    devoirs = [lire_note(code, f"d{n}", semestre) for n in range(1, NB_DEVOIRS + 1)]

    interros_saisies = [x for x in interros if x is not None]
    moy_interro = (
        sum(interros_saisies) / len(interros_saisies) if interros_saisies else None
    )

    valeurs = [x for x in devoirs if x is not None]
    if moy_interro is not None:
        valeurs.insert(0, moy_interro)
    moyenne = sum(valeurs) / len(valeurs) if valeurs else None

    coef = coefs.get(code, 0)
    moy_coef = moyenne * coef if moyenne is not None and coef else None
    return {
        "coef": coef,
        "interros": interros,
        "devoirs": devoirs,
        "moy_interro": moy_interro,
        "moyenne": moyenne,
        "moy_coef": moy_coef,
    }


def resume(semestre=None):
    if semestre is None:
        semestre = semestre_courant
    evaluees = []
    total_points = 0.0
    total_coefs = 0.0
    for nom, code, _ in MATIERES:
        r = calculer_matiere(code, semestre)
        if r["moyenne"] is not None:
            evaluees.append((nom, r["moyenne"]))
            if r["coef"]:
                total_points += r["moy_coef"] if r["moy_coef"] is not None else 0
                total_coefs += r["coef"]
    return {
        "moyenne_generale": total_points / total_coefs if total_coefs else None,
        "total_points": total_points,
        "total_coefs": total_coefs,
        "nb_evaluees": len(evaluees),
        "meilleure": max(evaluees, key=lambda x: x[1]) if evaluees else None,
        "faible": min(evaluees, key=lambda x: x[1]) if len(evaluees) > 1 else None,
    }


def mention(moyenne, langue="fr"):
    m = TRADUCTIONS[langue]["mentions"]
    if moyenne is None:
        return m["aucune"]
    if moyenne >= 16:
        return m["tb"]
    if moyenne >= 14:
        return m["b"]
    if moyenne >= 12:
        return m["ab"]
    if moyenne >= SEUIL:
        return m["p"]
    return m["i"]


def fmt_note(x):
    return "" if x is None else f"{x:g}"


def fmt_moy(x):
    return "" if x is None else f"{x:.2f}"


def fmt_coef(x):
    if x is None or x == 0:
        return ""
    return f"{x:g}"


def texte_ligne(nom, r):
    return [
        fmt_coef(r['coef']),
        nom,
        *[fmt_note(x) for x in r["interros"]],
        fmt_moy(r["moy_interro"]),
        *[fmt_note(x) for x in r["devoirs"]],
        fmt_moy(r["moyenne"]),
        fmt_moy(r["moy_coef"]),
    ]


def ligne_total_textes(res, langue="fr"):
    return [
        fmt_coef(res['total_coefs']),
        TRADUCTIONS[langue]["total_libelle"],
        *[""] * 8,
        fmt_moy(res["moyenne_generale"]),
        fmt_moy(res["total_points"]) if res["nb_evaluees"] else "",
    ]

# ============================================================
# FENÊTRE DE PARAMÈTRES (DIALOGUE)
# ============================================================

class DialogueParametres(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app_parent = parent
        self.resize(420, 410)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        self.lbl_titre = QLabel()
        self.lbl_titre.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.lbl_titre)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.combo_langue = QComboBox()
        self.combo_langue.addItems(["Français", "English"])
        self.combo_langue.setCurrentIndex(0 if getattr(parent, "langue", "fr") == "fr" else 1)
        self.combo_langue.currentIndexChanged.connect(self.changer_langue)
        
        self.lbl_langue = QLabel()
        form_layout.addRow(self.lbl_langue, self.combo_langue)

        self.combo_theme = QComboBox()
        self.lbl_theme = QLabel()
        self.combo_theme.setCurrentIndex(1 if getattr(parent, "mode_clair", False) else 0)
        self.combo_theme.currentIndexChanged.connect(self.changer_theme)
        form_layout.addRow(self.lbl_theme, self.combo_theme)

        self.combo_semestre = QComboBox()
        self.lbl_semestre = QLabel()
        self.combo_semestre.setCurrentIndex(0 if getattr(parent, "semestre_courant", "S1")=="S1" else 1)
        self.combo_semestre.currentIndexChanged.connect(self.changer_semestre)
        form_layout.addRow(self.lbl_semestre, self.combo_semestre)

        layout.addLayout(form_layout)

        # --- Deux options demandées : ajouter / retirer matière ---
        from PyQt6.QtWidgets import QInputDialog, QListWidget, QListWidgetItem
        self._extra_imports = (QInputDialog, QListWidget)

        btns_matieres = QHBoxLayout()
        self.btn_ajouter_mat = QPushButton("➕ Ajouter une matière")
        self.btn_retirer_mat = QPushButton("➖ Retirer une matière")
        self.btn_ajouter_mat.clicked.connect(self.ajouter_matiere_simple)
        self.btn_retirer_mat.clicked.connect(self.retirer_matiere_simple)
        btns_matieres.addWidget(self.btn_ajouter_mat)
        btns_matieres.addWidget(self.btn_retirer_mat)
        layout.addLayout(btns_matieres)

        separateur = QFrame()
        separateur.setFrameShape(QFrame.Shape.HLine)
        separateur.setStyleSheet(f"background-color: {BORDURE}; max-height: 1px;")
        layout.addWidget(separateur)

        self.lbl_actions = QLabel()
        self.lbl_actions.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.lbl_actions)

        self.btn_html = QPushButton()
        self.btn_html.setObjectName("btn_principal")
        self.btn_html.clicked.connect(self.app_parent.exporter_html)
        layout.addWidget(self.btn_html)

        self.btn_csv = QPushButton()
        self.btn_csv.clicked.connect(self.app_parent.exporter_csv)
        layout.addWidget(self.btn_csv)

        self.btn_reset = QPushButton()
        self.btn_reset.setStyleSheet(f"color: {ROUGE}; border-color: {ROUGE};")
        self.btn_reset.clicked.connect(self.app_parent.effacer_notes)
        layout.addWidget(self.btn_reset)

        self.btn_apropos = QPushButton()
        self.btn_apropos.clicked.connect(self.ouvrir_a_propos)
        layout.addWidget(self.btn_apropos)

        layout.addStretch()
        self.recalculer_textes()

    def ouvrir_a_propos(self):
        t_langue = getattr(self.app_parent, "langue", "fr")
        if t_langue == "en":
            titre = "About Relevé de Notes"
            message = (
                "<b>Grade Report Application</b><br>"
                "Version 1.0 (2026)<br><br>"
                "<b>Developed by:</b> Antoine Epiphane Segla<br>"
                "Designed with PyQt6 & Python.<br><br>"
                "© 2026 All rights reserved."
            )
        else:
            titre = "À propos de Relevé de Notes"
            message = (
                "<b>Application Relevé de Notes</b><br>"
                "Version 1.0 (2026)<br><br>"
                "<b>Développé par :</b> Antoine Epiphane Segla<br>"
                "Conçu avec PyQt6 & Python.<br><br>"
                "© 2026 Tous droits réservés."
            )

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(titre)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()

    def ajouter_matiere_simple(self):
        from PyQt6.QtWidgets import QInputDialog
        nom, ok = QInputDialog.getText(self, "Ajouter une matière", "Nom de la matière :")
        if not ok:
            return
        nom = nom.strip()
        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom ne peut pas être vide.")
            return
        # Générer un code unique à partir du nom
        base = "".join([c for c in nom.lower() if c.isalnum()])[:4]
        if len(base) < 2:
            base = (nom.lower()[:2] + "x")[:3]
        code = base
        idx = 1
        exist = {c for _, c, _ in MATIERES}
        while code in exist:
            idx += 1
            code = f"{base}{idx}"
        MATIERES.append((nom, code, 0))
        # coef reste vide (0)
        self.app_parent.sauvegarder()
        self.app_parent.rafraichir_tout()
        QMessageBox.information(self, "Ajouté", f"Matière '{nom}' ajoutée au tableau.")

    def retirer_matiere_simple(self):
        from PyQt6.QtWidgets import QInputDialog, QListWidget, QListWidgetItem, QDialog, QVBoxLayout, QHBoxLayout, QPushButton

        dlg = QDialog(self)
        dlg.setWindowTitle("Retirer une matière")
        dlg.resize(360, 400)
        v = QVBoxLayout(dlg)
        v.addWidget(QLabel("Choisissez la matière à supprimer :"))
        liste = QListWidget()
        for nom, code, _ in MATIERES:
            liste.addItem(f"{nom}  ({code})")
        v.addWidget(liste)

        h = QHBoxLayout()
        h.addStretch()
        btn_ann = QPushButton("Annuler")
        btn_sup = QPushButton("Supprimer")
        btn_sup.setStyleSheet(f"color: {ROUGE}; border-color: {ROUGE};")
        h.addWidget(btn_ann)
        h.addWidget(btn_sup)
        v.addLayout(h)

        btn_ann.clicked.connect(dlg.reject)

        def do_sup():
            row = liste.currentRow()
            if row < 0:
                QMessageBox.warning(dlg, "Aucune sélection", "Sélectionnez une matière.")
                return
            nom, code, _ = MATIERES[row]
            rep = QMessageBox.question(dlg, "Confirmer", f"Supprimer '{nom}' ?\nLes notes de cette matière seront perdues.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if rep != QMessageBox.StandardButton.Yes:
                return
            # Supprimer
            MATIERES.pop(row)
            coefs.pop(code, None)
            for sem in SEMESTRES:
                keys = [k for k in list(notes[sem].keys()) if k.startswith(code)]
                for k in keys:
                    notes[sem].pop(k, None)
            self.app_parent.sauvegarder()
            self.app_parent.rafraichir_tout()
            dlg.accept()

        btn_sup.clicked.connect(do_sup)
        dlg.exec()

    def recalculer_textes(self):
        t = TRADUCTIONS[self.app_parent.langue]
        self.setWindowTitle(t["param_titre"])
        self.lbl_titre.setText(t["param_section_opt"])
        self.lbl_langue.setText(t["langue_libelle"])
        self.lbl_theme.setText(t["theme_libelle"])
        self.lbl_semestre.setText(t["semestre_libelle"])
        
        self.combo_theme.blockSignals(True)
        self.combo_theme.clear()
        self.combo_theme.addItems([t["theme_sombre"], t["theme_clair"]])
        self.combo_theme.setCurrentIndex(1 if self.app_parent.mode_clair else 0)
        self.combo_theme.blockSignals(False)

        self.combo_semestre.blockSignals(True)
        self.combo_semestre.clear()
        self.combo_semestre.addItems([t["semestre_1"], t["semestre_2"]])
        self.combo_semestre.setCurrentIndex(0 if self.app_parent.semestre_courant=="S1" else 1)
        self.combo_semestre.blockSignals(False)

        self.lbl_actions.setText(t["param_section_actions"])
        self.btn_html.setText(t["btn_html"])
        self.btn_csv.setText(t["btn_csv"])
        self.btn_reset.setText(t["btn_reset"])
        self.btn_apropos.setText(t["btn_apropos"])

    def changer_langue(self, index):
        langue = "fr" if index == 0 else "en"
        self.app_parent.changer_langue(langue)
        self.recalculer_textes()

    def changer_theme(self, index):
        mode_clair = (index == 1)
        self.app_parent.appliquer_theme(mode_clair)

    def changer_semestre(self, index):
        sem = "S1" if index==0 else "S2"
        self.app_parent.changer_semestre(sem)

# ============================================================
# APPLICATION PRINCIPALE PYQT6
# ============================================================

class ReleveNotesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(890, 785)

        chemin_logo = DOSSIER / "icone.png"
        if chemin_logo.exists():
            self.setWindowIcon(QIcon(str(chemin_logo)))

        self.eleve_sauve, mode_clair_sauve, langue_sauve, sem_sauve = charger_donnees()
        self.mode_clair = mode_clair_sauve
        self.langue = langue_sauve
        self.semestre_courant = sem_sauve if sem_sauve in SEMESTRES else "S1"
        global semestre_courant
        semestre_courant = self.semestre_courant
        self.eleve_inputs = {}
        self.labels_statiques = {}

        self.init_ui()
        if self.mode_clair:
            self.appliquer_theme(True)

        self.charger_identite()
        self.traduire_interface()
        self.rafraichir_tout()

    def nom_complet(self):
        nom = self.eleve_inputs.get("nom")
        prenom = self.eleve_inputs.get("prenom")
        nom_txt = nom.text().strip() if nom else ""
        prenom_txt = prenom.text().strip() if prenom else ""
        if nom_txt and prenom_txt:
            return f"{prenom_txt} {nom_txt}"
        return nom_txt or prenom_txt or "Élève"

    def sauvegarder(self):
        donnees = {
            "eleve": {k: v.text() for k, v in self.eleve_inputs.items()},
            "coefs": coefs,
            "notes": notes,
            "matieres": MATIERES,
            "mode_clair": getattr(self, "mode_clair", False),
            "langue": getattr(self, "langue", "fr"),
            "semestre_courant": getattr(self, "semestre_courant", "S1"),
        }
        try:
            with FICHIER_NOTES.open("w", encoding="utf-8") as f:
                json.dump(donnees, f, ensure_ascii=False, indent=4)
        except OSError as erreur:
            QMessageBox.critical(
                self, "Erreur", f"Impossible d'enregistrer les notes.\n{erreur}"
            )

    def changer_langue(self, code_langue):
        self.langue = code_langue
        self.traduire_interface()
        self.sauvegarder()
        self.rafraichir_tout()

    def changer_semestre(self, nouveau_sem):
        self.semestre_courant = nouveau_sem
        global semestre_courant
        semestre_courant = nouveau_sem
        self.sauvegarder()
        self.rafraichir_tout()
        self.mettre_a_jour_badge_trimestre()
        if hasattr(self, 'lbl_status'):
            t = TRADUCTIONS.get(self.langue, TRADUCTIONS["fr"])
            label_sem = t["semestre_1"] if nouveau_sem=="S1" else t["semestre_2"]
            self.lbl_status.setText(f"{t['pret']} — {label_sem}")
        # met à jour badge bas
        if hasattr(self, 'lbl_status'):
            t = TRADUCTIONS[self.langue]
            label_sem = t["semestre_1"] if nouveau_sem=="S1" else t["semestre_2"]
            # on garde le statut pret + semestre
            self.lbl_status.setText(f"{t['pret']} — {label_sem}")


    def traduire_interface(self):
        t = TRADUCTIONS[self.langue]
        self.setWindowTitle(t["fenetre_titre"])
        self.lbl_app_titre.setText(t["app_titre"])
        self.lbl_titre_moy.setText(t["moyenne_generale"])
        self.labels_statiques["infos_eleve"].setText(t["infos_eleve"])
        self.labels_statiques["vue_ensemble"].setText(t["vue_ensemble"])
        self.labels_statiques["resultats"].setText(t["resultats"])
        self.labels_statiques["aide_cellule"].setText(t["aide_cellule"])

        for key in ["nom", "prenom", "matricule", "classe", "filiere", "annee"]:
            if key in self.labels_statiques:
                self.labels_statiques[key].setText(t[key])

        for col_idx, titre in enumerate(t["entetes"]):
            item = QTableWidgetItem(titre)
            self.table.setHorizontalHeaderItem(col_idx, item)

        self.btn_parametres.setText(t["parametres"])
        self.lbl_status.setText(t["pret"])

    def appliquer_theme(self, mode_clair):
        global FOND, CARTE, CARTE_2, CHAMP, BORDURE, TEXTE, TEXTE_DOUX
        self.mode_clair = mode_clair
        
        if mode_clair:
            FOND = "#ffffff"
            CARTE = "#ffffff"
            CARTE_2 = "#e4e8ee"
            CHAMP = "#f8f9fa"
            BORDURE = "#cbd5e1"
            TEXTE = "#0f172a"
            TEXTE_DOUX = "#1e293b"
            scroll_handle = "#cbd5e1"
            scroll_handle_hover = "#94a3b8"
        else:
            FOND = "#0b0d10"
            CARTE = "#14171c"
            CARTE_2 = "#1b2027"
            CHAMP = "#1a1e24"
            BORDURE = "#2c333d"
            TEXTE = "#f1f3f5"
            TEXTE_DOUX = "#a5adb8"
            scroll_handle = "#4a525d"
            scroll_handle_hover = "#687382"

        nouveau_style = f"""
        QMainWindow {{ background-color: {FOND}; }}
        QScrollArea {{ background-color: {FOND}; border: none; }}
        QWidget {{ color: {TEXTE}; font-family: "{POLICE}"; font-size: 13px; background-color: {FOND}; }}
        QLabel {{ border: none !important; background: transparent !important; outline: none !important; }}
        QFrame {{ border: none; }}
        QFrame#carte_principale {{ background-color: {CARTE}; border: 1px solid {BORDURE}; border-radius: 12px; }}
        QFrame#carte_entete {{ background-color: {"#ffffff" if mode_clair else "#111820"}; border: 1px solid {BORDURE}; border-radius: 14px; }}
        QFrame#bloc_moyenne {{ background-color: {CARTE}; border: 1px solid {BORDURE}; border-radius: 12px; }}
        QFrame#stat_card {{ background-color: {CARTE_2}; border: 1px solid {BORDURE}; border-radius: 10px; }}
        
        QLineEdit {{
            background-color: {CHAMP};
            border: 1px solid {BORDURE};
            border-radius: 8px;
            padding: 8px 12px;
            color: {TEXTE};
            font-size: 13px;
        }}
        QLineEdit:focus {{
            border: 1px solid {ACCENT};
        }}

        /* SUPPRESSION DE LA FLÈCHE NATIVE & REMPLACEMENT PAR UN TRAIT VERTICAL ÉPURÉ */
        QComboBox {{
            background-color: {CHAMP};
            border: 1px solid {BORDURE};
            border-radius: 8px;
            padding: 6px 12px;
            color: {TEXTE};
            font-size: 13px;
        }}
        QComboBox:focus {{
            border: 1px solid {ACCENT};
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 2px solid {TEXTE_DOUX};
            margin-top: 8px;
            margin-bottom: 8px;
            margin-right: 8px;
            background: transparent;
        }}
        QComboBox::down-arrow {{
            image: none;
            width: 0px;
            height: 0px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {CARTE};
            color: {TEXTE};
            border: 1px solid {BORDURE};
            selection-background-color: {ACCENT};
            selection-color: white;
            outline: none;
            border-radius: 6px;
            padding: 4px;
        }}

        QPushButton {{ background-color: {CARTE}; border: 1px solid {BORDURE}; border-radius: 8px; padding: 10px 20px; color: {TEXTE}; font-weight: bold; font-size: 13px; }}
        QPushButton:hover {{ background-color: {"#e2e8f0" if mode_clair else "#252b33"}; }}
        QPushButton#btn_principal {{ background-color: {ACCENT}; border: none; color: white; }}
        QPushButton#btn_principal:hover {{ background-color: {ACCENT_HOVER}; }}
        
        QTableWidget {{ background-color: {CARTE}; border: 1px solid {BORDURE}; border-radius: 10px; gridline-color: {BORDURE}; font-size: 13px; }}
        QHeaderView::section {{ background-color: {"#e2e8f0" if mode_clair else "#20262d"}; color: {TEXTE}; font-weight: bold; padding: 8px; border: 1px solid {BORDURE}; font-size: 12px; }}
        QDialog {{ background-color: {FOND}; }}

        /* BARRES DE DÉFILEMENT */
        QScrollBar:vertical {{ background: transparent; width: 10px; margin: 0px; }}
        QScrollBar::handle:vertical {{ background: {scroll_handle}; min-height: 30px; border-radius: 5px; }}
        QScrollBar::handle:vertical:hover {{ background: {scroll_handle_hover}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical, QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; height: 0px; }}

        QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 0px; }}
        QScrollBar::handle:horizontal {{ background: {scroll_handle}; min-width: 30px; border-radius: 5px; }}
        QScrollBar::handle:horizontal:hover {{ background: {scroll_handle_hover}; }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal, QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; width: 0px; }}
        """
        QApplication.instance().setStyleSheet(nouveau_style)

        if hasattr(self, "lbl_sous_titre"):
            self.lbl_sous_titre.setStyleSheet(f"color: {TEXTE_DOUX}; font-size: 12px;")
        if hasattr(self, "lbl_status"):
            self.lbl_status.setStyleSheet(f"color: {TEXTE_DOUX}; font-size: 11px;")
        if hasattr(self, "btn_trimestre"):
            self.btn_trimestre.setStyleSheet(f"""
                QPushButton#btn_trimestre {{
                    background-color: {CARTE_2};
                    border: 1px solid {BORDURE};
                    border-radius: 8px;
                    padding: 9px 16px;
                    font-weight: bold;
                    font-size: 12px;
                    color: {TEXTE};
                }}
                QPushButton#btn_trimestre:hover {{
                    background-color: {"#e2e8f0" if self.mode_clair else "#252b33"};
                    border-color: {ACCENT};
                }}
            """)
            self.mettre_a_jour_badge_trimestre()

        self.sauvegarder()
        self.rafraichir_tout()

    def init_ui(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.setCentralWidget(scroll_area)

        main_widget = QWidget()
        scroll_area.setWidget(main_widget)

        self.layout_principal = QVBoxLayout(main_widget)
        self.layout_principal.setContentsMargins(20, 20, 20, 20)
        self.layout_principal.setSpacing(16)

        self.creer_entete()
        self.creer_section_infos()
        self.creer_section_stats()
        self.creer_section_tableau()
        self.creer_pied_de_page()

    def creer_carte(self):
        carte = QFrame()
        carte.setObjectName("carte_principale")
        return carte

    def creer_entete(self):
        entete = QFrame()
        entete.setObjectName("carte_entete")
        layout = QHBoxLayout(entete)
        layout.setContentsMargins(20, 20, 20, 20)

        lbl_logo = QLabel()
        lbl_logo.setFixedSize(75, 75)
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setStyleSheet(
            f"background-color: #181d23; border: 1px solid {BORDURE} !important; border-radius: 12px;"
        )

        chemin_logo = DOSSIER / "logo.png"
        if chemin_logo.exists():
            pix = QPixmap(str(chemin_logo)).scaled(
                65, 65, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            lbl_logo.setPixmap(pix)
        else:
            lbl_logo.setText("🎓")
            lbl_logo.setFont(QFont("Segoe UI Emoji", 32))

        layout.addWidget(lbl_logo)

        vbox_titre = QVBoxLayout()
        self.lbl_app_titre = QLabel()
        self.lbl_app_titre.setStyleSheet(f"color: {ACCENT}; font-weight: bold; font-size: 13px;")

        self.lbl_eleve_nom = QLabel("CPET LE PHENIX")
        self.lbl_eleve_nom.setStyleSheet("font-size: 22px; font-weight: bold;")

        self.lbl_sous_titre = QLabel("")
        self.lbl_sous_titre.setStyleSheet(f"color: {TEXTE_DOUX}; font-size: 12px;")

        vbox_titre.addWidget(self.lbl_app_titre)
        vbox_titre.addWidget(self.lbl_eleve_nom)
        vbox_titre.addWidget(self.lbl_sous_titre)
        vbox_titre.addStretch()

        layout.addLayout(vbox_titre)
        layout.addStretch()

        # Bloc Moyenne
        bloc_moy = QFrame()
        bloc_moy.setObjectName("bloc_moyenne")
        vbox_moy = QVBoxLayout(bloc_moy)
        vbox_moy.setContentsMargins(18, 12, 18, 12)

        self.lbl_titre_moy = QLabel()
        self.lbl_titre_moy.setStyleSheet(f"color: {TEXTE_DOUX}; font-weight: bold; font-size: 10px;")
        self.lbl_titre_moy.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.lbl_moy_val = QLabel("—")
        self.lbl_moy_val.setStyleSheet("font-size: 28px; font-weight: bold;")
        self.lbl_moy_val.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.lbl_mention = QLabel()
        self.lbl_mention.setStyleSheet(f"color: {TEXTE_DOUX}; font-weight: bold; font-size: 12px;")
        self.lbl_mention.setAlignment(Qt.AlignmentFlag.AlignRight)

        vbox_moy.addWidget(self.lbl_titre_moy)
        vbox_moy.addWidget(self.lbl_moy_val)
        vbox_moy.addWidget(self.lbl_mention)

        layout.addWidget(bloc_moy)
        self.layout_principal.addWidget(entete)

    def ouvrir_parametres(self):
        dialogue = DialogueParametres(self)
        dialogue.exec()

    def creer_section_infos(self):
        carte = self.creer_carte()
        vbox = QVBoxLayout(carte)
        vbox.setContentsMargins(18, 16, 18, 16)
        vbox.setSpacing(12)

        lbl_t = QLabel()
        lbl_t.setStyleSheet("font-size: 16px; font-weight: bold;")
        vbox.addWidget(lbl_t)
        self.labels_statiques["infos_eleve"] = lbl_t

        champs = [
            ("nom", 0),
            ("prenom", 0),
            ("matricule", 0),
            ("classe", 1),
            ("filiere", 1),
            ("annee", 1),
        ]

        grid_1 = QHBoxLayout()
        grid_2 = QHBoxLayout()

        for key, row in champs:
            box = QVBoxLayout()
            lbl = QLabel()
            lbl.setStyleSheet(f"color: {TEXTE_DOUX}; font-size: 10px; font-weight: bold;")
            self.labels_statiques[key] = lbl

            inp = QLineEdit()
            inp.editingFinished.connect(self.enregistrer_identite)
            self.eleve_inputs[key] = inp

            box.addWidget(lbl)
            box.addWidget(inp)

            if row == 0:
                grid_1.addLayout(box)
            else:
                grid_2.addLayout(box)

        vbox.addLayout(grid_1)
        vbox.addLayout(grid_2)
        self.layout_principal.addWidget(carte)

    def creer_section_stats(self):
        carte = self.creer_carte()
        vbox = QVBoxLayout(carte)
        vbox.setContentsMargins(18, 16, 18, 16)
        vbox.setSpacing(12)

        lbl_t = QLabel()
        lbl_t.setStyleSheet("font-size: 16px; font-weight: bold;")
        vbox.addWidget(lbl_t)
        self.labels_statiques["vue_ensemble"] = lbl_t

        hbox = QHBoxLayout()
        self.stat_labels = {}
        self.stat_titres = {}

        for key in ["matieres_notees", "total_points", "meilleure_matiere", "a_renforcer"]:
            b = QFrame()
            b.setObjectName("stat_card")
            v = QVBoxLayout(b)
            v.setContentsMargins(12, 10, 12, 10)

            l1 = QLabel()
            l1.setStyleSheet(f"color: {TEXTE_DOUX}; font-size: 9px; font-weight: bold;")
            self.stat_titres[key] = l1

            l2 = QLabel("—")
            l2.setStyleSheet("font-size: 13px; font-weight: bold;")
            l2.setAlignment(Qt.AlignmentFlag.AlignCenter)

            v.addWidget(l1)
            v.addWidget(l2)
            hbox.addWidget(b)
            self.stat_labels[key] = l2

        vbox.addLayout(hbox)
        self.layout_principal.addWidget(carte)

    def creer_section_tableau(self):
        carte = self.creer_carte()
        vbox = QVBoxLayout(carte)
        vbox.setContentsMargins(18, 16, 18, 16)
        vbox.setSpacing(10)

        lbl_t = QLabel()
        lbl_t.setStyleSheet("font-size: 16px; font-weight: bold;")
        lbl_sub = QLabel()
        lbl_sub.setStyleSheet(f"color: {TEXTE_DOUX}; font-size: 11px;")

        self.labels_statiques["resultats"] = lbl_t
        self.labels_statiques["aide_cellule"] = lbl_sub

        vbox.addWidget(lbl_t)
        vbox.addWidget(lbl_sub)

        self.table = QTableWidget()
        self.table.setRowCount(len(MATIERES) + 1)
        self.table.setColumnCount(len(COLONNES_CLES))
        self.table.verticalHeader().setVisible(False)
        
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        for col_idx, width in enumerate(LARGEURS_COLONNES):
            self.table.setColumnWidth(col_idx, width)

        hauteur_entete = 38
        hauteur_ligne = 32
        hauteur_totale = hauteur_entete + (len(MATIERES) + 1) * hauteur_ligne + 25
        self.table.setFixedHeight(hauteur_totale)

        scroll_tableau = QScrollArea()
        scroll_tableau.setWidgetResizable(True)
        scroll_tableau.setFrameShape(QFrame.Shape.NoFrame)
        scroll_tableau.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_tableau.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_tableau.setWidget(self.table)
        scroll_tableau.setFixedHeight(hauteur_totale + 10)

        self.table.cellChanged.connect(self.on_cell_changed)
        vbox.addWidget(scroll_tableau)
        self.layout_principal.addWidget(carte)

    def creer_pied_de_page(self):
        hbox = QHBoxLayout()
        hbox.setSpacing(12)
        hbox.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.btn_parametres = QPushButton()
        self.btn_parametres.clicked.connect(self.ouvrir_parametres)
        hbox.addWidget(self.btn_parametres, alignment=Qt.AlignmentFlag.AlignVCenter)

        hbox.addStretch()

        self.lbl_status = QLabel()
        self.lbl_status.setStyleSheet(f"color: {TEXTE_DOUX}; font-size: 11px;")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        hbox.addWidget(self.lbl_status, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Indicateur trimestre actuel en bas à droite comme un bouton
        self.btn_trimestre = QPushButton()
        self.btn_trimestre.setObjectName("btn_trimestre")
        self.btn_trimestre.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_trimestre.setStyleSheet(f"""
            QPushButton#btn_trimestre {{
                background-color: {CARTE_2};
                border: 1px solid {BORDURE};
                border-radius: 8px;
                padding: 9px 16px;
                font-weight: bold;
                font-size: 12px;
                color: {TEXTE};
            }}
            QPushButton#btn_trimestre:hover {{
                background-color: #252b33;
                border-color: {ACCENT};
            }}
        """)
        self.btn_trimestre.clicked.connect(self.basculer_semestre_depuis_badge)
        hbox.addWidget(self.btn_trimestre, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.layout_principal.addLayout(hbox)
        # Mettre à jour immédiatement après création
        self.mettre_a_jour_badge_trimestre()

    def basculer_semestre_depuis_badge(self):
        nouveau = "S2" if self.semestre_courant == "S1" else "S1"
        self.changer_semestre(nouveau)

    def mettre_a_jour_badge_trimestre(self):
        if not hasattr(self, 'btn_trimestre'):
            return
        t = TRADUCTIONS.get(self.langue, TRADUCTIONS["fr"])
        label = t["semestre_1"] if self.semestre_courant == "S1" else t["semestre_2"]
        self.btn_trimestre.setText(f"📅  {label}")
        self.btn_trimestre.setToolTip("Cliquer pour changer de semestre")
        # Forcer le repaint
        self.btn_trimestre.update()

    def charger_identite(self):
        for k, inp in self.eleve_inputs.items():
            if k in self.eleve_sauve:
                inp.setText(str(self.eleve_sauve[k]))
        self.enregistrer_identite()

    def enregistrer_identite(self):
        morceaux = [
            self.eleve_inputs["classe"].text().strip(),
            self.eleve_inputs["filiere"].text().strip(),
            self.eleve_inputs["annee"].text().strip(),
        ]
        self.lbl_sous_titre.setText("  •  ".join(m for m in morceaux if m))
        self.sauvegarder()

    def rafraichir_tout(self):
        t = TRADUCTIONS[self.langue]
        # Ajuster nombre de lignes si matières ajoutées/supprimées
        needed = len(MATIERES) + 1
        if self.table.rowCount() != needed:
            self.table.setRowCount(needed)
            # ajuster hauteur
            try:
                hauteur_entete = 38
                hauteur_ligne = 32
                hauteur_totale = hauteur_entete + needed * hauteur_ligne + 25
                self.table.setFixedHeight(hauteur_totale)
                # parent scroll area
                parent = self.table.parent()
                if parent:
                    parent.setFixedHeight(hauteur_totale + 10)
            except Exception:
                pass

        self.table.blockSignals(True)

        for row, (nom, code, _) in enumerate(MATIERES):
            r = calculer_matiere(code)
            faible = r["moyenne"] is not None and r["moyenne"] < SEUIL
            valeurs = texte_ligne(nom, r)

            if self.mode_clair:
                bg_color = QColor("#fee2e2") if faible else QColor("#ffffff" if row % 2 == 0 else "#f8fafc")
            else:
                bg_color = QColor("#2a1719") if faible else QColor("#14171c" if row % 2 == 0 else "#11151a")
            
            fg_color = QColor(ROUGE) if faible else QColor(TEXTE)

            for col, val in enumerate(valeurs):
                item = QTableWidgetItem(val)
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                    if col == 1
                    else Qt.AlignmentFlag.AlignCenter
                )
                item.setBackground(bg_color)
                item.setForeground(fg_color)

                cle_col = COLONNES_CLES[col]
                if cle_col not in EDITABLES:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                self.table.setItem(row, col, item)

        res = resume()
        total_vals = ligne_total_textes(res, self.langue)
        row_total = len(MATIERES)

        bg_total = QColor("#cbd5e1") if self.mode_clair else QColor("#20262d")
        for col, val in enumerate(total_vals):
            item = QTableWidgetItem(val)
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                if col == 1
                else Qt.AlignmentFlag.AlignCenter
            )
            item.setBackground(bg_total)
            item.setForeground(QColor(TEXTE))
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_total, col, item)

        self.table.blockSignals(False)

        mg = res["moyenne_generale"]
        if mg is None:
            self.lbl_moy_val.setText("—")
            self.lbl_mention.setText(t["mentions"]["aucune"])
            self.lbl_mention.setStyleSheet(f"color: {TEXTE_DOUX}; font-weight: bold; font-size: 12px;")
        else:
            self.lbl_moy_val.setText(f"{mg:.2f}")
            m_text = mention(mg, self.langue)
            self.lbl_mention.setText(m_text)
            col_m = VERT if mg >= SEUIL else ROUGE
            self.lbl_mention.setStyleSheet(f"color: {col_m}; font-weight: bold; font-size: 12px;")

        for key in ["matieres_notees", "total_points", "meilleure_matiere", "a_renforcer"]:
            if key in self.stat_titres:
                self.stat_titres[key].setText(t[key])

        self.stat_labels["matieres_notees"].setText(f"{res['nb_evaluees']} / {len(MATIERES)}")
        self.stat_labels["total_points"].setText(fmt_moy(res["total_points"]) if res["nb_evaluees"] else "—")
        self.stat_labels["meilleure_matiere"].setText(
            f"{res['meilleure'][0]} ({res['meilleure'][1]:.2f})" if res["meilleure"] else "—"
        )
        self.stat_labels["a_renforcer"].setText(
            f"{res['faible'][0]} ({res['faible'][1]:.2f})" if res["faible"] else "—"
        )

        # MAJ badge semestre en bas
        if hasattr(self, 'lbl_sem_footer'):
            t = TRADUCTIONS[self.langue]
            sem_txt = t["semestre_1"] if self.semestre_courant=="S1" else t["semestre_2"]
            self.lbl_sem_footer.setText(sem_txt)
            # status avec semestre
            self.lbl_status.setText(f"{t['pret']} — {sem_txt}")

    def on_cell_changed(self, row, col):
        if row >= len(MATIERES):
            return

        code = MATIERES[row][1]
        cle_col = COLONNES_CLES[col]
        item = self.table.item(row, col)
        texte = item.text().strip().replace(",", ".")

        if cle_col == "coef":
            if texte == "":
                coefs.pop(code, None)
            else:
                try:
                    valeur = float(texte)
                    if 0 < valeur <= COEF_MAX:
                        coefs[code] = valeur
                    else:
                        QMessageBox.warning(self, "Invalide", f"Le coef doit être entre 1 et {COEF_MAX}.")
                except ValueError:
                    pass
        else:
            cle_note = f"{code}{cle_col}"
            target_notes = notes[self.semestre_courant]
            if texte == "":
                target_notes.pop(cle_note, None)
            else:
                try:
                    valeur = float(texte)
                    if 0 <= valeur <= NOTE_MAX:
                        target_notes[cle_note] = valeur
                    else:
                        QMessageBox.warning(self, "Invalide", f"La note doit être entre 0 et {NOTE_MAX}.")
                except ValueError:
                    pass

        self.sauvegarder()
        self.rafraichir_tout()

    def exporter_csv(self):
        t = TRADUCTIONS[self.langue]
        chemin, _ = QFileDialog.getSaveFileName(
            self, t["btn_csv"], "releve_de_notes.csv", "Classeur CSV (*.csv)"
        )
        if not chemin:
            return

        def virgule(ligne):
            return [str(c).replace(".", ",") for c in ligne]

        try:
            with open(chemin, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f, delimiter=";")
                w.writerow(["Élève", self.nom_complet()])
                w.writerow(["Classe", self.eleve_inputs["classe"].text(), self.eleve_inputs["filiere"].text()])
                w.writerow(["Année scolaire", self.eleve_inputs["annee"].text()])
                w.writerow([])
                w.writerow(t["entetes"])

                for nom, code, _ in MATIERES:
                    w.writerow(virgule(texte_ligne(nom, calculer_matiere(code))))

                w.writerow(virgule(ligne_total_textes(resume(), self.langue)))
            self.lbl_status.setText("Exporté avec succès.")
        except OSError as erreur:
            QMessageBox.critical(self, "Erreur", f"Échec de l'exportation.\n{erreur}")

    def exporter_html(self):
        res = resume()
        t = TRADUCTIONS[self.langue]
        lignes = ""

        for nom, code, _ in MATIERES:
            r = calculer_matiere(code)
            css = ' class="faible"' if r["moyenne"] is not None and r["moyenne"] < SEUIL else ""
            cellules = "".join(f"<td>{html.escape(c)}</td>" for c in texte_ligne(nom, r))
            lignes += f"<tr{css}>{cellules}</tr>\n"

        matricule = self.eleve_inputs["matricule"].text().strip()
        classe = " – ".join(
            p
            for p in (
                self.eleve_inputs["classe"].text().strip(),
                self.eleve_inputs["filiere"].text().strip(),
                "Année scolaire " + self.eleve_inputs["annee"].text().strip(),
            )
            if p
        )

        contenu = MODELE_HTML.substitute(
            eleve=html.escape(self.nom_complet()),
            matricule=html.escape(f" ({t['matricule']} : {matricule})") if matricule else "",
            classe=html.escape(classe),
            moyenne=fmt_moy(res["moyenne_generale"]) or "—",
            mention=html.escape(mention(res["moyenne_generale"], self.langue)),
            entetes="".join(f"<th>{html.escape(h)}</th>" for h in t["entetes"]),
            lignes=lignes,
            total="".join(f"<td>{html.escape(c)}</td>" for c in ligne_total_textes(res, self.langue)),
            date=date.today().strftime("%d/%m/%Y"),
        )

        chemin = DOSSIER_DONNEES / "releve_de_notes.html"
        try:
            chemin.write_text(contenu, encoding="utf-8")
            import webbrowser
            webbrowser.open(chemin.as_uri())
            self.lbl_status.setText("HTML prêt pour impression.")
        except OSError as erreur:
            QMessageBox.critical(self, "Erreur", f"Impossible de générer le document.\n{erreur}")

    def effacer_notes(self):
        t = TRADUCTIONS[self.langue]
        target = notes[self.semestre_courant]
        sem_label = t["semestre_1"] if self.semestre_courant=="S1" else t["semestre_2"]
        if not target:
            self.lbl_status.setText(f"Le registre {sem_label} est déjà vide.")
            return

        reponse = QMessageBox.question(
            self,
            "Réinitialisation",
            f"Voulez-vous vider les notes du {sem_label} ?\n(Les coefficients seront conservés et l'autre semestre gardé.)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reponse == QMessageBox.StandardButton.Yes:
            target.clear()
            self.sauvegarder()
            self.rafraichir_tout()
            self.lbl_status.setText(f"Registre {sem_label} réinitialisé.")

    def closeEvent(self, event):
        self.sauvegarder()
        event.accept()


# ============================================================
# EXECUTION DE L'APPLICATION
# ============================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET_BASE)

    def demarrer_app():
        try:
            global fenetre
            fenetre = ReleveNotesApp()
            fenetre.show()
        except Exception as e:
            print(f"Erreur attrapée : {e}")

    QTimer.singleShot(1, demarrer_app)
    sys.exit(app.exec())
