import json
import boto3
from botocore import UNSIGNED
from botocore.client import Config

from cakechat.utils.files_utils import PackageResolver, extract_tar
from cakechat.utils.s3 import S3FileResolver


def get_s3_resource():
    return boto3.resource('s3', config=Config(signature_version=UNSIGNED))


def _create_metadata(model):
    model_params_str = json.dumps(model.model_params, indent=2, sort_keys=True)
    metrics_str = json.dumps(model.metrics, indent=2, sort_keys=True) if model.metrics else 'Unknown'
    metadata = 'Model params:\n\n{}\n\nValidation metrics:\n\n{}\n'.format(model_params_str, metrics_str)

    return metadata

def get_s3_model_resolver(bucket_name, remote_dir):
    return PackageResolver.init_resolver(
        package_file_resolver_factory=S3FileResolver.init_resolver(bucket_name=bucket_name, remote_dir=remote_dir),
        package_file_ext='tar.gz',
        package_extractor=extract_tar)
