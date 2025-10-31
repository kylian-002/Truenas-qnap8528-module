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

echo "[3/3] Locating production kernel headers..."
# Search for either versioned or unversioned production headers
KERN_HEADERS=$(find /usr/src -maxdepth 1 -type d \
    \( -name "linux-headers-*-production+truenas" -o -name "linux-headers-truenas-production-amd64" \) \
    | head -n 1)

if [ -z "$KERN_HEADERS" ]; then
    echo "Error: Could not find production kernel headers in /usr/src"
    exit 1
fi

echo "Using kernel headers: $KERN_HEADERS"

echo "[4/4] Building kernel module..."
cd build/qnap8528/src
make -C "$KERN_HEADERS" M=$(pwd)

cd ../../..
if [ -f build/qnap8528/src/qnap8528.ko ]; then
    cp build/qnap8528/src/qnap8528.ko output/
    echo "Build complete. Module copied to ./output/qnap8528.ko"
else
    echo "Error: qnap8528.ko not found in src/. Build may have failed."
    exit 1
fi

