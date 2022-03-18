### 1. Get Linux
FROM debian:latest

RUN apt-get -qq update && apt-get -qq -y install curl bzip2 \
    && apt-get -qq install ffmpeg libsm6 libxext6  -y \
    && curl -sSL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -bfp /usr/local \
    && rm -rf /tmp/miniconda.sh \
    && conda install -y python=3.9 \
    && conda update conda \
    && conda install pip \
    && conda install git\
    && apt-get -qq -y remove curl bzip2 \
    && apt-get -qq -y autoremove \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* /var/log/dpkg.log \
    && conda clean --all --yes

ENV PATH /opt/conda/bin:$PATH
RUN apt-get -qq update && apt-get -qq -y install gcc cmake build-essential
RUN apt-get -qq install pkg-config 
RUN apt-get -qq install poppler-utils

### RUN pip install --trusted-host pypi.python.org flask
COPY ./ /app/.
WORKDIR /app

RUN pip install -r requirements.txt

# install libs

RUN pip install torch==1.11.0+cpu torchvision==0.12.0+cpu torchaudio==0.11.0+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html
RUN pip install 'git+https://github.com/facebookresearch/detectron2.git'
RUN pip install layoutparser "layoutparser[ocr]"
RUN pip install "camelot-py[base]"
RUN pip install pdf2doi

ENV FLASK_APP main.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 8080

EXPOSE 8080

CMD ["python3", "main.py"]