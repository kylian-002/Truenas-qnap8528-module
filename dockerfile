FROM debian:trixie

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    make \
    libelf-dev \
    bc \
    dwarves \
    flex \
    bison \
    && rm -rf /var/lib/apt/lists/*