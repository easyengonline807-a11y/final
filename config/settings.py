#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер конфигурации приложения
"""

import json
import os
from typing import Any, Dict


class ConfigManager:
    """Управление конфигурацией приложения."""
    
    def __init__(self, config_path: str = "config.json"):
        """Инициализация менеджера конфигурации."""
        self.config_path = config_path
        self.config = self.load_config()  # ← ИСПРАВЛЕНО: без подчеркивания
        
        # Проверка наличия новых параметров и добавление значений по умолчанию
        self._ensure_chunker_settings()
    
    def load_config(self) -> Dict[str, Any]:
        """Загрузить конфигурацию из JSON файла."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"❌ Файл конфигурации не найден: {self.config_path}"
            )
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"✅ Конфигурация загружена из {self.config_path}")
            return config
        except json.JSONDecodeError as e:
            raise ValueError(
                f"❌ Ошибка в JSON конфигурации: {e}"
            )
        except Exception as e:
            raise Exception(
                f"❌ Не удалось загрузить конфигурацию: {e}"
            )
    
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
                print(f"ℹ️ Добавлен параметр конфигурации: {key} = {value}")
        
        if updated:
            self.save_config()
            print("✅ Конфигурация обновлена с новыми параметрами")
    
    def save_config(self):
        """Сохранить конфигурацию в JSON файл."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"💾 Конфигурация сохранена в {self.config_path}")
        except Exception as e:
            print(f"❌ Ошибка сохранения конфигурации: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение параметра."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Установить значение параметра."""
        self.config[key] = value
    
    def get_chunks_folder(self) -> str:
        """Получить путь к папке с чанками."""
        return self.config.get('chunks_folder', 'chunks')
    
    def get_prompts_folder(self) -> str:
        """Получить путь к папке с промптами."""
        return self.config.get('prompts_folder', 'prompts')
    
    def get_model(self) -> str:
        """Получить имя модели."""
        return self.config.get('model', 'meta-llama/llama-guard-4-12b')
    
    def get_temperature(self) -> float:
        """Получить температуру генерации."""
        return self.config.get('temperature', 0.8)
    
    def get_prompts_count(self) -> int:
        """Получить количество промптов для генерации."""
        return self.config.get('prompts_count', 5)
    
    def get_delay(self) -> int:
        """Получить задержку между запросами."""
        return self.config.get('delay', 1)
    
    def get_system_prompt(self) -> str:
        """Получить системный промпт."""
        return self.config.get('system_prompt', '')
