FROM ubuntu:14.04

MAINTAINER "Kevin Cox <kevin@phhhoto.com>"

# TODO remove sudo

# add twemproxy source
# http://ppa.launchpad.net/twemproxy/stable/ubuntu/dists/trusty/main/binary-amd64/Packages
RUN echo "deb http://ppa.launchpad.net/twemproxy/stable/ubuntu trusty main" > /etc/apt/sources.list.d/twemproxy-stable-trusty.list
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F9DFF4ACC692420F
RUN apt-get update -y

# install twemproxy
RUN apt-get install twemproxy -y

# install boto & related dependencies for twemproxy auto-configuration script
RUN apt-get install python-setuptools python-requests python-yaml -y && easy_install boto3

# install twemproxy auto-configuration script
ADD nutcracker_aws_autoconf.py /usr/src/nutcracker_aws_autoconf.py
ADD nutcracker.yml /usr/src/nutcracker.yml

# install tools for debugging
# RUN apt-get install telnet netcat nano lsof -y
# install AWS API tools
# RUN apt-get install awscli -y

EXPOSE 6379 11211 22222

ADD run.sh /usr/local/bin/run
RUN chmod +x /usr/local/bin/run
CMD ["/usr/local/bin/run"]
