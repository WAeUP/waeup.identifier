FROM ubuntu:12.04

MAINTAINER Uli Fouquet <uli@waeup.org>

RUN apt-get update && apt-get install -y
# need apt-add-repository
RUN apt-get install python-software-properties -y

RUN add-apt-repository ppa:ansible/ansible -y    # get recent ansible
RUN add-apt-repository ppa:fkrull/deadsnakes -y  # get python3.4

RUN apt-get update
RUN apt-get install ansible -y

# install python3.4
RUN apt-get install python3.4 python3.4-dev -y
RUN apt-get install python-pip python-virtualenv -y

CMD /bin/bash
