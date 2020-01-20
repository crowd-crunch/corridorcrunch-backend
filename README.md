# puzzlepieces

<p align="center">
  <a href="https://discord.gg/WF94QBc">
    <img src="https://discordapp.com/assets/bb408e0343ddedc0967f246f7e89cebf.svg" alt="join us on discord">
  </a>
</p>
join us on discord!

# And we're done
It's been a blast, thank you to everyone who transcribed, you're the true GOATs!  
Final csv export files are in this repo  
We had over 26,000 image URLs submitted, almost 51,000 transcriptions, of which almost 29,000 were used to find trusted transcriptions, and found over 1,400 trusted transcriptions.  
If there is one regret, it is that we did not catch an important bug in our frontend API earlier, which means all transcriptions submitted through the "pretty" front-end never were used to find "solutions". We could and would have fixed that in a couple more hours, and then the puzzle got solved.  

You all ROCK!
 
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
pz restart
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
- [ ] Needs a approval process for submitted images...
- [ ] The 19 lore puzzle pieces should be filtered out of the results
- [ ] Dockerize app and figure out deployment
- [ ] update this readme lmao

# Rough guide to spinning this up as a dev server from scratch. Is missing notes on lup (mount local dir) and general iteration loop
Assuming a fresh Ubuntu 18.04 host. This also works in Win10 2004 with WSL2 docker and Docker for Desktop

From the ~ directory, here assuming a non-root user

```
sudo apt update  
sudo apt upgrade  
```
Restart services automatically and keep local versions when asked  

Some of these upgrades require reboot, let's do that now  
```sudo reboot  

sudo apt install direnv  
sudo apt install docker  
sudo apt install docker-compose  

sudo usermod -aG docker $USER  
```

Create .vimrc  
```
vi .vimrc  
set noexpandtab  
set background=dark  
```

Add to the very end of .bashrc  
```
vi .bashrc  
eval "$(direnv hook bash)"  
LS_COLORS=$LS_COLORS:'di=1;44:' ; export LS_COLORS  
```

Log out and back in  

Minimal git setup  
```
git config --global user.name "*Your name*"  
git config --global user.email *Your email*  
git config --global core.autocrlf input  
```

If you just want to play with it and you don't intend to submit code:  
```
git clone git@github.com:Corridors-of-Time-Transcription/puzzlepieces.git  
```

If you DO want to submit code and PRs, please:  
- Fork to your own repo  
- On your dev server, create keys
```
ssh-keygen -t ed25519 -o
cat .ssh/id_ed25519.pub
```

Go to your github settings, SSH and GPG keys, and set this as a "New SSH key". Title could be "Puzzle Test Server" or something descriptive.  

Get the URL for the develop branch (NOT master) from your github fork, "Clone with SSH", and  
```
git clone *URL github gave you*  
cd puzzlepieces  
git remote add upstream git@github.com:Corridors-of-Time-Transcription/puzzlepieces.git  
git remote -v  
```

Once you have the code from either git:
```
cd ~/puzzlepieces 
direnv allow  
```

Now edit docker files depending on how you'll access your machine. Yes we know our docker routing is shonky. We invite help! Get in touch with @ebuch.  

So, figure out how you access your dev server. If it's through localhost, no changes needed. If it's through another IP or a name, you'll need that IP or that name, and we'll tell docker about it. Notably that's what you use to get to it, which may not be its local IP.  

```
cd ops  
vi docker-compose.dev.yml  
```

Find "VIRTUAL_HOST=localhost" and change to "VIRTUAL_HOST=*whatever-IP-or-name-you-use-to-connect*"  

Rinse repeat for docker-compose.dev.local.yml  

Environment files next. Same thing here, docker help appreciated  
```
cp db-dev.env.example db-dev.env  
cp production.env.example production.env  
cp development.env.example development.env  

cd ..  
git update-index --assume-unchanged ops/docker-compose.dev.local.yml  
git update-index --assume-unchanged ops/docker-compose.dev.yml  
```

Back to puzzlepieces and spin this up. We're using pz, which is just a little script wrapped around docker  

```
pz build  
pz up  
```

You should be able to get to http://*your-machine*, and from CLI  ```docker ps``` should show you three containers  

Syncing with upstream master, assuming your own fork and a fork and branch model 

```
git checkout develop
git pull upstream develop 
git push  
```

And get the changes into your running docker instances  

```
pz build  
pz up
```

Similar for "master" which is where the live version was going to live.


If you have PRs to contribute, not that we do this now any more, it'd be:

```
git checkout develop
git checkout -b *new-feature-branch*
```

Lots of coding occurs, testing, etc

```
git commit
git checkout develop
git pull upstream develop
git checkout *new-feature-branch*
git rebase develop
git push --set-upstream origin *new-feature-branch*
```

The DB for the dev environment is named "puzzlepieces", the user is "puzzler" and the password "puzzling"  

