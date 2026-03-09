from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMakeToolchain, CMakeDeps


class ArrayMorphRecipe(ConanFile):
    name = "ArrayMorph"
    version = "0.2.0"

    settings = "os", "compiler", "build_type", "arch"

    # HDF5 is here for HEADERS ONLY at build time.
    # At runtime, h5py's bundled libhdf5.so provides the symbols.
    # Pin to the same minor series h5py 3.11/3.12 ships (1.14.x).
    # Check with: python -c "import h5py; print(h5py.version.hdf5_version)"
    requires = (
        "aws-sdk-cpp/1.11.692",
        "azure-sdk-for-cpp/1.16.1",
        "hdf5/1.14.3",
    )

    default_options = {
        # Static HDF5 — we only use headers + link stubs at build time.
        # The wheel must NOT ship any HDF5 shared libs.
        "hdf5/*:shared": False,

        # Static everything else so the wheel is self-contained
        # (no extra .so files to bundle except libarraymorph itself).
        "aws-sdk-cpp/*:shared": False,
        "azure-sdk-for-cpp/*:shared": False,
        "libcurl/*:shared": False,
        "openssl/*:shared": False,

        # AWS: only S3
        "aws-sdk-cpp/*:s3": True,
        "aws-sdk-cpp/*:monitoring": False,
        "aws-sdk-cpp/*:transfer": False,
        "aws-sdk-cpp/*:queues": False,
        "aws-sdk-cpp/*:identity-management": False,
        "aws-sdk-cpp/*:access-management": False,
        "aws-sdk-cpp/*:s3-encryption": False,
        "aws-sdk-cpp/*:text-to-speech": False,

        # Azure: only Blob
        "azure-sdk-for-cpp/*:with_storage_blobs": True,
        "azure-sdk-for-cpp/*:with_storage_datalake": False,
    }

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self, generator="Ninja")
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()
