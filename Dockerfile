### 1. Get Linux
FROM centos:8

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

### RUN pip install --trusted-host pypi.python.org flask
COPY ./ /app/.
WORKDIR /app

ENV FLASK_APP main.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 8080

RUN pip install -r requirements.txt
####
#### OPTIONAL : 4. SET JAVA_HOME environment variable, uncomment the line below if you need it
##ENV JAVA_HOME="/usr/lib/jvm/java-1.8-openjdk"
####
EXPOSE 8080

CMD ["python3", "main.py"]