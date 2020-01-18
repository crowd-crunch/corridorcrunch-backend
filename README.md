# puzzlepieces
[JOIN THE DISCORD HERE, FRIEND](https://discord.gg/WF94QBc)



[what? check the draft of the frontend to get a better idea what this is about](#about)

# development
## ez mode
requriements:
- direnv
- docker
- docker-compose

if you're on linux you can use tooling to make your life easier[direnv](https://github.com/direnv/direnv)


```bash
# allow the directory to load the custom commands
direnv allow
```

and then you can use the `pz` command to do different things

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

# about
> the following is a draft of the frontend content, added here to hopefully convey the idea of the project a bit better
### PURPOSE:
The purpose of this site is to provide the most accurate database of puzzle piece transcriptions for anyone to use. Download link below.

### HELP WANTED:
Puzzle piece images needed! Click here to learn how to find your puzzle piece in-game. Only screenshots from the game will be utilized. Upload your images to the #corridors-of-time-images channel on the RaidSecrets Discord server: https://discord.gg/Tue4PMf

### INSTRUCTIONS: 
Transcribe the image below using https://tjl.co/corridors-of-time/.
Copy and paste the RAW JSON output into this box and click submit: 

### BAD PHOTOS:
If an image is blurry, covered, cropped off, too small, doesn't load, or is unreadable for any reason, please click "Flag as Bad Photo" and it will be removed from circulation. Images with rotations that cannot be determined should also be flagged.

### IMAGE ROTATION: 
All puzzle pieces should be transcribed as they appear when room's entrance is behind the player. You can easily verify the image rotation by using the outer pillars as landmarks. [See this rotation landmarks guide.(https://cdn.discordapp.com/attachments/667254133589540877/667353728365363200/Rotation_Landmarks.png)]

### HOW DOES THIS WORK: 
Each image is transcribed several times by different people. Identical transcriptions increases the confidence that the transcription is accurate. Once the accuracy of an image's transcription has reached a high confidence rating, it will be added to our table of verified results. 

### EXPORT RESULTS:
Click here to download all verified puzzle piece transcriptions (.CSV). This link will update with new data every 15 minutes. The results can be cross-referenced or merged with other datasets.

### ABOUT VALIDATION: 
<explain how data is validated>
