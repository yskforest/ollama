FROM ubuntu:24.04

# Install core utilities
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
&& rm -rf /var/lib/apt/lists/*

# Prepare keyrings for Charm repository
RUN mkdir -p /etc/apt/keyrings
RUN curl -fsSL https://repo.charm.sh/apt/gpg.key | gpg --dearmor -o /etc/apt/keyrings/charm.gpg
RUN echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" > /etc/apt/sources.list.d/charm.list
RUN apt-get update && apt-get install -y \
    crush \
&& rm -rf /var/lib/apt/lists/*

# Align ubuntu user UID/GID with host
ARG UID=1000
ARG GID=1000
RUN groupmod -g ${GID} ubuntu && \
    usermod -u ${UID} -g ${GID} ubuntu && \
    chown -R ubuntu:ubuntu /home/ubuntu

USER ubuntu

# Install Opencode
RUN curl -fsSL https://opencode.ai/install | bash

CMD ["/bin/bash"]
