import aioboto3

from domain.entities.base import Url
from domain.interfaces.services.file_storage import FileStorage


class S3FileStorage(FileStorage):
    def __init__(
        self,
        *,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        public_base_url: str,
    ) -> None:
        self._session = aioboto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        self._endpoint_url = endpoint_url
        self._bucket = bucket
        self._public_base_url = public_base_url.rstrip("/")

    async def upload_file(self, file_bytes: bytes, destination_path: str, content_type: str) -> Url:
        async with self._session.client("s3", endpoint_url=self._endpoint_url) as s3:
            await s3.put_object(
                Bucket=self._bucket,
                Key=destination_path,
                Body=file_bytes,
                ContentType=content_type,
            )
        return Url(f"{self._public_base_url}/{destination_path}")
