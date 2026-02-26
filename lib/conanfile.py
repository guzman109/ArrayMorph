from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMakeToolchain, CMakeDeps


class ArrayMorphRecipe(ConanFile):
    name = "ArrayMorph"
    version = "0.2.0"
    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires("aws-sdk-cpp/1.11.692")
        self.requires("azure-sdk-for-cpp/1.16.1")
        self.requires("hdf5/1.14.6")
        self.requires("libcurl/8.17.0")
        self.requires("openssl/3.6.1")

    def configure(self):
        self.options["*"].shared = False

        # AWS SDK: ONLY S3 — disable everything that pulls in
        # audio (libalsa), GUI (xorg), and other unnecessary deps
        self.options["aws-sdk-cpp"].s3 = True
        self.options["aws-sdk-cpp"].text_to_speech = False
        self.options["aws-sdk-cpp"].access_management = False
        self.options["aws-sdk-cpp"].identity_management = False
        self.options["aws-sdk-cpp"].transfer = False
        self.options["aws-sdk-cpp"].queues = False
        self.options["aws-sdk-cpp"].messaging = False

        # Azure SDK: only blob storage
        self.options["azure-sdk-for-cpp"].with_storage_blobs = True
        self.options["azure-sdk-for-cpp"].with_storage_datalake = False

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self, generator="Ninja")
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
