# # Base image
FROM docker:19.03-dind

# install kubectl and doctl
RUN apk add curl sudo wget bash gettext git && \
    curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl && \
    chmod +x ./kubectl && \
    mv ./kubectl /usr/local/bin/kubectl && \
    wget https://github.com/digitalocean/doctl/releases/download/v1.17.0/doctl-1.17.0-linux-amd64.tar.gz && \
    curl -sL https://github.com/digitalocean/doctl/releases/download/v1.38.0/doctl-1.38.0-linux-amd64.tar.gz | tar -xzv && \
    mkdir /root/doctl && \
    rm -rf doctl-1.17.0-linux-amd64.tar.gz && \
    mv doctl /usr/local/bin
