#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Complete setup for the Rock-Paper-Scissors CV project on macOS (Apple Silicon or Intel)
# Installs Homebrew tcl-tk, recompiles CPython via pyenv, sets up the venv,
# installs dependencies, and tests Tkinter.
# -----------------------------------------------------------------------------
set -e

PYTHON_VERSION="3.10.12"           # you can use 3.11.x or 3.12.x
PROJECT_DIR="$HOME/rock-paper-scissors-cv"

echo "==> 1. Checking Homebrew"
if ! command -v brew &>/dev/null; then
  echo "❌ Homebrew missing. Install it first: https://brew.sh/"
  exit 1
fi
brew update

echo "==> 2. Installing pyenv & tcl-tk"
brew install pyenv tcl-tk

# -----------------------------------------------------------------------------
# 3. Permanent environment variables for pyenv to detect tcl-tk
# -----------------------------------------------------------------------------
ZSHRC="$HOME/.zshrc"
echo "==> 3. Adding tcl-tk variables to $ZSHRC"
grep -q 'tcl-tk' "$ZSHRC" || cat <<'EOF' >> "$ZSHRC"

# —— Tcl/Tk for Python (added by setup_rps.sh) ——
export PATH="/opt/homebrew/opt/tcl-tk/bin:$PATH"
export LDFLAGS="-L/opt/homebrew/opt/tcl-tk/lib"
export CPPFLAGS="-I/opt/homebrew/opt/tcl-tk/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/tcl-tk/lib/pkgconfig"
EOF
source "$ZSHRC"

# -----------------------------------------------------------------------------
# 4. (Re)compiling CPython with Tk support
# -----------------------------------------------------------------------------
echo "==> 4. Compiling Python $PYTHON_VERSION with Tk"
if pyenv versions | grep -q "$PYTHON_VERSION"; then
  echo "    — Version already present, removing it for a clean recompile."
  pyenv uninstall -f "$PYTHON_VERSION"
fi

env PYTHON_CONFIGURE_OPTS="--enable-shared" \
    CPPFLAGS="-I$(brew --prefix tcl-tk)/include" \
    LDFLAGS="-L$(brew --prefix tcl-tk)/lib" \
    PKG_CONFIG_PATH="$(brew --prefix tcl-tk)/lib/pkgconfig" \
    pyenv install "$PYTHON_VERSION"

pyenv global "$PYTHON_VERSION"
echo "    → Python $(python -V) activated"

# -----------------------------------------------------------------------------
# 5. Testing Tkinter (opens and closes a small window)
# -----------------------------------------------------------------------------
python - <<'PY'
import tkinter, sys
print(f"    Tk version: {tkinter.TkVersion}")
tk = tkinter.Tk(); tk.withdraw(); tk.destroy()
PY

# -----------------------------------------------------------------------------
# 6. Creating project directory + virtualenv + dependencies
# -----------------------------------------------------------------------------
echo "==> 6. Creating virtualenv & installing dependencies"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
python -m venv venv
source venv/bin/activate

pip install -U pip
pip install opencv-python mediapipe numpy
pip install --extra-index-url https://PySimpleGUI.net/install PySimpleGUI

echo "==> 7. Installation complete!"
echo "Activate the venv and run:"
echo "   source $PROJECT_DIR/venv/bin/activate"
echo "   python rps_cam.py"
