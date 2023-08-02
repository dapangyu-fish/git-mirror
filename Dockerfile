#=======================
# build github-mirror
# base: python:3.11.4-slim
# user：root
# workspace：/root
#=======================

FROM python:3.11.4-slim
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
RUN pwd
COPY ./service /root/service
COPY ./tasks /root/tasks
ADD ./service/sync_repo.sh /usr/bin/sync_repo
RUN chmod +x /usr/bin/sync_repo
RUN mkdir -p /etc/supervisor/conf.d && ls
RUN mkdir -p /var/log/supervisor/conf.d
COPY supervisor/supervisord.conf /etc/supervisor/supervisord.conf
COPY supervisor/conf.d/git-mirror.conf /etc/supervisor/conf.d/git-mirror.conf


#=======================
# Set ssh for root login
#=======================
RUN touch /entrypoint.sh && chmod +x /entrypoint.sh && \
                            echo "#!/usr/bin/env bash" >> /entrypoint.sh && \
                            echo "git lfs install" >> /entrypoint.sh && \
                            echo "supervisord --nodaemon -c /etc/supervisor/supervisord.conf" >> /entrypoint.sh  && \
                            echo "if [ \$# -eq 0 ]; then" >> /entrypoint.sh && \
                            echo "  echo \"No command, running /bin/bash as default.\"" >> /entrypoint.sh && \
                            echo "  /bin/bash" >> /entrypoint.sh && \
                            echo "else" >> /entrypoint.sh && \
                            echo "  \"\$@\"" >> /entrypoint.sh && \
                            echo "fi" >> /entrypoint.sh


EXPOSE 8000

ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]


## docker build -t github-mirror:latest .
## docker build -t github-mirror:latest . --build-arg https_proxy=http://192.168.111.1:7890 --build-arg http_proxy=http://192.168.111.1:7890 --build-arg all_proxy=socks5://192.168.111.1:7890