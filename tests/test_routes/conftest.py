import os
import signal
import time
from dotenv import load_dotenv
import pytest
from testcontainers.compose import DockerCompose
from sqlalchemy import text
from s3 import S3Handler, bucket_config
from utils import *
from app import app
from db.database import db



@pytest.fixture(scope="session", autouse=True)
def docker_compose_services(request):
    load_dotenv(dotenv_path=".example.env")
    
    compose = DockerCompose(
        context="dev-infrastructure",
        compose_file_name="docker-compose.yml"
    )

    os.environ["ADMINER_PORT"] = "0"

    compose.start()
    
    def handle_sigint(signum, frame):
        print("\nSIGINT received, stopping Docker Compose...")
        compose.stop()
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, handle_sigint)
    
    def wait_for_services():
        time_out = 30
        for sec in range(time_out):
            print(f"Waiting for services... ({sec} sec.)")
            try:
                with app.app_context():
                    db.session.execute(text("SELECT 1"))
                    
                bucket_config.minio_host = "http://localhost"
                S3Handler.get(bucket_config.base_data_bucket, "nationalities.json")
                return
            except Exception as e:
                print(f"Services not up ({e}).")
                time.sleep(1)
        
        compose.stop()
        raise RuntimeError("Starting services timed out.")
    
    wait_for_services()
    
    def teardown():
        compose.stop()
    
    request.addfinalizer(teardown)