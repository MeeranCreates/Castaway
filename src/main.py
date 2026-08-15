import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)


from src.engine.app import GameApp

if __name__ == "__main__":  

    app = GameApp()
    app.run()
