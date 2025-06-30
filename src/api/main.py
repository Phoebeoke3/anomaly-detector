import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.controllers.api_controller import APIController

if __name__ == "__main__":
    app = APIController().create_app()
    app.run(debug=True, port=5000) 