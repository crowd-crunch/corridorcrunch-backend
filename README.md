# puzzlepieces

<p align="center">
  <a href="https://discord.gg/WF94QBc">
    <img src="https://discordapp.com/assets/bb408e0343ddedc0967f246f7e89cebf.svg" alt="join us on discord">
  </a>
</p>
join us on discord!

# about
> spreadsheetstiny 2: corridors of sleeplessness

### PURPOSE:
The purpose of this site is to provide the most accurate database of puzzle piece transcriptions for anyone to use. Download link below.

### HOW DOES THIS WORK: 
Each image is transcribed several times by different people. Identical transcriptions increases the confidence that the transcription is accurate. Once the accuracy of an image's transcription has reached a high confidence rating, it will be added to our table of verified results. 

# development
## ez mode
requriements:
- [direnv](https://github.com/direnv/direnv)
- docker
- docker-compose


```bash
# allow the directory to load the custom commands
direnv allow
```
and then you can use the `pz` command to run the commands on a built version of the current code:

```bash
# learn about how to use the pz tool
pz help
```

## manual setup
### Docker
```bash
# setup env
cp ops/db-dev.env.example ops/db-dev.env
cp ops/development.env.example ops/development.env
# Dev
docker-compose -f ops/docker-compose.dev.yml build
docker-compose -f ops/docker-compose.dev.yml up
```

### local python
Python 3.7 or newer.

Install Django. Anything 3.0.x.
``` bash
pip install Django
pip install mysqlclient
# OR
pip install -r requirements.txt

# Setup the database
python manage.py migrate

# Run the web server
python manage.py runserver 8000
```


