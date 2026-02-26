"""
ArrayMorph - HDF5 VOL connector for cloud object storage.

Supports AWS S3 and Azure Blob Storage via HDF5's Virtual Object Layer.
"""

from __future__ import annotations

import os
from pathlib import Path

__version__ = "0.2.0"

# The compiled VOL plugin lives next to this file after installation
_PLUGIN_DIR = str(Path(__file__).parent / "lib")


def get_plugin_path() -> str:
    """Return the directory containing the ArrayMorph VOL plugin (.so/.dylib).

    Use this to set HDF5_PLUGIN_PATH:
        >>> import arraymorph
        >>> os.environ["HDF5_PLUGIN_PATH"] = arraymorph.get_plugin_path()
    """
    return _PLUGIN_DIR


def enable() -> None:
    """Configure HDF5 environment variables to use ArrayMorph.

    Sets HDF5_PLUGIN_PATH and HDF5_VOL_CONNECTOR so that any
    subsequent h5py calls route through the ArrayMorph VOL connector.

    Usage:
        >>> import arraymorph
        >>> arraymorph.enable()
        >>> import h5py
        >>> f = h5py.File("s3://bucket/data.h5", "r")
    """
    os.environ["HDF5_PLUGIN_PATH"] = _PLUGIN_DIR
    os.environ["HDF5_VOL_CONNECTOR"] = "arraymorph"


def configure_s3(
    bucket: str,
    access_key: str = "",
    secret_key: str = "",
    endpoint: str | None = None,
    region: str = "us-east-2",
    use_tls: bool = False,
    addressing_style: bool = False,
    use_signed_payloads: bool = False,
) -> None:
    """Configure AWS S3 credentials and client behavior for ArrayMorph.

    Sets the environment variables read by the VOL connector's S3 client
    at initialization time. Call this before any h5py file operations.

    Args:
        bucket: Name of the S3 bucket where HDF5 files are stored.
            Maps to: BUCKET_NAME
        access_key: Access key ID for authentication with the S3 service.
            Maps to: AWS_ACCESS_KEY_ID
        secret_key: Secret access key paired with access_key for authentication.
            Maps to: AWS_SECRET_ACCESS_KEY
        endpoint: Custom S3-compatible endpoint URL (e.g. 'http://localhost:3900').
            When None, the S3 client targets the default AWS endpoint. Required
            for any non-AWS S3-compatible object store (MinIO, Ceph, etc.).
            Maps to: AWS_ENDPOINT_URL_S3
        region: Region label used in SigV4 request signing. Must match the region
            your bucket or S3-compatible store is configured with — a mismatch
            produces signature validation errors. Defaults to 'us-east-2'.
            Maps to: AWS_REGION
        use_tls: Whether to use HTTPS (True) or HTTP (False) for S3 connections.
            Set to False for object stores that do not have TLS configured.
            Defaults to False.
            Maps to: AWS_USE_TLS
        addressing_style: URL addressing style for the S3 client. When True,
            uses path-style ('endpoint/bucket/key'). When False, uses
            virtual-hosted style ('bucket.endpoint/key'), which can cause the
            S3 client to misinterpret the HDF5 filename as the bucket name.
            Most S3-compatible stores require path-style addressing.
            Defaults to False.
            Maps to: AWS_S3_ADDRESSING_STYLE
        use_signed_payloads: Whether to include the request body in the SigV4
            signature (PayloadSigningPolicy::Always). Some S3-compatible stores
            require signed payloads and will reject requests with signature
            validation errors if this is disabled. Defaults to False.
            Maps to: AWS_SIGNED_PAYLOADS

    Example:
        >>> import arraymorph
        >>> arraymorph.configure_s3(
        ...     bucket="my-bucket",
        ...     access_key="my-access-key",
        ...     secret_key="my-secret-key",
        ...     endpoint="http://localhost:3900",
        ...     region="us-east-1",
        ...     use_tls=False,
        ...     addressing_style=True,
        ...     use_signed_payloads=True,
        ... )
        >>> arraymorph.enable()
    """
    if not (access_key and secret_key):
        raise ValueError(
            "configure_s3() requires both 'access_key' and 'secret_key'. "
            "Set them explicitly or export AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY "
            "before calling this function."
        )

    os.environ["AWS_ACCESS_KEY_ID"] = access_key
    os.environ["AWS_SECRET_ACCESS_KEY"] = secret_key
    os.environ["STORAGE_PLATFORM"] = "S3"
    os.environ["BUCKET_NAME"] = bucket
    os.environ["AWS_REGION"] = region

    if endpoint:
        os.environ["AWS_ENDPOINT_URL_S3"] = endpoint

    os.environ["AWS_USE_TLS"] = str(use_tls).lower()
    os.environ["AWS_S3_ADDRESSING_STYLE"] = "path" if addressing_style else "virtual"
    os.environ["AWS_SIGNED_PAYLOADS"] = str(use_signed_payloads).lower()


def configure_azure(
    container: str,
    connection_string: str | None = None,
) -> None:
    """Configure Azure Blob Storage credentials for ArrayMorph.

    Sets the environment variables read by the VOL connector's Azure client
    at initialization time. Call this before any h5py file operations.

    Args:
        container: Name of the Azure Blob Storage container where HDF5 files
            are stored. Maps to: BUCKET_NAME
        connection_string: Azure Storage connection string used to authenticate
            and locate the storage account. If None, the connector will fall back
            to the existing AZURE_STORAGE_CONNECTION_STRING environment variable.
            Maps to: AZURE_STORAGE_CONNECTION_STRING

    Example:
        >>> import arraymorph
        >>> arraymorph.configure_azure(
        ...     container="my-container",
        ...     connection_string="DefaultEndpointsProtocol=https;AccountName=...",
        ... )
        >>> arraymorph.enable()
    """
    if not connection_string and not os.environ.get("AZURE_STORAGE_CONNECTION_STRING"):
        raise ValueError(
            "configure_azure() requires a 'connection_string'. "
            "Set it explicitly or export AZURE_STORAGE_CONNECTION_STRING "
            "before calling this function."
        )

    os.environ["STORAGE_PLATFORM"] = "Azure"
    os.environ["BUCKET_NAME"] = container
    if connection_string:
        os.environ["AZURE_STORAGE_CONNECTION_STRING"] = connection_string
