#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Setup complet du projet Rock‑Paper‑Scissors CV sur macOS (Apple Silicon ou Intel)
# Installe Homebrew tcl‑tk, recompil CPython via pyenv, prépare le venv,
# installe les dépendances et teste Tkinter.
# -----------------------------------------------------------------------------
set -e

PYTHON_VERSION="3.10.12"           # tu peux mettre 3.11.x ou 3.12.x
PROJECT_DIR="$HOME/rock-paper-scissors-cv"

echo "==> 1. Vérification Homebrew"
if ! command -v brew &>/dev/null; then
  echo "❌ Homebrew manquant. Installe-le d’abord : https://brew.sh/"
  exit 1
fi
brew update

echo "==> 2. Installation pyenv & tcl‑tk"
brew install pyenv tcl-tk

# -----------------------------------------------------------------------------
# 3. Variables d’environnement permanentes pour que pyenv voie tcl‑tk
# -----------------------------------------------------------------------------
ZSHRC="$HOME/.zshrc"
echo "==> 3. Ajout des variables tcl‑tk dans $ZSHRC"
grep -q 'tcl-tk' "$ZSHRC" || cat <<'EOF' >> "$ZSHRC"

# —— Tcl/Tk pour Python (ajouté par setup_rps.sh) ——
export PATH="/opt/homebrew/opt/tcl-tk/bin:$PATH"
export LDFLAGS="-L/opt/homebrew/opt/tcl-tk/lib"
export CPPFLAGS="-I/opt/homebrew/opt/tcl-tk/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/tcl-tk/lib/pkgconfig"
EOF
source "$ZSHRC"

# -----------------------------------------------------------------------------
# 4. (Re)Compilation CPython avec Tk pris en compte
# -----------------------------------------------------------------------------
echo "==> 4. Compilation Python $PYTHON_VERSION avec Tk"
if pyenv versions | grep -q "$PYTHON_VERSION"; then
  echo "    — Version déjà présente, on la supprime pour la recompiler proprement."
  pyenv uninstall -f "$PYTHON_VERSION"
fi

env PYTHON_CONFIGURE_OPTS="--enable-shared" \
    CPPFLAGS="-I$(brew --prefix tcl-tk)/include" \
    LDFLAGS="-L$(brew --prefix tcl-tk)/lib" \
    PKG_CONFIG_PATH="$(brew --prefix tcl-tk)/lib/pkgconfig" \
    pyenv install "$PYTHON_VERSION"

pyenv global "$PYTHON_VERSION"
echo "    → Python $(python -V) activé"

# -----------------------------------------------------------------------------
# 5. Test Tkinter (ouvre et ferme une petite fenêtre)
# -----------------------------------------------------------------------------
python - <<'PY'
import tkinter, sys
print(f"    Tk version: {tkinter.TkVersion}")
tk = tkinter.Tk(); tk.withdraw(); tk.destroy()
PY

# -----------------------------------------------------------------------------
# 6. Création dossier projet + virtualenv + dépendances
# -----------------------------------------------------------------------------
echo "==> 6. Création du virtualenv & installation deps"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
python -m venv venv
source venv/bin/activate

pip install -U pip
pip install opencv-python mediapipe numpy
pip install --extra-index-url https://PySimpleGUI.net/install PySimpleGUI

echo "==> 7. Installation terminée !"
echo "Active le venv puis lance :"
echo "   source $PROJECT_DIR/venv/bin/activate"
echo "   python rps_cam.py"
