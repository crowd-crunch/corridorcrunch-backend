# puzzlepieces
[JOIN THE DISCORD HERE, FRIEND](https://discord.gg/WF94QBc)



[what? check the draft of the frontend to get a better idea what this is about](#about)

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
- [ ] Needs to be moved to MariaDB/PostgresSQL vs sqlite since sqlite does table-locks for any changes/reads.
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
