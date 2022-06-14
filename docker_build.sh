docker build . -t falcoeye-backend --build-arg SSH_KEY="$(cat ssh/id_rsa)"
