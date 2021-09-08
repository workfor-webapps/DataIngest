### 1. Get Linux
FROM centos:8

# Setup python and java and base system
#ENV DEBIAN_FRONTEND noninteractive
#ENV LANG=en_US.UTF-8

### 2. Get Java via the package manager
#RUN apt-get update && \
#  apt-get install -y software-properties-common && \
#  add-apt-repository ppa:deadsnakes/ppa && \
#  apt-get update && \
#  apt-get install -q -y openjdk-8-jdk python3.8 python3-pip language-pack-en
### 3. Get Python, PIP

# Install Java
RUN yum update -y \
&& yum install java-1.8.0-openjdk -y \
&& yum clean all \
&& rm -rf /var/cache/yum

# Set JAVA_HOME environment var
ENV JAVA_HOME="/usr/lib/jvm/jre-openjdk"

# Install Python
RUN yum install python3 -y \
&& pip3 install --upgrade pip setuptools wheel \
&& if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi \
&& if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi \
&& yum clean all \
&& rm -rf /var/cache/yum

#apt-get update && \
#  apt-get upgrade -y && \

#RUN pip3 install --upgrade pip requests

#RUN if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
#if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
#rm -r /root/.cache

### RUN pip install --trusted-host pypi.python.org flask
COPY ./ /app/.
WORKDIR /app

ENV FLASK_APP main.py
ENV FLASK_RUN_HOST 127.0.0.1
ENV FLASK_RUN_PORT 8080

RUN pip install -r requirements.txt
####
#### OPTIONAL : 4. SET JAVA_HOME environment variable, uncomment the line below if you need it

##ENV JAVA_HOME="/usr/lib/jvm/java-1.8-openjdk"

####
EXPOSE 8080

CMD ["python3", "main.py"]