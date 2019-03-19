FROM python:3.6

RUN apt-get update --fix-missing
RUN apt-get install -y apt-utils
RUN apt-get install -y build-essential \
ca-certificates \
git \
pkg-config \
python \
python-all-dev \
python-setuptools \
python-dev \
build-essential \
gfortran \
libatlas-base-dev \
libatlas3-base \
python-dev \
libjpeg-dev \
libxml2-dev \
libfreetype6-dev \
libpng-dev \
unzip \
zip \
zsh && \
rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -f -y postgresql-client

ENV TERM xterm


COPY ./bender_service/requirements.txt /requirements.txt

RUN pip install pip --upgrade
RUN pip install -r /requirements.txt

RUN curl https://cdn.rawgit.com/zsh-users/antigen/v1.0.4/antigen.zsh > /root/antigen.zsh
COPY ./scripts/.bashrc /root/.bashrc
COPY ./scripts/.zshrc /root/.zshrc
RUN /bin/zsh /root/.zshrc

COPY ./scripts/run_development.sh /run_development.sh
COPY ./scripts/run_packaged.sh /run_packaged.sh
COPY ./scripts/run_web.sh /run_web.sh
COPY ./scripts/run_web.sh /run_tests.sh

RUN pip install benderopt==1.3.1

COPY ./bender_service /usr/src/app
WORKDIR /usr/src/app
EXPOSE 8000
