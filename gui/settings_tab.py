import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import json
from pathlib import Path

class SettingsTab:
    """Вкладка настроек"""
    
    def __init__(self, parent, config_manager):
        self.parent = parent
        self.config = config_manager
        self.create_tab()

        def _create_chunker_section(self, parent):
            """Создать секцию разбивки текста."""
            import os
            from tkinter import filedialog, messagebox
            from logic.text_chunker import TextChunker
            
            # Frame для разбивки
            chunker_frame = tk.LabelFrame(
                parent, 
                text="✂️ Разбивка текста на чанки",
                font=('Arial', 9, 'bold'),
                padx=10,
                pady=10
            )
            chunker_frame.pack(fill='x', padx=10, pady=(0, 10))
            
            # Строка 1: Исходный файл
            row1 = tk.Frame(chunker_frame)
            row1.pack(fill='x', pady=(0, 5))
            
            tk.Label(row1, text="Исходный файл:", font=('Arial', 9)).pack(
                side='left', padx=(0, 5)
            )
            
            self.source_file_var = tk.StringVar(
                value=self.config_manager.get('source_text_file', '')
            )
            
            source_entry = tk.Entry(
                row1, 
                textvariable=self.source_file_var,
                font=('Arial', 9),
                width=40
            )
            source_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
            
            def select_source_file():
                filepath = filedialog.askopenfilename(
                    title="Выберите текстовый файл",
                    filetypes=[
                        ("Текстовые файлы", "*.txt"),
                        ("Все файлы", "*.*")
                    ]
                )
                if filepath:
                    self.source_file_var.set(filepath)
                    self.config_manager.set('source_text_file', filepath)
                    self.config_manager.save_config()
            
            tk.Button(
                row1,
                text="📁",
                command=select_source_file,
                width=3
            ).pack(side='left')
            
            # Строка 2: Размер чанка
            row2 = tk.Frame(chunker_frame)
            row2.pack(fill='x', pady=(0, 5))
            
            tk.Label(row2, text="Размер чанка:", font=('Arial', 9)).pack(
                side='left', padx=(0, 5)
            )
            
            self.chunk_size_var = tk.IntVar(
                value=self.config_manager.get('chunk_size', 2000)
            )
            
            chunk_spinbox = tk.Spinbox(
                row2,
                from_=500,
                to=10000,
                increment=100,
                textvariable=self.chunk_size_var,
                font=('Arial', 9),
                width=10,
                command=lambda: self.config_manager.set('chunk_size', self.chunk_size_var.get())
            )
            chunk_spinbox.pack(side='left', padx=(0, 5))
            
            tk.Label(row2, text="символов", font=('Arial', 9)).pack(
                side='left', padx=(0, 10)
            )
            
            tk.Label(
                row2, 
                text="(допуск ±10%, объединение < 50%)",
                font=('Arial', 8),
                fg='gray'
            ).pack(side='left')
            
            # Строка 3: Кнопка разбивки
            def split_text():
                """Обработчик разбивки текста."""
                source_file = self.source_file_var.get()
                
                # Валидация
                if not source_file:
                    messagebox.showwarning(
                        "Внимание",
                        "Выберите исходный текстовый файл!"
                    )
                    return
                
                if not os.path.exists(source_file):
                    messagebox.showerror(
                        "Ошибка",
                        f"Файл не найден:\n{source_file}"
                    )
                    return
                
                # Читаем файл
                try:
                    with open(source_file, 'r', encoding='utf-8') as f:
                        text = f.read()
                except Exception as e:
                    messagebox.showerror(
                        "Ошибка чтения",
                        f"Не удалось прочитать файл:\n{str(e)}"
                    )
                    return
                
                if not text.strip():
                    messagebox.showwarning(
                        "Внимание",
                        "Файл пустой!"
                    )
                    return
                
                # Параметры разбивки
                chunk_size = self.chunk_size_var.get()
                tolerance = self.config_manager.get('chunk_tolerance', 0.10)
                min_threshold = self.config_manager.get('chunk_min_threshold', 0.50)
                
                # Разбиваем текст
                try:
                    chunks, merged_count = TextChunker.split_text(
                        text, chunk_size, tolerance, min_threshold
                    )
                except Exception as e:
                    messagebox.showerror(
                        "Ошибка разбивки",
                        f"Не удалось разбить текст:\n{str(e)}"
                    )
                    return
                
                if not chunks:
                    messagebox.showwarning(
                        "Внимание",
                        "Не удалось создать чанки!"
                    )
                    return
                
                # Проверяем папку chunks
                chunks_folder = self.config_manager.get('chunks_folder', 'chunks')
                
                if os.path.exists(chunks_folder) and os.listdir(chunks_folder):
                    # Папка не пустая, спрашиваем
                    response = messagebox.askyesno(
                        "Папка не пустая",
                        f"В папке '{chunks_folder}' уже есть файлы.\n"
                        "Удалить их перед созданием новых чанков?",
                        icon='warning'
                    )
                    
                    if response:
                        # Удаляем старые файлы
                        try:
                            for filename in os.listdir(chunks_folder):
                                filepath = os.path.join(chunks_folder, filename)
                                if os.path.isfile(filepath):
                                    os.remove(filepath)
                        except Exception as e:
                            messagebox.showerror(
                                "Ошибка",
                                f"Не удалось очистить папку:\n{str(e)}"
                            )
                            return
                else:
                    # Создаем папку если её нет
                    os.makedirs(chunks_folder, exist_ok=True)
                
                # Сохраняем чанки
                try:
                    for i, chunk in enumerate(chunks, 1):
                        filename = f"{i:02d}.txt"
                        filepath = os.path.join(chunks_folder, filename)
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(chunk)
                except Exception as e:
                    messagebox.showerror(
                        "Ошибка сохранения",
                        f"Не удалось сохранить чанки:\n{str(e)}"
                    )
                    return
                
                # Успех!
                merge_info = f" (объединено {merged_count})" if merged_count > 0 else ""
                messagebox.showinfo(
                    "Успех",
                    f"✅ Создано {len(chunks)} чанков{merge_info}\n"
                    f"Папка: {chunks_folder}"
                )
                
                # Обновляем статистику если есть
                if hasattr(self, 'update_file_stats'):
                    self.update_file_stats()
            
            split_btn = tk.Button(
                chunker_frame,
                text="✂️ Разбить на чанки",
                command=split_text,
                font=('Arial', 10, 'bold'),
                bg='#2196F3',
                fg='white',
                cursor='hand2'
            )
            split_btn.pack(fill='x', pady=(5, 0))

    
    def load_models_from_config(self):
        """📌 НОВОЕ: Загрузить список моделей из config.json"""
        try:
            # Пытаемся загрузить из config.json
            if hasattr(self.config, 'production_models'):
                return self.config.production_models
            
            # Fallback: загружаем напрямую из файла
            with open('config.json', 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                models = config_data.get('production_models', [])
                if models:
                    return models
        except:
            pass
        
        # Последний fallback - Production модели
        return [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "meta-llama/llama-guard-4-12b"
        ]
    
    def create_tab(self):
        """Создание вкладки настроек"""
        container = tk.Frame(self.parent, bg="#ffffff")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        row = 0
        
        # Модель
        tk.Label(container, text="🤖 Модель:", bg="#ffffff", fg="black", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=10)
        self.model_var = tk.StringVar(value=self.config.get("model", "llama-3.3-70b-versatile"))
        model_combo = ttk.Combobox(container, textvariable=self.model_var, width=40, state="readonly")
        
        # ✅ ИСПРАВЛЕНО: Загружаем модели из config.json вместо hardcode
        available_models = self.load_models_from_config()
        model_combo['values'] = available_models
        
        model_combo.grid(row=row, column=1, sticky=tk.W, pady=10)
        model_combo.bind("<<ComboboxSelected>>", lambda e: self.on_setting_change())
        row += 1
        
        # Температура
        tk.Label(container, text="🌡️ Температура:", bg="#ffffff", fg="black", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=10)
        self.temp_var = tk.DoubleVar(value=self.config.get("temperature", 0.7))
        temp_frame = tk.Frame(container, bg="#ffffff")
        temp_frame.grid(row=row, column=1, sticky=tk.W, pady=10)
        
        tk.Scale(
            temp_frame, 
            from_=0.0, 
            to=2.0, 
            resolution=0.1, 
            orient=tk.HORIZONTAL, 
            variable=self.temp_var, 
            length=300,
            bg="#ffffff",
            fg="black",
            troughcolor="#e0e0e0",
            highlightthickness=0,
            command=lambda e: self.on_setting_change()
        ).pack(side=tk.LEFT)
        
        temp_label = tk.Label(temp_frame, width=5, bg="#ffffff", fg="black")
        temp_label.pack(side=tk.LEFT, padx=5)
        
        def update_temp_label(*args):
            temp_label.config(text=f"{self.temp_var.get():.2f}")
        self.temp_var.trace_add('write', update_temp_label)
        update_temp_label()
        row += 1
        
        # Количество промптов
        tk.Label(container, text="📊 Количество промптов:", bg="#ffffff", fg="black", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=10)
        self.prompts_count_var = tk.IntVar(value=self.config.get("prompts_count", 5))
        ttk.Spinbox(container, from_=1, to=10, textvariable=self.prompts_count_var, width=10, command=self.on_setting_change).grid(row=row, column=1, sticky=tk.W, pady=10)
        row += 1
        
        # Задержка
        tk.Label(container, text="⏱️ Задержка между файлами:", bg="#ffffff", fg="black", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=10)
        delay_frame = tk.Frame(container, bg="#ffffff")
        delay_frame.grid(row=row, column=1, sticky=tk.W, pady=10)
        self.delay_var = tk.IntVar(value=self.config.get("delay", 1))
        ttk.Spinbox(delay_frame, from_=0, to=60, textvariable=self.delay_var, width=10, command=self.on_setting_change).pack(side=tk.LEFT)
        tk.Label(delay_frame, text=" сек", bg="#ffffff", fg="black").pack(side=tk.LEFT)
        tk.Label(delay_frame, text="(Авто 0 если ключей > 5)", bg="#ffffff", fg="gray", font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Сохранять сырые ответы
        self.save_raw_var = tk.BooleanVar(value=self.config.get("save_raw_responses", False))
        tk.Checkbutton(
            container,
            text="☑️ Сохранять сырые ответы API (для отладки)",
            variable=self.save_raw_var,
            bg="#ffffff",
            fg="black",
            selectcolor="#e0e0e0",
            font=("Arial", 10),
            command=self.on_setting_change
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=10)
        row += 1
        
        # Папка с чанками
        tk.Label(container, text="📁 Папка с чанками:", bg="#ffffff", fg="black", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=10)
        chunks_frame = tk.Frame(container, bg="#ffffff")
        chunks_frame.grid(row=row, column=1, sticky=tk.W, pady=10)
        self.chunks_folder_var = tk.StringVar(value=self.config.get("chunks_folder", ""))
        tk.Entry(chunks_frame, textvariable=self.chunks_folder_var, width=35, bg="white", fg="black", insertbackground="black").pack(side=tk.LEFT)
        tk.Button(chunks_frame, text="📂", command=lambda: self.select_folder("chunks_folder"), width=3, bg="#e0e0e0", fg="black", cursor="hand2").pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Папка с промптами
        tk.Label(container, text="💾 Папка с промптами:", bg="#ffffff", fg="black", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=10)
        prompts_frame = tk.Frame(container, bg="#ffffff")
        prompts_frame.grid(row=row, column=1, sticky=tk.W, pady=10)
        self.prompts_folder_var = tk.StringVar(value=self.config.get("prompts_folder", ""))
        tk.Entry(prompts_frame, textvariable=self.prompts_folder_var, width=35, bg="white", fg="black", insertbackground="black").pack(side=tk.LEFT)
        tk.Button(prompts_frame, text="📂", command=lambda: self.select_folder("prompts_folder"), width=3, bg="#e0e0e0", fg="black", cursor="hand2").pack(side=tk.LEFT, padx=5)
        row += 1
        
        # System prompt
        tk.Label(container, text="📝 System Prompt:", bg="#ffffff", fg="black", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.NW, pady=10)
        self.system_prompt_text = scrolledtext.ScrolledText(
            container, 
            width=50, 
            height=8, 
            font=("Consolas", 9),
            bg="white",
            fg="black",
            insertbackground="black",
            wrap=tk.WORD
        )
        self.system_prompt_text.grid(row=row, column=1, sticky=tk.W, pady=10)
        
        default_prompt = self.config.get("system_prompt", 
            "Ты создаешь промпты для генерации исторических изображений. "
            "На основе предоставленного текста о военной истории создай {n} детальных описаний "
            "ключевых сцен для генератора изображений. "
            "Каждый промпт должен быть на русском языке, содержать описание сцены, персонажей, "
            "техники, окружения и атмосферы. Промпты должны быть визуально яркими и детальными. "
            "Каждый промпт пиши с новой строки без нумерации и лишних символов.")
        
        self.system_prompt_text.insert(1.0, default_prompt)
        self.system_prompt_text.bind("<KeyRelease>", lambda e: self.on_setting_change())
    
    def select_folder(self, field_name):
        """Выбор папки"""
        folder = filedialog.askdirectory()
        if folder:
            if field_name == "chunks_folder":
                self.chunks_folder_var.set(folder)
            elif field_name == "prompts_folder":
                self.prompts_folder_var.set(folder)
            self.on_setting_change()
    
    def on_setting_change(self):
        """Автосохранение при изменении настроек"""
        self.config.config["model"] = self.model_var.get()
        self.config.config["temperature"] = self.temp_var.get()
        self.config.config["chunks_folder"] = self.chunks_folder_var.get()
        self.config.config["prompts_folder"] = self.prompts_folder_var.get()
        self.config.config["system_prompt"] = self.system_prompt_text.get(1.0, tk.END).strip()
        self.config.config["prompts_count"] = self.prompts_count_var.get()
        self.config.config["delay"] = self.delay_var.get()
        self.config.config["save_raw_responses"] = self.save_raw_var.get()
        self.config.save_config()
