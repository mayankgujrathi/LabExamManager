#!/bin/bash
# Script used to setup a django server require "dir name" and "apache2 conf"
#  __  __                         _       ____        _           _   _     _
# |  \/  | __ _ _   _  __ _ _ __ | | __  / ___|_   _ (_)_ __ __ _| |_| |__ (_)
# | |\/| |/ _` | | | |/ _` | '_ \| |/ / | |  _| | | || | '__/ _` | __| '_ \| |
# | |  | | (_| | |_| | (_| | | | |   <  | |_| | |_| || | | | (_| | |_| | | | |
# |_|  |_|\__,_|\__, |\__,_|_| |_|_|\_\  \____|\__,_|/ |_|  \__,_|\__|_| |_|_|
#               |___/                              |__/

# installing dependencies
echo installing dependencies...
sudo apt install ufw apache2 libapache2-mod-wsgi-py3 zip unzip -y
echo done

echo configuring firewall
sudo ufw default allow outgoing
sudo ufw default deny incoming
sudo ufw allow ssh
sudo ufw allow http/tcp
sudo ufw enable
sudo ufw status
echo done

echo configuring apache2 with $2
sudo cp $2 /etc/apache2/sites-available/
sudo a2ensite $2
sudo a2dissite 000-default.conf
echo done

echo configuring setting premissions to $1
sudo chown :www-data $1/db.sqlite3
sudo chmod 775 $1/db.sqlite3
sudo chown -R :www-data $1/media/
sudo chmod -R 775 $1/media/
sudo chown :www-data $1/
sudo chmod 775 $1/
echo done

echo restarting server
sudo service apache2 restart
echo done
