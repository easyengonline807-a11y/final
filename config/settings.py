import json
import os

class ConfigManager:
    """Управление настройками программы (config.json)"""
    
    def __init__(self, config_path: str = "config.json"):
        """Инициализация менеджера конфигурации."""
        self.config_path = config_path
        self.config = self._load_config()
        
        # Проверка наличия новых параметров и добавление значений по умолчанию
        self._ensure_chunker_settings()
    
    def _ensure_chunker_settings(self):
        """Добавить настройки разбивки текста, если их нет."""
        defaults = {
            'source_text_file': '',
            'chunk_size': 2000,
            'chunk_tolerance': 0.10,
            'chunk_min_threshold': 0.50
        }
        
        updated = False
        for key, value in defaults.items():
            if key not in self.config:
                self.config[key] = value
                updated = True
        
        if updated:
            self.save_config()
            
    def load_config(self):
        """Загрузка конфигурации из файла"""
        default_config = {
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.7,
            "chunks_folder": "",
            "prompts_folder": "",
            "system_prompt": "",
            "prompts_count": 5,
            "delay": 1,
            "save_raw_responses": False
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Объединяем с default (на случай новых полей)
                    default_config.update(loaded_config)
                    return default_config
            except:
                return default_config
        else:
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config=None):
        """Сохранение конфигурации в файл"""
        if config:
            self.config = config
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get(self, key, default=None):
        """Получить значение настройки"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Установить значение настройки"""
        self.config[key] = value
        self.save_config()
