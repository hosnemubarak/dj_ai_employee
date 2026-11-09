# DJ AI Employee

## PostgreSQL

Django loads PostgreSQL settings from the `.env` file in the project root.
Update `POSTGRES_PASSWORD` to match your PostgreSQL user:

| Variable | Default | Description |
| --- | --- | --- |
| `POSTGRES_DB` | `dj_ai_employee` | Database name |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | empty | Database password |
| `POSTGRES_HOST` | `localhost` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |

Install the Python dependencies and run migrations:

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
```
