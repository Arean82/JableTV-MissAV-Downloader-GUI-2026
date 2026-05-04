import os
import json

class ConfigManager:
    """Manages application settings via settings.json."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        self.config_path = os.path.join(os.path.dirname(__file__), "..", "settings.json")
        self.defaults = {
            "save_path": "download",
            "max_concurrent": 3,
            "speed_limit": 0, # 0 = Unlimited
            "language": "zh",
            "theme": "dark",
            "resolution": "highest"
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for k, v in self.defaults.items():
                        if k not in self.data:
                            self.data[k] = v
            except Exception as e:
                print(f"[Config] Error loading settings: {e}")
                self.data = self.defaults.copy()
        else:
            self.data = self.defaults.copy()
            self.save()

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Config] Error saving settings: {e}")

def get_config():
    return ConfigManager()
