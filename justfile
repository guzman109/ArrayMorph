# ArrayMorph — Top-Level Build Orchestration
# https://just.systems
# --- Settings ---

set dotenv-load := true
set export := true

# --- Variables ---

VCPKG_TOOLCHAIN := env("VCPKG_ROOT", home_directory() / ".vcpkg") / "scripts/buildsystems/vcpkg.cmake"
# HDF5_DIR := `./.venv/bin/python3 -c "import h5py,os;d=os.path.dirname(h5py.__file__);print(os.path.join(d,'.dylibs') if os.path.exists(os.path.join(d,'.dylibs')) else os.path.join(os.path.dirname(d),'h5py.libs'))"`
# HDF5_DIR := env("HDF5_DIR")
HDF5_DIR := "1"
# --- Recipes ---

# List available commands
default:
    @just --list

# Build Python wheel (scikit-build-core handles CMake)
wheel:
    CMAKE_TOOLCHAIN_FILE={{ VCPKG_TOOLCHAIN }} \
    HDF5_DIR={{ HDF5_DIR }} \
      uv build --wheel --no-build-isolation

# Install editable into current venv (for development iteration)
dev:
    CMAKE_TOOLCHAIN_FILE={{ VCPKG_TOOLCHAIN }} \
    HDF5_DIR={{ HDF5_DIR }} \
    uv pip install -e .

# Full build from scratch: deps → wheel
build: wheel

test:
    python main.py

# Full build + test
all: build

# Clean build artifacts
clean:
    rm -rf lib/build lib/vcpkg_installed dist *.egg-info .test-venv .dist

# Patch h5py's libhdf5 install name so the linker and loader can resolve it
patch-hdf5:
    #!/usr/bin/env bash
    HDF5_LIB=$(find "{{ HDF5_DIR }}" -name "libhdf5.*.dylib" ! -name "*_hl*" | head -1)
    if [ -z "$HDF5_LIB" ]; then
        echo "patch-hdf5: nothing to patch (not macOS or library not found)"
        exit 0
    fi
    CURRENT=$(otool -D "$HDF5_LIB" | tail -1)
    if [ "$CURRENT" = "$HDF5_LIB" ]; then
        echo "patch-hdf5: already patched ($HDF5_LIB)"
        exit 0
    fi
    echo "patch-hdf5: $CURRENT → $HDF5_LIB"
    install_name_tool -id "$HDF5_LIB" "$HDF5_LIB"

# Full clean rebuild
rebuild: clean patch-hdf5 build

# Show current env var values (for debugging)
info:
    @echo "CMAKE_TOOLCHAIN_FILE: {{ VCPKG_TOOLCHAIN }}"
    @echo "HDF5_DIR:        {{ HDF5_DIR }}"
    @echo "Plugin lib:            $(find lib/build -name 'lib_array_morph*' 2>/dev/null || echo 'not built')"
