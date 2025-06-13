#!/bin/bash

# Build from source code
cmake -B ./build -S . -DCMAKE_PREFIX_PATH=$BUILD_PREFIX
cd ./build
make
cd ..

# Create target directory
mkdir -p ${PREFIX}/lib/arraymorph

# Install library
cp ./build/src/libarraymorph.so ${PREFIX}/lib/arraymorph/

# Install activation/deactivation scripts
mkdir -p ${PREFIX}/etc/conda/activate.d
mkdir -p ${PREFIX}/etc/conda/deactivate.d

cp activate.sh ${PREFIX}/etc/conda/activate.d/arraymorph-activate.sh
cp deactivate.sh ${PREFIX}/etc/conda/deactivate.d/arraymorph-deactivate.sh

# Make scripts executable
chmod +x ${PREFIX}/etc/conda/activate.d/arraymorph-activate.sh
chmod +x ${PREFIX}/etc/conda/deactivate.d/arraymorph-deactivate.sh
