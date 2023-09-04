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
               && apt install -y wget curl tini git git-lfs ssh vim \
               && apt autoclean -y \
               && apt autoremove -y \
               && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://code-server.dev/install.sh | sh

#=======================
# Set ssh for root login
#=======================
RUN touch /entrypoint.sh && chmod +x /entrypoint.sh && \
                            echo "#!/usr/bin/env bash" >> /entrypoint.sh && \
                            echo "git lfs install" >> /entrypoint.sh && \
                            echo "code-server --bind-addr=0.0.0.0:8080 --auth=none" >> /entrypoint.sh  && \
                            echo "if [ \$# -eq 0 ]; then" >> /entrypoint.sh && \
                            echo "  echo \"No command, running /bin/bash as default.\"" >> /entrypoint.sh && \
                            echo "  /bin/bash" >> /entrypoint.sh && \
                            echo "else" >> /entrypoint.sh && \
                            echo "  \"\$@\"" >> /entrypoint.sh && \
                            echo "fi" >> /entrypoint.sh
                            

EXPOSE 8080

ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]


## docker build -t github-mirror:latest .
## docker build -t github-mirror:latest . --build-arg https_proxy=http://192.168.111.1:7890 --build-arg http_proxy=http://192.168.111.1:7890 --build-arg all_proxy=socks5://192.168.111.1:7890