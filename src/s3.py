from dataclasses import dataclass
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import json
import pickle



load_dotenv()

@dataclass
class S3Config:
    minio_user: str = os.getenv("MINIO_USER")
    minio_password: str = os.getenv("MINIO_PASSWORD")
    minio_host: str = os.getenv("MINIO_HOST")
    minio_port: str = os.getenv("MINIO_PORT")
    model_bucket: str = os.getenv("MODEL_S3_BUCKET")
    base_data_bucket: str = os.getenv("BASE_DATA_S3_BUCKET")
    base_model: str = os.getenv("BASE_MODEL")


bucket_config = S3Config()


class S3Handler:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        self._client = boto3.client(
            "s3",
            aws_access_key_id=bucket_config.minio_user,
            aws_secret_access_key=bucket_config.minio_password,
            endpoint_url=f"{bucket_config.minio_host}:{bucket_config.minio_port}"
        )

    @classmethod
    def instance(cls):
        return cls()

    @classmethod
    def upload(cls, bucket_name: str, body: str, object_key: str):
        cls.instance()._client.put_object(
            Body=body,
            Bucket=bucket_name,
            Key=object_key,
        )

    @classmethod
    def get(cls, bucket_name: str, object_key: str):    
        try:
            response = cls.instance()._client.get_object(Bucket=bucket_name, Key=object_key)
            body = response["Body"].read()
            
            if object_key.endswith(".json"):
                return json.loads(body)
            elif object_key.endswith(".pickle"):
                return pickle.loads(body)
            return body
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return None
            raise

    @classmethod
    def check_file_existence(cls, bucket_name: str, object_key: str) -> bool:
        try:
            cls.instance()._client.head_object(Bucket=bucket_name, Key=object_key)
            return True
        except Exception:
            return False
        
    @classmethod
    def clear_bucket(cls, bucket_name: str):
        client = cls.instance()._client

        objects_to_delete = client.list_objects_v2(Bucket=bucket_name)

        if "Contents" in objects_to_delete:
            delete_objects = [{"Key": obj["Key"]} for obj in objects_to_delete["Contents"]]
            client.delete_objects(Bucket=bucket_name, Delete={"Objects": delete_objects})

