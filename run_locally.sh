#!/bin/sh

if [[ -z "${FALCOYE_PYTHON}" ]]; then
    echo "Set Python first using export FALCOYE_PYTHON=<path to activate file>"
    exit
fi

source $FALCOYE_PYTHON

export FLASK_APP="falcoeye"
export GOOGLE_APPLICATION_CREDENTIALS="$PWD/google/key.json"
export DATABASE_URL="sqlite:///$PWD/data-dev.sqlite"
export FLASK_CONFIG="development"
export STREAMING_USER="streaming@falcoeye.io"
export STREAMING_PASSWORD="NO_TRUE_STREAMING"
export WORKFLOW_USER="workflow@falcoeye.io"
export WORKFLOW_PASSWORD="LIFE_IS_BUSY"

echo "Initializing db"
flask db init
echo "Migrating db"
flask db migrate
echo "Upgrading db"
flask db upgrade >& /dev/null


gunicorn -b 0.0.0.0:5000 falcoeye:app
