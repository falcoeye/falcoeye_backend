rm -r data-dev.sqlite
rm -r migrations
export FLASK_APP=falcoeye
flask db init
flask db migrate
py=`ls migrations/versions/*.py`
sed -i '' 's/def upgrade()/import app\ndef upgrade()/' $py
flask db upgrade
