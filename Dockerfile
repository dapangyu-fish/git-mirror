#=======================
# build github-mirror
# base: ubuntu:22.04
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
               && apt install -y wget curl gcc g++ make tini git git-lfs \
               && apt autoclean -y \
               && apt autoremove -y \
               && rm -rf /var/lib/apt/lists/*

#=======================
# Install miniconda3&python3
#=======================
RUN if [ $(uname -m) = "x86_64" ]; then \
      /bin/bash -c "wget -c https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
      chmod +x Miniconda3-latest-Linux-x86_64.sh && bash Miniconda3-latest-Linux-x86_64.sh -b -p /root/miniconda3 && \
      chmod +x /root/miniconda3/bin/activate && source /root/miniconda3/bin/activate && rm Miniconda3-latest-Linux-x86_64.sh"; \
    elif [ $(uname -m) = "arm64" ] || [ $(uname -m) = "aarch64" ]; then \
      /bin/bash -c "wget -c https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh && \
      chmod +x Miniconda3-latest-Linux-aarch64.sh && bash Miniconda3-latest-Linux-aarch64.sh -b -p /root/miniconda3 && \
      chmod +x /root/miniconda3/bin/activate && source /root/miniconda3/bin/activate && rm Miniconda3-latest-Linux-aarch64.sh"; \
    else \
      echo "Unknown platform: $(uname -m)"; \
      exit 1; \
    fi

ENV _CONDA_ROOT="/root/miniconda3"
ENV PATH=$PATH:$_CONDA_ROOT/bin
RUN ln -s $_CONDA_ROOT/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". $_CONDA_ROOT/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc && \
    find /root/miniconda3/ -follow -type f -name '*.a' -delete && \
    find /root/miniconda3/ -follow -type f -name '*.js.map' -delete && \
    /root/miniconda3/bin/conda clean -afy && \
    conda install python=3.11 -y

#=======================
# Install pip requirements
#=======================
RUN pip install -U pip
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN pwd && ls && ls && ls && ls && ls && pwd && ls && ls && pwd
COPY ./service /root/service


#=======================
# Set ssh for root login
#=======================
RUN touch /entrypoint.sh && chmod +x /entrypoint.sh && \
                            echo "#!/usr/bin/env bash" >> /entrypoint.sh && \
                            echo "git lfs install" >> /entrypoint.sh && \
                            echo "python -m gunicorn service:app --workers 10 --backlog 50 --bind 0.0.0.0:80" >> /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]

## docker build -t github-mirror:latest .
## docker build -t github-mirror:latest . --build-arg https_proxy=http://192.168.111.1:7890 --build-arg http_proxy=http://192.168.111.1:7890 --build-arg all_proxy=socks5://192.168.111.1:7890
