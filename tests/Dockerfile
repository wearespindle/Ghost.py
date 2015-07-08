FROM voipgrid/ubuntu-12.04-pyqt5:0.1
MAINTAINER VoIPGRID <dev@voipgrid.nl>

# Install utils so other installations run more smoothly.
RUN apt-get update && apt-get install -y apt-utils python-software-properties sudo

# Install packages
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    dbus \
    vim \
    python \
    python-dev \
    python-distribute \
    python-pip \
    libmysqlclient-dev \
    python-mysqldb \
    git \
    build-essential \
    ipython \
    xvfb \
    xfonts-100dpi

# Base config.
RUN useradd docker
RUN echo "ALL ALL = (ALL) NOPASSWD: ALL" >> /etc/sudoers
WORKDIR /home/docker
ENV HOME /home/docker

RUN pip install -U pip # make sure the newest version of pip is used.
# Install python pip packages.
ADD requirements.txt $HOME/requirements.txt
RUN pip install -r $HOME/requirements.txt
RUN rm $HOME/requirements.txt

# Expose the port of Django dev server.
EXPOSE 8000

# Switch to docker user.
RUN chown -R docker:docker $HOME/
USER docker

# Install ipdb.
RUN sudo pip install ipdb
ENV QT_GRAPHICSSYSTEM native
WORKDIR /home/docker/ghostrunner

# Set bash as default command for this image.
CMD ["/bin/bash"]
