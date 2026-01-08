import os
import json
import logging
import yaml
from pathlib import Path
from datetime import date, datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

class FoodAgentConfig:
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.settings_file = self.config_dir / "settings.json"
        
        self.data_dir = self._get_data_folder()
        self.daily_log_dir = self.data_dir / "daily"
        self.catalog_dir = self.data_dir / "catalog"
        self.catalog_file = self.catalog_dir / "catalog.json"
        
        # Schemas and app.yaml are part of the source distribution
        self.package_root = Path(__file__).parent.parent
        self.project_root = self.package_root.parent
        self.schemas_dir = self.project_root / "schemas"
        
        self.app_config = self._load_app_config()
        self.day_cutoff_hour = self.app_config.get("day_cutoff_hour", 0)

    def _load_app_config(self) -> dict:
        config_path = self.package_root / "app.yaml"
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.error(f"Error loading app.yaml: {e}")
        return {}

    def get_effective_today(self) -> date:
        """
        Return the 'effective' date for today.
        If current time is before day_cutoff_hour, return the previous day.
        """
        now = datetime.now()
        if now.hour < self.day_cutoff_hour:
            return (now - timedelta(days=1)).date()
        return now.date()

    def _get_config_dir(self) -> Path:
        """
        Get the configuration directory.
        Defaults to ~/.config/food-agent or XDG_CONFIG_HOME/food-agent
        """
        xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config_home:
            return Path(xdg_config_home) / "food-agent"
        return Path.home() / ".config" / "food-agent"

    def _get_data_folder(self) -> Path:
        """
        Determine the data folder path with the following priority:
        1. Environment variable FOOD_AGENT_DATA
        2. 'data_path' in ~/.config/food-agent/settings.json
        3. XDG Data Home (~/.local/share/food-agent)
        """
        # 1. Environment Variable
        env_path = os.environ.get("FOOD_AGENT_DATA")
        if env_path:
            logger.debug(f"Using data path from env var: {env_path}")
            return Path(env_path).expanduser().resolve()

        # 2. Settings File
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r") as f:
                    settings = json.load(f)
                    data_path = settings.get("data_path")
                    if data_path:
                        logger.debug(f"Using data path from settings file: {data_path}")
                        return Path(data_path).expanduser().resolve()
            except json.JSONDecodeError:
                logger.error(f"Error decoding settings file: {self.settings_file}")
            except Exception as e:
                logger.error(f"Error reading settings file: {e}")

        # 3. XDG Data Home (Default)
        xdg_data_home = os.environ.get("XDG_DATA_HOME")
        if xdg_data_home:
            base_path = Path(xdg_data_home)
        else:
            base_path = Path.home() / ".local" / "share"
        
        default_path = base_path / "food-agent"
        logger.debug(f"Using default XDG data path: {default_path}")
        return default_path

    def ensure_directories(self):
        """Ensure all necessary directories exist."""
        try:
            os.makedirs(self.daily_log_dir, exist_ok=True)
            os.makedirs(self.catalog_dir, exist_ok=True)
            os.makedirs(self.schemas_dir, exist_ok=True)
            os.makedirs(self.config_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            raise