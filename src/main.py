"""Entry point. Run from the repository root: python -m src.main."""
from src.engine.app import GameApp

if __name__ == "__main__":  

    app = GameApp()
    app.run()
