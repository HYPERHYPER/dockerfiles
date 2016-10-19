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
RUN apt-get install python-setuptools python-yaml -y && easy_install boto3

# set AWS_DEFAULT_REGION
# RUN set-aws-region.sh
# RUN apt-get install curl -y
# RUN export AWS_DEFAULT_REGION=$(curl -s 169.254.169.254/latest/meta-data/placement/availability-zone | sed 's/.$//')
ENV AWS_DEFAULT_REGION=us-east-1

# install twemproxy auto-configuration script
ADD nutcracker_aws_autoconf.py /usr/src/nutcracker_aws_autoconf.py
ADD nutcracker.yml /usr/src/nutcracker.yml

# run twemproxy auto-configuration script
RUN python /usr/src/nutcracker_aws_autoconf.py /usr/src/nutcracker.yml /etc/nutcracker.yml


# install tools for debugging
RUN apt-get install telnet netcat nano lsof -y
# install AWS API tools
RUN apt-get install awscli -y


# COPY nutcracker.yml /etc/

EXPOSE 6379 11211 22222

# CMD ["nutcracker", "-d", "-c", "/etc/nutcracker.yml", "-o", "/var/log/nutcracker.log"]
CMD ["nutcracker", "-c", "/etc/nutcracker.yml", "--verbose=11"]
