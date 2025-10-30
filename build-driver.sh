#!/bin/bash
set -e

echo "[1/3] Setting up build environment..."
mkdir -p build output

echo "[2/3] Cloning repository..."
if [ ! -d build/qnap8528 ]; then
    git clone https://github.com/0xGiddi/qnap8528.git build/qnap8528
else
    cd build/qnap8528
    git pull
    cd ../..
fi

echo "[3/3] Building kernel module..."
cd build/qnap8528/src

make -C /usr/src/linux-headers-truenas-production-amd64 M=$(pwd)

cd ../../..
if [ -f build/qnap8528/src/qnap8528.ko ]; then
    cp build/qnap8528/src/qnap8528.ko output/
    echo "Build complete. Module copied to ./output/qnap8528.ko"
else
    echo "Error: qnap8528.ko not found in src/. Build may have failed."
    exit 1
fi