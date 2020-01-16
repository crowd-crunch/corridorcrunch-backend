# puzzlepieces

# development
Python 3.7 or newer.

Install Django. Anything 3.0.x.
``` bash
pip install Django
# OR
pip install -r requirements.txt

# Setup the database
python manage.py migrate

# Run the web server
python manage.py runserver 8000
```

# TODO:
- [] Needs to be moved to MariaDB/PostgresSQL vs sqlite since sqlite does table-locks for any changes/reads.
- [] Needs a bulk add for images...
- [] Needs a approval process for submitted images...
- [] Needs a prettification badly...
