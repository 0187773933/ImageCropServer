FROM ubuntu:latest

RUN apt-get upgrade
RUN apt-get update
RUN apt-get install software-properties-common -y
RUN apt-get install build-essential -y
RUN apt-get install net-tools -y
RUN apt-get install python3-pip -y
RUN apt-get install python3-dev -y
RUN apt-get install libssl-dev -y
RUN apt-get install libffi-dev -y
RUN apt-get install cargo -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install tzdata -y
RUN apt-get install sudo -y
RUN apt-get install curl -y
RUN apt-get install wget -y
RUN apt-get install git -y

RUN apt-get install python3-setuptools -y
RUN apt-get install python3-smbus -y
RUN apt-get install python3-numpy -y
RUN apt-get install python3-scipy -y
RUN apt-get install libncursesw5-dev -y
RUN apt-get install libgdbm-dev -y
RUN apt-get install libc6-dev -y
RUN apt-get install zlib1g-dev -y
RUN apt-get install libsqlite3-dev -y
RUN apt-get install tk-dev -y
RUN apt-get install libssl-dev -y
RUN apt-get install openssl -y
RUN apt-get install libffi-dev -y
RUN apt-get install libbz2-dev -y
RUN apt-get install libreadline-dev -y
RUN apt-get install llvm -y
RUN apt-get install libncurses5-dev -y
RUN apt-get install xz-utils -y
RUN apt-get install tk-dev -y
RUN apt-get install libxml2-dev -y
RUN apt-get install libxmlsec1-dev -y
RUN apt-get install liblzma-dev -y
RUN apt-get install libatlas-base-dev -y
RUN apt-get install libopenjp2-7 -y
RUN apt-get install libtiff5 -y
RUN apt-get install apt-transport-https -y
RUN apt-get install ca-certificates  -y
RUN update-ca-certificates -f
RUN mkdir -p /etc/pki/tls/certs
RUN cp /etc/ssl/certs/ca-certificates.crt /etc/pki/tls/certs/ca-bundle.crt

ENV TZ="US/Eastern"
RUN echo "US/Eastern" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
ARG USERNAME="morphs"
ARG PASSWORD="asdfasdf"
RUN useradd -m $USERNAME -p $PASSWORD -s "/bin/bash"
RUN mkdir -p /home/$USERNAME
RUN chown -R $USERNAME:$USERNAME /home/$USERNAME
RUN usermod -aG sudo $USERNAME
RUN echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER $USERNAME
WORKDIR /home/$USERNAME
RUN mkdir -p /home/$USERNAME/SHARING
RUN sudo chown -R $USERNAME:$USERNAME /home/$USERNAME/SHARING

ENV PYTHON_VERSION 3.7.3
RUN git clone https://github.com/pyenv/pyenv.git /home/$USERNAME/.pyenv
ENV PYENV_ROOT /home/$USERNAME/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
RUN /home/$USERNAME/.pyenv/bin/pyenv install $PYTHON_VERSION
RUN /home/$USERNAME/.pyenv/bin/pyenv global $PYTHON_VERSION
RUN /home/$USERNAME/.pyenv/bin/pyenv rehash

RUN python -m pip install -U pip
RUN python -m pip install -U Pillow
RUN python -m pip install -U sanic
RUN python -m pip install -U pytz
RUN python -m pip install -U python-dateutil

COPY ./server.py /home/$USERNAME/server.py
ENTRYPOINT [ "python" , "server.py" ]