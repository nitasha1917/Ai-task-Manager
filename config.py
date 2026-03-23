"""
Configuration Management: Centralized settings and environment variables.
Handles all configuration with validation and defaults.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass, field, asdict
import json


@dataclass
class APIConfig:
    """API Configuration Settings."""
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite"))
    api_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    def validate(self) -> bool:
        """Validate API configuration."""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        if not self.gemini_model:
            raise ValueError("GEMINI_MODEL environment variable is required")
        return True


@dataclass
class AppConfig:
    """Application Configuration Settings."""
    app_name: str = "Agentic AI Study Planner"
    app_version: str = "1.0.0"
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"


@dataclass
class PathConfig:
    """Path Configuration Settings."""
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    memory_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "memory")
    log_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "logs")
    data_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "data")
    
    memory_file: Path = field(init=False)
    log_file: Path = field(init=False)
    
    def __post_init__(self):
        """Initialize derived paths."""
        self.memory_file = self.memory_dir / "memory.json"
        self.log_file = self.log_dir / "app.log"
        self.ensure_directories()
    
    def ensure_directories(self) -> None:
        """Create all required directories if they don't exist."""
        for directory in [self.memory_dir, self.log_dir, self.data_dir]:
            directory.mkdir(parents=True, exist_ok=True)


@dataclass
class StudyPlanConfig:
    """Study Plan Configuration Settings."""
    default_duration_days: int = 30
    default_hours_per_day: float = 2.0
    min_duration_days: int = 1
    max_duration_days: int = 365
    min_hours_per_day: float = 0.5
    max_hours_per_day: float = 12.0
    min_topics: int = 3
    max_topics: int = 20


@dataclass
class UIConfig:
    """Streamlit UI Configuration Settings."""
    page_title: str = "Agentic AI Study Planner"
    page_icon: str = "🎓"
    layout: str = "wide"
    theme_primary: str = "#667eea"
    theme_secondary: str = "#764ba2"
    sidebar_state: str = "expanded"


@dataclass
class Config:
    """Main Configuration Class - Combines all settings."""
    api: APIConfig = field(default_factory=APIConfig)
    app: AppConfig = field(default_factory=AppConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    study_plan: StudyPlanConfig = field(default_factory=StudyPlanConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    
    @staticmethod
    def load_from_env() -> "Config":
        """Load configuration from environment variables."""
        config = Config()
        config.api.validate()
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "api": asdict(self.api),
            "app": asdict(self.app),
            "paths": {
                "project_root": str(self.paths.project_root),
                "memory_dir": str(self.paths.memory_dir),
                "log_dir": str(self.paths.log_dir),
                "data_dir": str(self.paths.data_dir),
                "memory_file": str(self.paths.memory_file),
                "log_file": str(self.paths.log_file),
            },
            "study_plan": asdict(self.study_plan),
            "ui": asdict(self.ui),
        }
    
    def save_to_file(self, filepath: str) -> bool:
        """Save configuration to JSON file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
            return False


# Global configuration instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get or create the global Config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config.load_from_env()
    return _config_instance


def reset_config() -> None:
    """Reset the global configuration instance (useful for testing)."""
    global _config_instance
    _config_instance = None
