#!/bin/bash
yum update -y
yum install cowsay java-1.8.0-openjdk* -y
yum install httpd -y
service httpd start
chkconfig httpd on

# next, add the extra disk space
mkfs -t ext4 /dev/xvdf
mkdir /space
mount /dev/xvdf /space

wget https://black-machine-340614.appspot.com/cacheavoid/HelloWorld.java -P /space
# should add a line here that compiles the file; may need to check
# file ownership permissions also
wget https://black-machine-340614.appspot.com/cacheavoid/hello.py -P /var/www/cgi-bin
chmod +x /var/www/cgi-bin/hello.py
cp /home/ec2-user/HelloWorld.java /space
wget https://black-machine-340614.appspot.com/cacheavoid/index.html -P /var/www/html
# instance is ready when hello.py or index.html is available
