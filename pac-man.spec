# -*- mode: python ; coding: utf-8 -*-
#
# Fichier de packaging PyInstaller pour le projet Pacman.
# Doit rester a la racine du depot (exige par le sujet, chapitre VII).
#
# Ce build utilise une configuration dediee, independante de celle utilisee
# en developpement, afin de ne pas dependre du config.json du depot :
#
#   packaging/config.json  -> devient config.json dans le build
# Les highscores sont crees dans le dossier de donnees de l'utilisateur.
#
# Utilisation (depuis la racine du repo) :
#   rm -rf build dist
#   .venv/bin/pyinstaller pac-man.spec --noconfirm
#
# Le resultat se trouve dans dist/pac-man/ (mode onedir).
# C'est ce dossier entier qu'il faut zipper et uploader sur Itch.io.
#
# Verification apres build (le sous-dossier peut etre _internal/ selon
# la version de PyInstaller, voir pacman/paths.py qui gere ca au runtime) :
#   find dist/pac-man -name "sprites_sheet.png"
#   find dist/pac-man -name "config.json"
#   find dist/pac-man -name "README.txt"

from pathlib import Path

block_cipher = None

# Racine du projet = dossier contenant ce fichier .spec
PROJECT_ROOT = Path(SPECPATH)
PACKAGING_DIR = PROJECT_ROOT / "packaging"

# ---------------------------------------------------------------------------
# Ressources a embarquer dans le build.
# Format attendu par PyInstaller : (chemin_source, dossier_destination_dans_le_build)
# ---------------------------------------------------------------------------
datas = [
    # Dossier des assets (spritesheet, police)
    (str(PROJECT_ROOT / "assets"), "assets"),

    # Config dediee au build (pas le config.json de dev)
    (str(PACKAGING_DIR / "config.json"), "."),

    # Instructions minimales demandees dans le package livre
    (str(PACKAGING_DIR / "README.txt"), "."),
]

# Verifie que les fichiers dedies au packaging existent bien avant de
# builder, pour echouer tot avec un message clair plutot que de livrer
# un package incomplet.
for src, _dst in datas:
    if not Path(src).exists():
        raise FileNotFoundError(
            f"Fichier de packaging manquant : {src}\n"
            "Verifie que packaging/config.json et packaging/README.txt "
            "existent a la racine du repo."
        )

a = Analysis(
    ["pac-man.py"],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="pac-man",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="pac-man",
)
