#!/bin/sh
#Use "sudo docker exec -it bot /bin/bash" to connect to container.
#Use "sudo docker attach bot" for attach terminal.
cur_dir=$(exec pwd)
echo "$cur_dir"
case "$1" in
    install)
            echo "Install bot from Github"
            rm -r FamilySchedulerBot
            git clone https://github.com/JestemGrisza/FamilySchedulerBot.git
            cp Dockerfile ./FamilySchedulerBot/
            cd FamilySchedulerBot || exit 1
            sudo docker build -t fml_schd .
            sudo docker image ls
            echo "."
             ;;
    stop)
            echo "Stop bot"
            sudo docker stop bot
            echo "."
           ;;
    start)
            echo "Start bot"
            sudo docker stop bot
            sudo docker run --name bot -d --rm -v "$cur_dir":/usr/src/fml_schd/db fml_schd
            sudo docker ps
            echo "."
            ;;
    *)
          echo "Usage: bot.sh install|stop|start"
          exit 1
          ;;
esac