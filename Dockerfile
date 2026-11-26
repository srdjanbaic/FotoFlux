FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Belgrade

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        software-properties-common \
        ca-certificates \
        tzdata \
        gnupg \
        gpg-agent \
        dirmngr \
        build-essential \
        binutils \
        patchelf \
        file \
        dpkg-dev \
        fakeroot \
        desktop-file-utils \
        libgl1 \
        libglib2.0-0 && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.11 \
        python3.11-dev \
        python3.11-venv \
        python3.11-tk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
