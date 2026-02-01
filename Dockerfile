FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    curl wget unzip git \
    && rm -rf /var/lib/apt/lists/*

# Update ubuntu user to match host UID/GID
ARG UID=1000
ARG GID=1000
RUN groupmod -g ${GID} ubuntu && \
    usermod -u ${UID} -g ${GID} ubuntu && \
    chown -R ubuntu:ubuntu /home/ubuntu

USER ubuntu

RUN curl -fsSL https://opencode.ai/install | bash

CMD ["/bin/bash"]
