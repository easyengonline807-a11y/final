#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text Chunker - разбивка текста на чанки
Версия: 1.0
"""

import re
from typing import List, Tuple


class TextChunker:
    """Класс для разбивки текста на чанки с умным объединением."""
    
    @staticmethod
    def split_text(text: str, max_size: int = 2000, 
                   tolerance: float = 0.10, 
                   min_threshold: float = 0.50) -> Tuple[List[str], int]:
        """
        Разбить текст на чанки с автоматическим объединением коротких.
        
        Args:
            text: исходный текст
            max_size: целевой размер чанка в символах
            tolerance: допуск ±X% от целевого размера (0.10 = ±10%)
            min_threshold: порог короткого чанка (0.50 = 50% от базового)
        
        Returns:
            (список чанков, количество объединенных чанков)
        """
        if not text or not text.strip():
            return [], 0
        
        # Шаг 1: Разбить по абзацам
        paragraphs = TextChunker._split_by_paragraphs(text)
        
        # Шаг 2: Собрать чанки с учетом допуска
        chunks = TextChunker._build_chunks(paragraphs, max_size, tolerance)
        
        # Шаг 3: Разбить слишком большие чанки по предложениям
        chunks = TextChunker._split_oversized_chunks(chunks, max_size, tolerance)
        
        # Шаг 4: Объединить слишком короткие чанки
        chunks, merged_count = TextChunker._merge_short_chunks(
            chunks, max_size, min_threshold
        )
        
        return chunks, merged_count
    
    @staticmethod
    def _split_by_paragraphs(text: str) -> List[str]:
        """Разбить текст по абзацам (одинарный перенос строки)."""
        # Разбиваем по \n, удаляем пустые строки
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        return paragraphs
    
    @staticmethod
    def _build_chunks(paragraphs: List[str], max_size: int, 
                      tolerance: float) -> List[str]:
        """
        Собрать чанки из абзацев с учетом допуска.
        
        Логика:
        - Если текущий чанк < max_size И добавление абзаца ≤ max_size * (1 + tolerance) → добавляем
        - Иначе → начинаем новый чанк
        """
        chunks = []
        current_chunk = []
        current_length = 0
        
        max_allowed = int(max_size * (1 + tolerance))
        
        for para in paragraphs:
            para_length = len(para)
            
            # Первый абзац в чанке
            if not current_chunk:
                current_chunk.append(para)
                current_length = para_length
                continue
            
            # Проверяем, можно ли добавить абзац
            new_length = current_length + para_length + 1  # +1 за \n
            
            if current_length < max_size:
                # Текущий чанк еще не достиг базового размера
                if new_length <= max_allowed:
                    # Добавление не выходит за допустимый предел
                    current_chunk.append(para)
                    current_length = new_length
                else:
                    # Добавление выходит за предел → начинаем новый чанк
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = [para]
                    current_length = para_length
            else:
                # Текущий чанк уже достиг базового размера → начинаем новый
                chunks.append('\n'.join(current_chunk))
                current_chunk = [para]
                current_length = para_length
        
        # Добавляем последний чанк
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    @staticmethod
    def _split_oversized_chunks(chunks: List[str], max_size: int,
                                tolerance: float) -> List[str]:
        """
        Разбить чанки, которые превышают max_size * (1 + tolerance), по предложениям.
        """
        max_allowed = int(max_size * (1 + tolerance))
        result = []
        
        for chunk in chunks:
            if len(chunk) <= max_allowed:
                result.append(chunk)
            else:
                # Разбиваем по предложениям
                sentences = TextChunker._split_by_sentences(chunk)
                sub_chunks = TextChunker._build_chunks(
                    sentences, max_size, tolerance
                )
                result.extend(sub_chunks)
        
        return result
    
    @staticmethod
    def _split_by_sentences(text: str) -> List[str]:
        """
        Разбить текст по предложениям.
        
        Ищем точку, восклицательный или вопросительный знак с пробелом после.
        """
        # Паттерн: точка/!/? + пробел/перенос строки/конец строки
        pattern = r'(?<=[.!?])\s+'
        sentences = re.split(pattern, text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    @staticmethod
    def _merge_short_chunks(chunks: List[str], max_size: int,
                           min_threshold: float) -> Tuple[List[str], int]:
        """
        Объединить короткие чанки с предыдущими.
        
        Короткий чанк = длина < max_size * min_threshold
        
        Returns:
            (обновленный список чанков, количество объединенных)
        """
        min_size = int(max_size * min_threshold)
        merged_count = 0
        result = []
        
        for chunk in chunks:
            if len(chunk) < min_size and result:
                # Объединяем с предыдущим чанком
                result[-1] = result[-1] + '\n' + chunk
                merged_count += 1
            else:
                result.append(chunk)
        
        return result, merged_count
