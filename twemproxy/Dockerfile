FROM ubuntu:14.04

MAINTAINER "Kevin Cox <kevin@phhhoto.com>"

# TODO remove sudo

# add twemproxy source
# http://ppa.launchpad.net/twemproxy/stable/ubuntu/dists/trusty/main/binary-amd64/Packages
RUN echo "deb http://ppa.launchpad.net/twemproxy/stable/ubuntu trusty main" > /etc/apt/sources.list.d/twemproxy-stable-trusty.list
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F9DFF4ACC692420F
RUN apt-get update -y


# # for fun, run memcached in this container for testing
# RUN sudo apt-get install memcached -y
# RUN ps auxwww | grep memcached
# RUN sudo service memcached start
# RUN ps auxwww | grep memcached


# install twemproxy
RUN apt-get install twemproxy -y

# install AWS API tools
RUN apt-get install awscli -y

# install boto & related dependencies for auto-configuration
RUN apt-get install python-boto python-yaml -y

# install tools for debugging
RUN apt-get install telnet netcat nano lsof -y

# export AWS_DEFAULT_REGION=us-east-1

COPY nutcracker.yml /etc/

EXPOSE 6379 11211 22222

# CMD ["nutcracker", "-d", "-c", "/etc/nutcracker.yml", "-o", "/var/log/nutcracker.log"]
CMD ["nutcracker", "-c", "/etc/nutcracker.yml", "--verbose=11"]
