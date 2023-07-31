#=======================
# build github-mirror
# base: python:3.11.4-slim
# user：root
# workspace：/root
#=======================

FROM ubuntu:22.04
USER root
WORKDIR /root
ENV DEBIAN_FRONTEND=noninteractive

#=======================
# install apt
#=======================
RUN apt update && apt upgrade -y \
               && apt install -y wget curl tini git git-lfs \
               && apt autoclean -y \
               && apt autoremove -y \
               && rm -rf /var/lib/apt/lists/*


#=======================
# Install pip requirements
#=======================
RUN pip install -U pip
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
COPY ./service /root/service
ADD ./service/sync_repo.sh /usr/bin/sync_repo
RUN chmod +x /usr/bin/sync_repo
RUN mkdir -p /var/log/supervisor/
COPY supervisor/supervisord.conf /etc/supervisor/supervisord.conf


#=======================
# Set ssh for root login
#=======================
RUN touch /entrypoint.sh && chmod +x /entrypoint.sh && \
                            echo "#!/usr/bin/env bash" >> /entrypoint.sh && \
                            echo "git lfs install" >> /entrypoint.sh && \
                            echo "python -m gunicorn service:app --workers 10 --backlog 50 --timeout 3600 --bind 0.0.0.0:80" >> /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]


## docker build -t github-mirror:latest .
## docker build -t github-mirror:latest . --build-arg https_proxy=http://192.168.111.1:7890 --build-arg http_proxy=http://192.168.111.1:7890 --build-arg all_proxy=socks5://192.168.111.1:7890