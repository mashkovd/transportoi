## references 
https://stackabuse.com/using-sqlalchemy-with-flask-and-postgresql/
https://stackoverflow.com/questions/4567089/hash-function-that-produces-short-hashes/40119266
https://flask-migrate.readthedocs.io/en/latest/
https://riptutorial.com/flask/example/5622/testing-a-json-api-implemented-in-flask

before start you need run follow command from backend container
1. flask db init
1. flask db migrate -m "Initial migration."
1. flask db upgrade
see - https://flask-migrate.readthedocs.io/en/latest/

for testing run follow command
1. python -m pytest