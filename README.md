# falcoeye_backend

export FLASK_APP=falcoeye
export FLASK_CONFIG=development

flask db init
flask db upgrade
flask run
