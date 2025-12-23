"""
Модуль для проверки и улучшения сгенерированных промптов через Groq API.
"""

import time
from pathlib import Path
from typing import Dict
import groq


class VerificationProcessor:
    """Обработчик проверки и улучшения промптов через AI."""
    
    def __init__(self, api_client, logger):
        """
        Инициализация процессора верификации.
        """
        self.api_client = api_client
        self.logger = logger
        self.stats = {
            'total': 0,
            'improved': 0, 
            'unchanged': 0,
            'errors': 0
        }
        self.start_time = None
        
    def verify_prompts_folder(self, prompts_folder: Path, verification_prompt: str, progress_callback=None):
        """
        Проверить все файлы с промптами в указанной папке.
        """
        self.stats = {'total': 0, 'improved': 0, 'unchanged': 0, 'errors': 0}
        self.start_time = time.time()
        
        # Получить все .txt файлы
        prompt_files = sorted(Path(prompts_folder).glob('*.txt'))
        total_files = len(prompt_files)
        
        if total_files == 0:
            self.logger.log("⚠️ Нет файлов для проверки в папке prompts", "warning")
            return self.stats
        
        self.logger.log(f"🔍 Начало проверки {total_files} файлов...", "info")
        
        # Обработать каждый файл
        for index, file_path in enumerate(prompt_files, 1):
            # Обновить прогресс
            if progress_callback:
                progress_callback(index, total_files, file_path.name)
            
            self.logger.log(f"📄 Проверяется файл {index}/{total_files}: {file_path.name}", "info")
            
            # Проверить один файл
            result = self.verify_single_file(file_path, verification_prompt)
            self.stats['total'] += 1
            self.stats[result] += 1
            
        # Вычислить время выполнения
        elapsed_time = time.time() - self.start_time
        self.logger.log(self._format_final_stats(elapsed_time), "success")
        
        return self.stats
    
    def verify_single_file(self, file_path: Path, verification_prompt: str):
        """
        Проверить и улучшить промпты в одном файле.
        """
        try:
            # 1. Прочитать все промпты из файла
            original_content = file_path.read_text(encoding='utf-8').strip()
            
            if not original_content:
                self.logger.log(f"⚠️ Файл {file_path.name} пуст, пропускается", "warning")
                return 'unchanged'
            
            # 2. Отправить в Groq API
            self.logger.log(f"🔄 Отправка запроса в API для {file_path.name}...", "info")
            
            response, status = self.api_client.send_request(
                user_message=original_content,
                system_prompt=verification_prompt,
                model=self.api_client.key_manager.config.get('model'),
                temperature=self.api_client.key_manager.config.get('temperature', 1.0)
            )
            
            if status != "success" or not response:
                self.logger.log(f"❌ Ошибка API при проверке {file_path.name}", "error")
                return 'errors'
            
            # 3. Получить улучшенный контент
            improved_content = response.strip()
            
            # 4. Проверить, есть ли изменения
            original_normalized = ' '.join(original_content.split())
            improved_normalized = ' '.join(improved_content.split())
            
            if original_normalized != improved_normalized:
                # 5. Перезаписать файл с улучшенными промптами
                file_path.write_text(improved_content, encoding='utf-8')
                self.logger.log(f"✅ Улучшен: {file_path.name}", "success")
                return 'improved'
            else:
                self.logger.log(f"ℹ️ Без изменений: {file_path.name}", "info")
                return 'unchanged'
                
        except Exception as e:
            self.logger.log(f"❌ Ошибка при проверке {file_path.name}: {e}", "error")
            return 'errors'
    
    def _format_final_stats(self, elapsed_time: float):
        """
        Форматировать итоговую статистику.
        """
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        
        improved_percent = (self.stats['improved'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
        unchanged_percent = (self.stats['unchanged'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
        
        stats_text = f"""
╔══════════════════════════════════════╗
║   ✅ ПРОВЕРКА ЗАВЕРШЕНА!             ║
╠══════════════════════════════════════╣
║ 📊 Статистика:                       ║
║   • Обработано файлов: {self.stats['total']}            ║
║   • Улучшено: {self.stats['improved']} ({improved_percent:.1f}%)          ║
║   • Без изменений: {self.stats['unchanged']} ({unchanged_percent:.1f}%)   ║
║   • Ошибок: {self.stats['errors']}                      ║
║                                      ║
║ ⏱️  Время выполнения: {minutes} мин {seconds} сек      ║
╚══════════════════════════════════════╝
"""
        return stats_text
