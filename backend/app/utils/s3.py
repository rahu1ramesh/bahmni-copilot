import boto3
import os
import logging
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError, EndpointConnectionError
from fastapi import HTTPException, status
from dotenv import load_dotenv
from typing import Optional
from boto3.exceptions import S3UploadFailedError


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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File '{file_path}' does not exist."
            )

        if object_name is None:
            object_name = os.path.basename(file_path)

        try:
            bucket_name = os.getenv("S3_BUCKET_NAME")
            S3Utils.s3.upload_file(file_path, bucket_name, object_name)
            logging.info(f"File '{file_path}' uploaded to bucket '{bucket_name}' as '{object_name}'.")
        except EndpointConnectionError:
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail="Failed to connect to S3 endpoint."
            )
        except S3UploadFailedError as e:
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail=f"Failed to upload file to S3: {e}"
            )
        except NoCredentialsError:
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail="S3 credentials not provided or incorrect."
            )
        except PartialCredentialsError:
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail="Incomplete S3 credentials provided."
            )
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail=f"Failed to upload file to S3: {e}"
            )
