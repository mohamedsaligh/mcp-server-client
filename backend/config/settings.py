import yaml
from pathlib import Path

class Settings:
    def __init__(self, env: str = "dev"):
        config_path = Path(f"config/app-{env}.yaml")
        with config_path.open() as f:
            cfg = yaml.safe_load(f)
        self.database_url = cfg["database"]["url"]

settings = Settings()
