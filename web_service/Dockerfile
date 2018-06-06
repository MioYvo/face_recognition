FROM python:3-slim

COPY . /generator/

RUN sed -i "s/deb.debian.org/mirrors.aliyun.com/g" /etc/apt/sources.list  && \
    apt update &&\
    apt install -y netcat && \
    # change timezone to Asia/Shanghai
#    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata && \
    # install app
    pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r /generator/requirements.txt
    # do clean
#    apk del --no-cache tzdata

WORKDIR /generator
CMD ["./start.sh"]
