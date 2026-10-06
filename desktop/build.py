"""Build the reviewed spec with the current Python environment."""
import subprocess
import sys
from pathlib import Path

if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    raise SystemExit(subprocess.call([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', 'CompetitorMonitor.spec'], cwd=root))
