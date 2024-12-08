import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from boto3.exceptions import S3UploadFailedError
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError, EndpointConnectionError
from app.utils.s3 import S3Utils


class TestS3Utils(unittest.TestCase):

    @patch("boto3.client")
    @patch("os.getenv")
    def test_initialize_s3(self, mock_getenv, mock_boto_client):
        mock_getenv.side_effect = lambda key: {
            "S3_ENDPOINT_URL": "http://localhost:4566",
            "S3_ACCESS_KEY_ID": "test_access_key",
            "S3_SECRET_ACCESS_KEY": "test_secret_key",
        }.get(key)
        S3Utils.initialize_s3()
        mock_boto_client.assert_called_once_with(
            "s3",
            endpoint_url="http://localhost:4566",
            aws_access_key_id="test_access_key",
            aws_secret_access_key="test_secret_key",
        )

    @patch("os.path.exists", return_value=False)
    def test_upload_file_not_exist(self, mock_exists):
        with self.assertRaises(HTTPException) as context:
            S3Utils.upload_file("non_existent_file.txt")
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("File 'non_existent_file.txt' does not exist.", context.exception.detail)

    @patch("boto3.client")
    @patch("os.getenv", return_value="test_bucket")
    @patch("os.path.exists", return_value=True)
    def test_upload_file_success(self, mock_exists, mock_getenv, mock_boto_client):
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        S3Utils.s3 = None

        S3Utils.upload_file("test_file.txt", "test_object.txt")
        mock_s3.upload_file.assert_called_once_with("test_file.txt", "test_bucket", "test_object.txt")

    @patch("boto3.client")
    @patch("os.getenv", return_value="test_bucket")
    @patch("os.path.exists", return_value=True)
    def test_upload_file_s3_upload_failed(self, mock_exists, mock_getenv, mock_boto_client):
        mock_s3 = MagicMock()
        mock_s3.upload_file.side_effect = S3UploadFailedError
        mock_boto_client.return_value = mock_s3
        S3Utils.s3 = None

        with self.assertRaises(HTTPException) as context:
            S3Utils.upload_file("test_file.txt", "test_object.txt")
        self.assertEqual(context.exception.status_code, 424)
        self.assertIn("Failed to upload file to S3", context.exception.detail)

    @patch("boto3.client")
    @patch("os.getenv", return_value="test_bucket")
    @patch("os.path.exists", return_value=True)
    def test_upload_file_endpoint_connection_error(self, mock_exists, mock_getenv, mock_boto_client):
        mock_s3 = MagicMock()
        mock_s3.upload_file.side_effect = EndpointConnectionError(endpoint_url="http://localhost:4566")
        mock_boto_client.return_value = mock_s3
        S3Utils.s3 = None

        with self.assertRaises(HTTPException) as context:
            S3Utils.upload_file("test_file.txt", "test_object.txt")
        self.assertEqual(context.exception.status_code, 424)
        self.assertIn("Failed to connect to S3 endpoint.", context.exception.detail)

    @patch("boto3.client")
    @patch("os.getenv", return_value="test_bucket")
    @patch("os.path.exists", return_value=True)
    def test_upload_file_no_credentials(self, mock_exists, mock_getenv, mock_boto_client):
        mock_s3 = MagicMock()
        mock_s3.upload_file.side_effect = NoCredentialsError
        mock_boto_client.return_value = mock_s3
        S3Utils.s3 = None

        with self.assertRaises(HTTPException) as context:
            S3Utils.upload_file("test_file.txt", "test_object.txt")
        self.assertEqual(context.exception.status_code, 424)
        self.assertIn("S3 credentials not provided or incorrect.", context.exception.detail)

    @patch("boto3.client")
    @patch("os.getenv", return_value="test_bucket")
    @patch("os.path.exists", return_value=True)
    def test_upload_file_partial_credentials(self, mock_exists, mock_getenv, mock_boto_client):
        mock_s3 = MagicMock()
        mock_s3.upload_file.side_effect = PartialCredentialsError(provider="aws", cred_var="aws_secret_access_key")
        mock_boto_client.return_value = mock_s3
        S3Utils.s3 = None

        with self.assertRaises(HTTPException) as context:
            S3Utils.upload_file("test_file.txt", "test_object.txt")
        self.assertEqual(context.exception.status_code, 424)
        self.assertIn("Incomplete S3 credentials provided.", context.exception.detail)

    @patch("boto3.client")
    @patch("os.getenv", return_value="test_bucket")
    @patch("os.path.exists", return_value=True)
    def test_upload_file_client_error(self, mock_exists, mock_getenv, mock_boto_client):
        mock_s3 = MagicMock()
        mock_s3.upload_file.side_effect = ClientError(
            {"Error": {"Code": "500", "Message": "Internal Server Error"}}, "upload_file"
        )
        mock_boto_client.return_value = mock_s3
        S3Utils.s3 = None

        with self.assertRaises(HTTPException) as context:
            S3Utils.upload_file("test_file.txt", "test_object.txt")
        self.assertEqual(context.exception.status_code, 424)
        self.assertIn("Failed to upload file to S3", context.exception.detail)

    @patch("boto3.client")
    @patch("os.getenv", return_value="test_bucket")
    @patch("os.path.exists", return_value=True)
    def test_upload_file_default_object_name(self, mock_exists, mock_getenv, mock_boto_client):
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        S3Utils.s3 = None

        file_path = "path/to/test_file.txt"
        expected_object_name = os.path.basename(file_path)

        S3Utils.upload_file(file_path)
        mock_s3.upload_file.assert_called_once_with(file_path, "test_bucket", expected_object_name)
