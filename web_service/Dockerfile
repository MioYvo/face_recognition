FROM ccr.ccs.tencentyun.com/h3c-cpc/face_rec

COPY . /web_service/

#RUN sed -i "s/deb.debian.org/mirrors.aliyun.com/g" /etc/apt/sources.list  && \
#    sed -i "s/security.debian.org/mirrors.aliyun.com/g" /etc/apt/sources.list && \
#    apt update &&\
#    apt install -y netcat && \
    # change timezone to Asia/Shanghai
#    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
#    echo "Asia/Shanghai" > /etc/timezone && \
#    dpkg-reconfigure -f noninteractive tzdata && \
    # install app
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r /web_service/requirements.txt
    # do clean
#    apk del --no-cache tzdata

WORKDIR /web_service
CMD ["python", "app.py"]
