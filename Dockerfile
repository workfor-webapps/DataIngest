### 1. Get Linux
FROM centos:8

# Install Java
#RUN yum update -y \
#&& yum groupinstall 'Development Tools'\
#&& yum install java-1.8.0-openjdk -y \
#&& yum clean all \
#&& rm -rf /var/cache/yum

# Set JAVA_HOME environment var
#ENV JAVA_HOME="/usr/lib/jvm/jre-openjdk"

# Install Python

#RUN yum install python3 -y \
#&& pip3 install --upgrade pip setuptools wheel \
#&& if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi \
#&& if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi \
#&& yum clean all \
#&& rm -rf /var/cache/yum

# install conda
RUN yum -y update \
    && yum -y install curl bzip2 \
    && curl -sSL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -bfp /usr/local/ \
    && rm -rf /tmp/miniconda.sh \
    && conda install -y python=3.9 \
    && conda update conda \
    && conda install pip \
    && conda clean --all --yes \
    && rpm -e --nodeps curl bzip2 \
    && yum clean all
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"

### RUN pip install --trusted-host pypi.python.org flask
COPY ./ /app/.
WORKDIR /app

RUN pip install -r requirements.txt
RUN yum makecache --refresh
RUN yum -y install pkgconf
RUN yum install poppler-utils
# install libs
RUN conda install -y pytorch torchvision torchaudio cpuonly -c pytorch
RUN python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'
RUN pip install torch==1.11.0+cpu torchvision==0.12.0+cpu torchaudio==0.11.0+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html
RUN pip install 'git+https://github.com/facebookresearch/detectron2.git'
RUN pip install layoutparser "layoutparser[ocr]"
RUN pip install "camelot-py[base]"
RUN pip install pdf2doi


#### OPTIONAL : 4. SET JAVA_HOME environment variable, uncomment the line below if you need it
#### ENV JAVA_HOME="/usr/lib/jvm/java-1.8-openjdk"

ENV FLASK_APP main.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 8080

EXPOSE 8080

CMD ["python3", "main.py"]