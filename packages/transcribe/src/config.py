"""Configuration management for YouTube transcription pipeline."""

import os
from pathlib import Path
import yaml


def load_config(config_path: str = "config.yaml") -> dict:
    """
    Load and validate configuration from YAML file.

    Args:
        config_path: Path to config.yaml file

    Returns:
        Dictionary containing configuration

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If required configuration is missing
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Validate required sections
    required_sections = ['youtube', 'paths', 'whisper', 'processing']
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")

    # Create directories if they don't exist
    base_dir = Path(config_path).parent
    for path_key, path_value in config['paths'].items():
        full_path = base_dir / path_value
        full_path.mkdir(parents=True, exist_ok=True)

    return config


def get_path(config: dict, path_key: str, base_dir: str = None) -> Path:
    """
    Get absolute path from config.

    Args:
        config: Configuration dictionary
        path_key: Key in config['paths']
        base_dir: Base directory for relative paths (defaults to src/)

    Returns:
        Absolute Path object
    """
    if base_dir is None:
        base_dir = Path(__file__).parent

    relative_path = config['paths'][path_key]
    return (base_dir / relative_path).resolve()


if __name__ == "__main__":
    # Test configuration loading
    config = load_config("config.yaml")
    print("Configuration loaded successfully!")
    print(f"Channel: {config['youtube']['channel_url']}")
    print(f"Whisper model: {config['whisper']['model']}")
    print(f"Audio path: {get_path(config, 'raw_audio')}")
