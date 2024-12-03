import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import os
from dotenv import load_dotenv
from typing import Optional
import logging


load_dotenv()


class S3Utils:
    s3 = None

    @staticmethod
    def initialize_s3():
        """
        Initialize the S3 client. This method must be called once before using any other methods.
        """
        if S3Utils.s3 is None:
            endpoint_url = os.getenv("S3_ENDPOINT_URL")
            access_key_id = os.getenv("S3_ACCESS_KEY_ID")
            secret_access_key = os.getenv("S3_SECRET_ACCESS_KEY")
            S3Utils.s3 = boto3.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
            )

    @staticmethod
    def upload_file(file_path: str, object_name: Optional[str] = None):
        """
        Upload a file to an S3 bucket.

        :param file_path: Path to the local file to be uploaded.
        :param object_name: S3 object name. Defaults to the file's name.

        :raises ValueError: If the file does not exist.
        :raises ClientError: If an error occurs with S3.
        """
        if S3Utils.s3 is None:
            S3Utils.initialize_s3()

        if not os.path.exists(file_path):
            raise ValueError(f"File '{file_path}' does not exist.")

        if object_name is None:
            object_name = os.path.basename(file_path)

        try:
            bucket_name = os.getenv("S3_BUCKET_NAME")
            S3Utils.s3.upload_file(file_path, bucket_name, object_name)
            logging.info(f"File '{file_path}' uploaded to bucket '{bucket_name}' as '{object_name}'.")
        except NoCredentialsError:
            raise ValueError("S3 credentials not provided or incorrect.")
        except PartialCredentialsError:
            raise ValueError("Incomplete S3 credentials provided.")
        except ClientError as e:
            raise ValueError(f"Failed to upload file to S3: {e}")
