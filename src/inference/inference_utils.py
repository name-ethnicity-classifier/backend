from io import BytesIO
import torch
from s3 import S3Handler, bucket_config



device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def get_model_checkpoint(model_id: str):
    model_checkpoint_path = f"{model_id}/model.pt"
    model_file = S3Handler.get(bucket_config.model_bucket, model_checkpoint_path)
    
    device_map_location = {"cuda:0": "cpu"} if device.type == "cpu" else None
    return torch.load(BytesIO(model_file), map_location=device_map_location)


def load_model_config() -> dict:
    model_config_path = f"model-configs/{bucket_config.base_model}.json"
    return S3Handler.get(bucket_config.base_data_bucket, model_config_path)