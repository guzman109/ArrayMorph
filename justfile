
# ArrayMorph — Top-Level Build Orchestration
# https://just.systems

# --- Settings ---
set dotenv-load := true
set export := true

# --- Variables ---
CONAN_BUILD_DIR := "lib/build/Release/generators"
CMAKE_TOOLCHAIN_FILE := justfile_directory() / CONAN_BUILD_DIR / "conan_toolchain.cmake"
H5PY_HDF5_DIR := `./.venv/bin/python -c "import h5py,os;d=os.path.dirname(h5py.__file__);print(os.path.join(d,'.dylibs') if os.path.exists(os.path.join(d,'.dylibs')) else os.path.join(os.path.dirname(d),'h5py.libs'))"`

# --- Recipes ---

# List available commands
default:
    @just --list

# Install C++ dependencies via Conan
deps:
    cd lib && conan install . --build=missing -s build_type=Release

# Build Python wheel (scikit-build-core handles CMake)
wheel:
    CMAKE_TOOLCHAIN_FILE={{ CMAKE_TOOLCHAIN_FILE }} \
    H5PY_HDF5_DIR={{ H5PY_HDF5_DIR }} \
    uv build --wheel --no-build-isolation

# Install editable into current venv (for development iteration)
dev:
    CMAKE_TOOLCHAIN_FILE={{ CMAKE_TOOLCHAIN_FILE }} \
    H5PY_HDF5_DIR={{ H5PY_HDF5_DIR }} \
    uv pip install -e .

# Full build from scratch: deps → wheel
build: deps wheel

# Test the built wheel in an isolated venv
test:
    rm -rf .test-venv
    uv venv .test-venv
    source .test-venv/bin/activate.fish
    uv pip install dist/arraymorph-0.2.0-*.whl
    python -c "import arraymorph; print('Plugin:', arraymorph.get_plugin_path()); arraymorph.enable(); print('VOL enabled')"
    rm -rf .test-venv

# Full build + test
all: build test

# Clean build artifacts
clean:
    rm -rf lib/build dist *.egg-info .test-venv

# Full clean rebuild
rebuild: clean build

# Show current env var values (for debugging)
info:
    @echo "CMAKE_TOOLCHAIN_FILE: {{ CMAKE_TOOLCHAIN_FILE }}"
    @echo "H5PY_HDF5_DIR:        {{ H5PY_HDF5_DIR }}"
    @echo "Plugin lib:            $(find lib/build -name 'lib_array_morph*' 2>/dev/null || echo 'not built')"

