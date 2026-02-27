# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

> **⚠️ Pre-release** — API may change. Feedback welcome via [GitHub Issues](https://github.com/ICICLE-ai/ArrayMorph/issues).

### Added
- **Python Package & API**: ArrayMorph is now available via `pip install arraymorph`. You can now dynamically configure AWS S3, Azure Blob Storage, or any S3-compatible endpoints directly from Python (`arraymorph.configure_s3(...)` and `arraymorph.configure_azure(...)`).
- **Pre-built Binaries**: Pre-compiled binaries of `lib_arraymorph` are now attached to GitHub releases for Linux (x86_64, aarch64) and macOS (Apple Silicon).
- **Expanded Documentation**: The README has been overhauled with comprehensive How-To guides, tutorials, and a detailed explanation of ArrayMorph's chunked storage model and async I/O.

### Changed
- **Simplified Build System**: The build system has been revamped. It now leverages `uv` for Python environments and `vcpkg` for fetching C++ SDK dependencies, making building from source much smoother.
