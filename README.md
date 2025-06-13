# ArrayMorph

[![Build Status](https://github.com/ICICLE-ai/arraymorph/actions/workflows/build.yml/badge.svg)](https://github.com/ICICLE-ai/arraymorph/actions/workflows/build.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ArrayMorph is a software to manage array data stored on cloud object storage efficiently. It supports both HDF5 C++ API and h5py API. The data returned by h5py API is numpy arrays. By using h5py API, users can access array data stored on the cloud and feed the read data into machine learning pipelines seamlessly.

**Tag**: CI4AI

---

# How-To Guides

## Install dependencies

It is recommended to use Conda (and conda-forge) for managing dependencies.

1. Install [Miniconda](https://docs.anaconda.com/miniconda/)  
2. Create and activate environment with dependencies:
   ```bash
   conda create -n arraymorph conda-forge::gxx=9
   conda activate arraymorph
   conda install -n arraymorph cmake conda-forge::hdf5=1.14.2 conda-forge::aws-sdk-cpp conda-forge::azure-storage-blobs-cpp conda-forge::h5py
   ```

## Install ArrayMorph via ArrayMorph local conda package
   ```bash
   git clone https://github.com/ICICLE-ai/arraymorph.git
   cd arraymorph/arraymorph_channel
   conda index .
   conda install -n arraymorph arraymorph -c file://$(pwd) -c conda-forge
   ```

## Install ArryMorph from source code

### Build ArrayMorph
```bash
git clone https://github.com/ICICLE-ai/arraymorph.git
cd arraymorph/arraymorph
cmake -B ./build -S . -DCMAKE_PREFIX_PATH=$CONDA_PREFIX
cd build
make
```

### Enable VOL plugin:
```bash
export HDF5_PLUGIN_PATH=/path/to/arraymorph/arraymorph/build/src
export HDF5_VOL_CONNECTOR=arraymorph
```

## Configure Environment for Cloud Access

### AWS Configuration:
```bash
export BUCKET_NAME=XXXXXX
export AWS_ACCESS_KEY_ID=XXXXXX
export AWS_SECRET_ACCESS_KEY=XXXXXX
export AWS_REGION=us-east-2  # or your bucket's region
```

### Azure Configuration:
```bash
export AZURE_CONNECTION_STRING=XXXXXX
```

---

# Tutorials

## Run a simple example: Writing and Reading HDF5 files from Cloud

### Prerequisites:
- AWS or Azure cloud account with credentials
- S3 bucket or Azure container
- ArrayMorph dependencies installed

### Steps:
1. Activate conda environment  
   ```bash
   conda activate arraymorph
   ```

2. Write sample HDF5 data to the cloud  
   ```bash
   cd examples/python
   python3 write.py
   ```

3. Read data back from cloud HDF5 file  
   ```bash
   cd examples/python
   python3 read.py
   ```
---

# Explanation

### How ArrayMorph Works

ArrayMorph plugs into the HDF5 stack using a VOL (Virtual Object Layer) plugin that intercepts file operations and routes them to cloud object storage instead of local files. This allows existing HDF5 APIs (both C++ and h5py in Python) to operate on cloud-based data seamlessly, enabling transparent cloud access for scientific or ML pipelines.

It supports:
- Cloud backends: AWS S3 and Azure Blob
- File formats: Current binary data stream (we plan to extend to other formats like jpg in the future)
- Languages: C++ and Python (via h5py compatibility)

The system is designed to be efficient in latency-sensitive scenarios and aims to integrate well with large-scale distributed training and inference.

---

## References

- [HDF5 VOL connectors](https://docs.hdfgroup.org/hdf5/develop/_v_o_l.html)
- [AWS SDK for C++](https://github.com/aws/aws-sdk-cpp)
- [Azure SDK for C++](https://github.com/Azure/azure-sdk-for-cpp)
- [h5py documentation](https://docs.h5py.org/en/stable/)
- [conda-forge](https://conda-forge.org/)

---

## Acknowledgements

This project is supported by:

*National Science Foundation (NSF) funded AI institute for Intelligent Cyberinfrastructure with Computational Learning in the Environment (ICICLE) (OAC 2112606)*
