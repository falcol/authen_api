# FASTAPI
## Alembic
[link alembic]([https://](https://testdriven.io/blog/fastapi-sqlmodel/#async-sqlmodel))\
alembic init -t async migrations\
alembic revision --autogenerate -m "init"\
alembic upgrade head

## If create new model
Import model to env.py in migrations

## Run
1. Create postgres DB fastapi and change DATABASE_URL
2. Run migrations
3. cd fastapi
4. python -m venv venv
5. pip install -r requirements.txt
6. python src/main.py
