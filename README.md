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
# setup dev environment files
pz setupenv
# build the current dev version
pz lbuild
# start the dev stack
pz lup
# stop the dev stack
pz ldown
# build and reload  the dev stack (also starts if not running yet)
pz lreload
# view logs of running service
pz llogs
# attach to logs and follow running service
pz llogsf
# execute a command inside a container
pz lexec $docker_compose_service $commands
## so if you wanna run a shell inside the db it would look like this
pz lexec db bash
# run an arbitrary docker-compose command on the dev cluster
pz lcmd $command
```

if you do not want to mount the local `/src` directory into the running docker container, you can omit the prepended `l` on commands like so:

```bash
# setup dev environment files
pz setupenv
# build the current dev version
pz build
# start the dev stack
pz up
# stop the dev stack
pz down
# build and reload  the dev stack (also starts if not running yet)
pz reload
# view logs of running service
pz logs
# attach to logs and follow running service
pz logsf
# execute a command inside a container
pz exec $docker_compose_service $commands
## so if you wanna run a shell inside the db it would look like this
pz exec db bash
# run an arbitrary docker-compose command on the dev cluster
pz cmd $command
```

## manual setup
### Docker
```bash
# Dev
docker-compose -f build && docker-compose up -d

# Prod
docker-compose build && docker-compose up -d
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


# TODO:
- [ ] Needs a bulk add for images...
- [ ] Needs a approval process for submitted images...
- [ ] Needs a prettification badly...
- [ ] The 19 lore puzzle pieces should be filtered out of the results
- [ ] Dockerize app and figure out deployment
- [ ] update this readme lmao
