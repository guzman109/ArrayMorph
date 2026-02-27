# ArrayMorph

[![Build Status](https://github.com/ICICLE-ai/arraymorph/actions/workflows/build.yml/badge.svg)](https://github.com/ICICLE-ai/arraymorph/actions/workflows/build.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ArrayMorph enables efficient storage and retrieval of array data from cloud object stores, supporting AWS S3 and Azure Blob Storage. It is an HDF5 Virtual Object Layer (VOL) plugin that transparently routes HDF5 file operations to cloud storage — existing h5py or HDF5 C++ code works unchanged once the plugin is loaded.

**Tag**: CI4AI

---

# How-To Guides

## Install ArrayMorph

```bash
pip install arraymorph
```

Once installed, jump straight to [Configure credentials for AWS S3](#configure-credentials-for-aws-s3) or [Azure](#configure-credentials-for-azure-blob-storage) below.

If you need the standalone `lib_arraymorph` binary, you can [download a pre-built release](#download-a-pre-built-lib_arraymorph) or [build from source](#build-from-source).

## Configure credentials for AWS S3

Use the Python API before opening any HDF5 files:

```python
import arraymorph

arraymorph.configure_s3(
    bucket="my-bucket",
    access_key="MY_ACCESS_KEY",
    secret_key="MY_SECRET_KEY",
    region="us-east-1",
    use_tls=True,
)
arraymorph.enable()
```

Or set environment variables directly:

```bash
export STORAGE_PLATFORM=S3
export BUCKET_NAME=my-bucket
export AWS_ACCESS_KEY_ID=MY_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=MY_SECRET_KEY
export AWS_REGION=us-east-1
export HDF5_PLUGIN_PATH=$(python -c "import arraymorph; print(arraymorph.get_plugin_path())")
export HDF5_VOL_CONNECTOR=arraymorph
```

## Configure credentials for Azure Blob Storage

```python
import arraymorph

arraymorph.configure_azure(
    container="my-container",
    connection_string="DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net",
)
arraymorph.enable()
```

Or set environment variables directly:

```bash
export STORAGE_PLATFORM=Azure
export BUCKET_NAME=my-container
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;..."
export HDF5_PLUGIN_PATH=$(python -c "import arraymorph; print(arraymorph.get_plugin_path())")
export HDF5_VOL_CONNECTOR=arraymorph
```

## Use an S3-compatible object store (MinIO, Ceph, Garage)

Pass `endpoint`, `addressing_style=True`, and `use_signed_payloads=True` to match the requirements of most self-hosted S3-compatible stores:

```python
import arraymorph

arraymorph.configure_s3(
    bucket="my-bucket",
    access_key="MY_ACCESS_KEY",
    secret_key="MY_SECRET_KEY",
    endpoint="http://localhost:9000",
    region="us-east-1",
    use_tls=False,
    addressing_style=True,
    use_signed_payloads=True,
)
arraymorph.enable()
```

## Download a pre-built lib_arraymorph

Each [GitHub release](https://github.com/ICICLE-ai/ArrayMorph/releases) attaches standalone pre-compiled binaries of `lib_arraymorph` for all supported platforms:

| File                               | Platform            |
| ---------------------------------- | ------------------- |
| `lib_arraymorph-linux-x86_64.so`   | Linux x86_64        |
| `lib_arraymorph-linux-aarch64.so`  | Linux aarch64       |
| `lib_arraymorph-macos-arm64.dylib` | macOS Apple Silicon |

Download the file for your platform from the release assets and set `HDF5_PLUGIN_PATH` to the directory containing it before calling `arraymorph.enable()` or setting `HDF5_VOL_CONNECTOR` manually.

## Build from source

Use this path if you want to compile `lib_arraymorph` yourself — for example to target a specific platform, contribute changes, or build a custom wheel.

### Prerequisites

- [vcpkg](https://github.com/microsoft/vcpkg) — installs the AWS and Azure C++ SDKs via CMake
- [CMake](https://cmake.org) and [Ninja](https://ninja-build.org)
- [uv](https://docs.astral.sh/uv/) — Python package manager

### Step 1 — Clone and create a virtual environment

```bash
git clone https://github.com/ICICLE-ai/ArrayMorph.git
cd ArrayMorph
uv venv
source .venv/bin/activate
```

### Step 2 — Install h5py

`lib_arraymorph` links against an HDF5 shared library at build time. Rather than requiring a separate system-wide HDF5 installation, the build system points CMake at the `.so` / `.dylib` that h5py already bundles. Install h5py first so those libraries are present:

```bash
uv pip install h5py
```

On macOS the bundled libraries land in `.venv/lib/python*/site-packages/h5py/.dylibs/`; on Linux in `.venv/lib/python*/site-packages/h5py.libs/`.

### Step 3 — Configure and build the shared library

```bash
export HDF5_DIR=$(.venv/bin/python -c "import h5py,os; d=os.path.dirname(h5py.__file__); print(os.path.join(d,'.dylibs') if os.path.exists(os.path.join(d,'.dylibs')) else os.path.join(os.path.dirname(d),'h5py.libs'))")

cmake -B lib/build -S lib \
    -DCMAKE_TOOLCHAIN_FILE=${VCPKG_ROOT:-~/.vcpkg}/scripts/buildsystems/vcpkg.cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -G Ninja

cmake --build lib/build
```

This produces `lib/build/lib_arraymorph.dylib` on macOS or `lib/build/lib_arraymorph.so` on Linux.

### Optional — Python package

If you also want to use the Python API, install the package in editable mode:

```bash
HDF5_DIR=$HDF5_DIR \
CMAKE_TOOLCHAIN_FILE=${VCPKG_ROOT:-~/.vcpkg}/scripts/buildsystems/vcpkg.cmake \
uv pip install -e .
```

Or build a redistributable wheel:

```bash
HDF5_DIR=$HDF5_DIR \
CMAKE_TOOLCHAIN_FILE=${VCPKG_ROOT:-~/.vcpkg}/scripts/buildsystems/vcpkg.cmake \
uv build --wheel --no-build-isolation
```

The wheel is written to `dist/`. Install it in any environment with:

```bash
pip install dist/arraymorph-*.whl
```

---

# Tutorials

## Write and read a chunked array on AWS S3

This tutorial walks through writing a 2-D NumPy array to a cloud HDF5 file and reading a slice of it back.

### Prerequisites

- An AWS account with an S3 bucket, or an S3-compatible object store
- ArrayMorph installed (`pip install arraymorph`)

### Step 1 — Configure and enable ArrayMorph

```python
import arraymorph

arraymorph.configure_s3(
    bucket="my-bucket",
    access_key="MY_ACCESS_KEY",
    secret_key="MY_SECRET_KEY",
    region="us-east-1",
    use_tls=True,
)
arraymorph.enable()
```

`arraymorph.enable()` sets `HDF5_PLUGIN_PATH` and `HDF5_VOL_CONNECTOR` in the current process. Any `h5py.File(...)` call made after this point is routed through ArrayMorph.

### Step 2 — Write array data

```python
import h5py
import numpy as np

data = np.fromfunction(lambda i, j: i + j, (100, 100), dtype="i4")

with h5py.File("demo.h5", "w") as f:
    f.create_dataset("values", data=data, chunks=(10, 10))
```

Each 10×10 chunk is stored as a separate object in your S3 bucket.

### Step 3 — Read a slice back

```python
import h5py

with h5py.File("demo.h5", "r") as f:
    dset = f["values"]
    print(dset.dtype)           # int32
    print(dset[5:15, 5:15])     # fetches only the chunks that overlap this slice
```

Only the chunks that overlap the requested hyperslab are fetched from cloud storage — no full-file download occurs.

---

# Explanation

## How ArrayMorph works

ArrayMorph is implemented as an HDF5 **Virtual Object Layer (VOL)** connector. The VOL is an abstraction layer inside the HDF5 library that separates the public API from the storage implementation. By providing a plugin that registers itself as a VOL connector, ArrayMorph intercepts every HDF5 file operation before it reaches the native POSIX layer.

When `arraymorph.enable()` is called:

1. `HDF5_PLUGIN_PATH` is set to the directory containing the compiled shared library (`lib_arraymorph.so` / `lib_arraymorph.dylib`).
2. `HDF5_VOL_CONNECTOR=arraymorph` tells HDF5 to load and activate that plugin for all subsequent file operations.

From this point, a call like `h5py.File("demo.h5", "w")` does not touch the local filesystem. Instead, the VOL connector:

1. Reads cloud credentials from environment variables and constructs an AWS S3 or Azure Blob client (selected by `STORAGE_PLATFORM`).
2. On dataset read/write, translates the HDF5 hyperslab selection into a list of chunks and dispatches asynchronous get/put requests against the object store — one object per chunk.

### Chunked storage model

HDF5 datasets are divided into fixed-size chunks (e.g. `chunks=(64, 64)` for a 2-D dataset). ArrayMorph stores each chunk as an independent object in the bucket. The object key encodes the dataset path and chunk coordinates, so a partial read only fetches the chunks that overlap the requested slice. For large chunks, ArrayMorph can issue byte-range requests to retrieve only the needed bytes within a chunk object.

### Async I/O

Both the S3 and Azure backends use asynchronous operations dispatched to a thread pool. This allows ArrayMorph to fetch multiple chunks in parallel, which is important for workloads that access many chunks per read (e.g. strided access patterns in machine learning data loaders).

### Compatibility

Because the interception happens at the VOL layer, no changes to application code are required. Any program that opens HDF5 files with h5py or the HDF5 C++ API will automatically use ArrayMorph once the plugin is loaded.

---

# References

## Python API

### `arraymorph.enable() -> None`

Sets `HDF5_PLUGIN_PATH` and `HDF5_VOL_CONNECTOR` in the current process environment. Must be called before any `h5py.File(...)` call.

### `arraymorph.get_plugin_path() -> str`

Returns the directory containing the compiled VOL plugin. Useful when you need to set `HDF5_PLUGIN_PATH` manually.

### `arraymorph.configure_s3(bucket, access_key, secret_key, endpoint=None, region="us-east-2", use_tls=False, addressing_style=False, use_signed_payloads=False) -> None`

Configures the S3 client. All parameters are written to environment variables consumed by the C++ plugin at file-open time.

| Parameter             | Environment variable      | Default     | Description                                          |
| --------------------- | ------------------------- | ----------- | ---------------------------------------------------- |
| `bucket`              | `BUCKET_NAME`             | —           | S3 bucket name                                       |
| `access_key`          | `AWS_ACCESS_KEY_ID`       | —           | Access key ID                                        |
| `secret_key`          | `AWS_SECRET_ACCESS_KEY`   | —           | Secret access key                                    |
| `endpoint`            | `AWS_ENDPOINT_URL_S3`     | AWS default | Custom endpoint for S3-compatible stores             |
| `region`              | `AWS_REGION`              | `us-east-2` | SigV4 signing region                                 |
| `use_tls`             | `AWS_USE_TLS`             | `false`     | Use HTTPS when `True`                                |
| `addressing_style`    | `AWS_S3_ADDRESSING_STYLE` | `virtual`   | `path` when `True`; required for most non-AWS stores |
| `use_signed_payloads` | `AWS_SIGNED_PAYLOADS`     | `false`     | Include request body in SigV4 signature              |

### `arraymorph.configure_azure(container, connection_string=None) -> None`

Configures the Azure Blob client.

| Parameter           | Environment variable              | Default  | Description                     |
| ------------------- | --------------------------------- | -------- | ------------------------------- |
| `container`         | `BUCKET_NAME`                     | —        | Azure container name            |
| `connection_string` | `AZURE_STORAGE_CONNECTION_STRING` | From env | Azure Storage connection string |

## Environment variables

All configuration can be applied via environment variables without using the Python API. This is useful when running HDF5 C++ programs directly.

| Variable                          | Description                                         |
| --------------------------------- | --------------------------------------------------- |
| `HDF5_PLUGIN_PATH`                | Directory containing `lib_arraymorph.so` / `.dylib` |
| `HDF5_VOL_CONNECTOR`              | Must be `arraymorph` to activate the plugin         |
| `STORAGE_PLATFORM`                | `S3` (default) or `Azure`                           |
| `BUCKET_NAME`                     | Bucket or container name                            |
| `AWS_ACCESS_KEY_ID`               | S3 access key                                       |
| `AWS_SECRET_ACCESS_KEY`           | S3 secret key                                       |
| `AWS_REGION`                      | SigV4 signing region                                |
| `AWS_ENDPOINT_URL_S3`             | Custom S3-compatible endpoint URL                   |
| `AWS_USE_TLS`                     | `true` / `false`                                    |
| `AWS_S3_ADDRESSING_STYLE`         | `path` or `virtual`                                 |
| `AWS_SIGNED_PAYLOADS`             | `true` / `false`                                    |
| `AZURE_STORAGE_CONNECTION_STRING` | Azure connection string                             |

## External references

- [HDF5 VOL connectors](https://docs.hdfgroup.org/hdf5/develop/_v_o_l.html)
- [AWS SDK for C++](https://github.com/aws/aws-sdk-cpp)
- [Azure SDK for C++](https://github.com/Azure/azure-sdk-for-cpp)
- [h5py documentation](https://docs.h5py.org/en/stable/)

---

## Acknowledgements

This project is supported by the National Science Foundation (NSF) funded AI institute for Intelligent Cyberinfrastructure with Computational Learning in the Environment (ICICLE) (OAC 2112606).
