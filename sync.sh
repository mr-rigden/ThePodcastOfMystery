#!/bin/bash

source /home/jason/oak/ThePodcastOfMystery/venv/bin/activate
python pom.py config.json
rsync -avzh  /home/jason/oak/ jason@45.33.58.35:/home/jason/oak
