FROM python:3.7-buster

WORKDIR /usr/src/app

# Clone the master branch.
git clone https://github.com/Corridors-of-Time-Transcription/puzzlepieces.git
cd puzzlepieces

# Install requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Setup the database.
python manage.py makemigrations collector
python manage.py migrate

COPY . .

CMD [ "python", "manage.py", "runserver", "8000" ]