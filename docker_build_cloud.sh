docker build . -t us-central1-docker.pkg.dev/${PROJECT_ID}/falcoeye-repo/falcoeye-backend --build-arg SSH_KEY="$(cat ssh/id_rsa)"
