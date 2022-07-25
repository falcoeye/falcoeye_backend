#!/bin/sh

if [[ -z "${FALCOYE_PYTHON}" ]]; then
    echo "Set Python first using export FALCOYE_PYTHON=<path to activate file>"
    exit
fi

source $FALCOYE_PYTHON
export STREAMING_USER="streaming@falcoeye.io"
export STREAMING_PASSWORD="NO_TRUE_STREAMING"
export WORKFLOW_USER="workflow@falcoeye.io"
export WORKFLOW_PASSWORD="LIFE_IS_BUSY"
export FLASK_CONFIG="development"

echo "Running add roles script"
python add-roles.py
echo "Running register-accounts script"
python register-accounts.py
echo "Running add-workflow script"
python add-workflows.py
