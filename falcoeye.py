import logging
import os

from dotenv import load_dotenv
from flask_migrate import Migrate

from app import create_app, db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run()
