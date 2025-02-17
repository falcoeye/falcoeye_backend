#docker build . -t falcoeye-backend --build-arg SSH_KEY="$(cat ssh/id_rsa)"
# Point your shell to minikube's Docker daemon
eval $(minikube docker-env)
docker build . -t falcoeye-backend
