#!/bin/sh

# echo "Waiting for postgres..."

# while ! nc -z postgres 5432; do
#   sleep 0.1
# done

# echo "PostgreSQL started"

# flask db init
# flask db migrate
# flask db upgrade

#echo "Uncomment in the first deployment"
#cd initialization
#echo "Running add roles script"
#python add-roles.py
#echo "Running register-accounts script"
#python register-accounts.py
#echo "Running add-workflow script"
#python add-workflows.py

gunicorn -b 0.0.0.0:5000 falcoeye:app
