import yaml


def load_config(env: str = "dev") -> dict:
    with open(f"config/app-{env}.yaml", "r") as f:
        return yaml.safe_load(f)
