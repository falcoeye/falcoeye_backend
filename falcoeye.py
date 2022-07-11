import logging
import os

from dotenv import load_dotenv
from falcoeye_kubernetes import FalcoServingKube
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

# No real use for this now in falcoeye_backend. It is good for falcoeye_workflow only
artifact_registry = os.getenv("ARTIFACT_REGISTRY")
if artifact_registry:
    FalcoServingKube.set_artifact_registry(artifact_registry)

app = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run()
