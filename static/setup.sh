#!/bin/bash
apt update
apt install python3 apache2 -y
wget https://black-machine-340614.ew.r.appspot.com/cacheavoid/apache2.conf
apache2ctl restart
mv apache2.conf /etc/apache2/apache2.conf
wget https://black-machine-340614.ew.r.appspot.com/cacheavoid/CalcVar.py
cp CalcVar.py /var/www/html/CalcVar.py
chmod 755 /var/www/html/CalcVar.py
a2enmod cgi
service apache2 restart

