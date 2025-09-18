"""
Jarvis Settings Configuration Manager
Handles loading, saving, and managing all application settings
"""

import json
import os
from typing import Dict, Any

class SettingsManager:
    def __init__(self):
        self.settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'jarvis_settings.json')
        self.default_settings = {
            "assistant": {
                "wake_word_enabled": True,
                "voice_feedback_enabled": True,
                "continuous_listening": False,
                "wake_word": "lumina"
            },
            "contacts": {
                "auto_format_phone": True,
                "whatsapp_integration": True,
                "default_country_code": "+91"
            },
            "media": {
                "system_volume_control": True,
                "media_key_integration": True,
                "youtube_shortcuts": True
            },
            "display": {
                "always_on_top": False,
                "theme_color": "#00AAFF",
                "minimize_to_tray": False,
                "window_position": [1500, 370],
                "window_size": [450, 800]
            },
            "system": {
                "start_with_windows": False,
                "microphone_permissions": True,
                "debug_mode": False
            },
            "applications": {
                "auto_scan_on_startup": False,
                "scan_paths": [
                    "C:\\Program Files",
                    "C:\\Program Files (x86)"
                ]
            }
        }
        self.settings = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """Load settings from JSON file or create with defaults"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_settings(self.default_settings, loaded_settings)
            else:
                # Create settings file with defaults
                self.save_settings(self.default_settings)
                return self.default_settings.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_settings.copy()

    def save_settings(self, settings: Dict[str, Any] = None) -> bool:
        """Save settings to JSON file"""
        try:
            settings_to_save = settings if settings else self.settings
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_to_save, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def get_setting(self, category: str, key: str, default=None):
        """Get a specific setting value"""
        try:
            return self.settings.get(category, {}).get(key, default)
        except Exception:
            return default

    def set_setting(self, category: str, key: str, value: Any) -> bool:
        """Set a specific setting value and save"""
        try:
            if category not in self.settings:
                self.settings[category] = {}
            self.settings[category][key] = value
            return self.save_settings()
        except Exception as e:
            print(f"Error setting {category}.{key}: {e}")
            return False

    def reset_to_defaults(self) -> bool:
        """Reset all settings to default values"""
        try:
            self.settings = self.default_settings.copy()
            return self.save_settings()
        except Exception as e:
            print(f"Error resetting settings: {e}")
            return False

    def _merge_settings(self, defaults: Dict, loaded: Dict) -> Dict:
        """Recursively merge loaded settings with defaults"""
        result = defaults.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        return result

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings"""
        return self.settings.copy()

    def update_settings(self, new_settings: Dict[str, Any]) -> bool:
        """Update multiple settings at once"""
        try:
            self.settings = self._merge_settings(self.settings, new_settings)
            return self.save_settings()
        except Exception as e:
            print(f"Error updating settings: {e}")
            return False

# Global settings manager instance
settings_manager = SettingsManager()