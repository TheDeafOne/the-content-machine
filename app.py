from config import DEBUG_MODE
from src import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=DEBUG_MODE)
