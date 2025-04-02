# main.py
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))
from app import main

if __name__ == "__main__":
    main()