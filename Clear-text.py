import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from deep_translator import GoogleTranslator
import re
import unicodedata
import pyperclip
import random
import threading

# =============================
# 1. Мәтінді тазалау функциялары
# =============================

def clean_hidden_chars(text):
    """Көрінбейтін таңбаларды өшіреді"""
    # Zero-width characters
    text = re.sub(r'[\u200B-\u200D\uFEFF\u2060]', '', text)
    # Control characters (қажетсіз)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', ' ', text)
    # Unicode нормализация
    text = unicodedata.normalize('NFKC', text)
    # Бос орындарды тазалау
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def humanize_text(text):
    """Мәтінді “адам жазғандай” етіп өзгертеді — синонимдер, құрылым"""
    synonyms = {
        "жасалды": ["орындалды", "аяқталды", "дайын", "жасап болдым"],
        "жақсы": ["өте жақсы", "тамаша", "жарайды", "жарамды"],
        "қолданыңыз": ["пайдаланыңыз", "қолдануға болады", "пайдалану керек"],
        "керек": ["қажет", "талап етіледі", "маңызды"],
        "болады": ["мүмкін", "шығады", "болуы мүмкін"],
        "айтады": ["деп тұр", "хабарлайды", "естіледі"],
        "мысалы": ["мысал ретінде", "мысалға алсақ", "дәл осылай"],
        "сондықтан": ["сол себепті", "осыдан", "дәл сондықтан"],
    }

    words = text.split()
    for i, word in enumerate(words):
        clean_word = word.strip('.,!?;:')
        if clean_word in synonyms:
            if random.random() > 0.4:  # 60% мүмкіндікпен ауыстырамыз
                new_word = random.choice(synonyms[clean_word])
                if word.endswith(('.', ',', '!', '?', ';', ':')):
                    words[i] = new_word + word[-1]
                else:
                    words[i] = new_word

    # Сөйлемдерді қысқарту/ұзарту үшін:
    sentences = ' '.join(words).split('. ')
    for i in range(len(sentences)):
        if len(sentences[i]) > 100 and random.random() > 0.7:
            # Ұзын сөйлемді екіге бөлу
            words_in_sent = sentences[i].split()
            mid = len(words_in_sent) // 2
            sentences[i] = '. '.join([
                ' '.join(words_in_sent[:mid]) + '.',
                ' '.join(words_in_sent[mid:]).capitalize()
            ])

    return '. '.join(sentences)

# =============================
# 2. Tkinter GUI
# =============================

class AntiPlagiarismCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🛡️ Антиплагиат Тазартқыш Pro")
        self.root.geometry("900x700")
        self.root.config(bg="#f8f9fa")

        # Стильдер
        self.font_title = ("Segoe UI", 18, "bold")
        self.font_normal = ("Segoe UI", 12)
        self.font_small = ("Segoe UI", 10)
        self.bg_color = "#f8f9fa"
        self.btn_primary = "#007bff"
        self.btn_success = "#28a745"
        self.btn_warning = "#ffc107"
        self.btn_danger = "#dc3545"
        self.text_bg = "white"
        self.text_fg = "#333"

        # Заголовок
        tk.Label(root, text="🛡️ ИИ-дан құтылу — Мәтінді тазалау", 
                 font=self.font_title, bg=self.bg_color, fg="#333").pack(pady=20)

        # Екі баған: сол жақта — енгізу, оң жақта — шығару
        main_frame = tk.Frame(root, bg=self.bg_color)
        main_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # Сол жақ: Енгізу
        left_frame = tk.Frame(main_frame, bg=self.bg_color)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        tk.Label(left_frame, text="📌 Бастапқы мәтін (ИИ-дан):", font=self.font_normal, bg=self.bg_color).pack(anchor="w")

        self.input_text = scrolledtext.ScrolledText(left_frame, width=50, height=20,
                                                   font=("Consolas", 11),
                                                   bg=self.text_bg, fg=self.text_fg,
                                                   relief="flat", padx=10, pady=10,
                                                   wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Оң жақ: Нәтиже
        right_frame = tk.Frame(main_frame, bg=self.bg_color)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        tk.Label(right_frame, text="✅ Тазартылған мәтін:", font=self.font_normal, bg=self.bg_color).pack(anchor="w")

        self.output_text = scrolledtext.ScrolledText(right_frame, width=50, height=20,
                                                     font=("Consolas", 11),
                                                     bg=self.text_bg, fg=self.text_fg,
                                                     relief="flat", padx=10, pady=10,
                                                     wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Батырмалар
        btn_frame = tk.Frame(root, bg=self.bg_color)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="📋 Clipboard-тан алу", font=self.font_normal,
                  bg=self.btn_primary, fg="white", relief="flat", padx=15, pady=8,
                  command=self.load_from_clipboard).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="🧹 Тазалау", font=self.font_normal,
                  bg=self.btn_success, fg="white", relief="flat", padx=25, pady=8,
                  command=self.start_cleaning).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="📋 Нәтижені clipboard-қа", font=self.font_normal,
                  bg=self.btn_warning, fg="black", relief="flat", padx=15, pady=8,
                  command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="🗑️ Тазарту", font=self.font_normal,
                  bg=self.btn_danger, fg="white", relief="flat", padx=20, pady=8,
                  command=self.clear_all).pack(side=tk.LEFT, padx=5)

        # Прогресс бар
        self.progress = ttk.Progressbar(root, orient="horizontal", length=700, mode="determinate")
        self.progress.pack(pady=10)

        # Status label
        self.status_label = tk.Label(root, text="✅ Дайын — мәтін енгізіңіз немесе clipboard-тан алыңыз", 
                                     font=self.font_small, bg=self.bg_color, fg="#666", anchor="w")
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, ipady=5)

        # Идеяларды қосу (қосымша функциялар)
        self.add_ideas()

    def add_ideas(self):
        """💡 ЕКІ ИДЕЯНЫ ҚОСУ: 1) Синоним ауыстыру 2) Тіл аудару (қаз→орыс→қаз)"""
        idea_frame = tk.Frame(self.root, bg=self.bg_color)
        idea_frame.pack(pady=10)

        self.use_synonyms = tk.BooleanVar(value=True)
        self.use_translate_trick = tk.BooleanVar(value=False)

        tk.Checkbutton(idea_frame, text="💡 Синонимдер арқылы адам стиліне айналдыру", 
                       variable=self.use_synonyms, font=self.font_small, bg=self.bg_color).pack(side=tk.LEFT, padx=10)

        tk.Checkbutton(idea_frame, text="🌍 Тіл аудару әдісі (қаз→орыс→қаз — стилді өзгертеді)", 
                       variable=self.use_translate_trick, font=self.font_small, bg=self.bg_color).pack(side=tk.LEFT, padx=10)

    def load_from_clipboard(self):
        try:
            text = pyperclip.paste()
            if text.strip():
                self.input_text.delete(1.0, tk.END)
                self.input_text.insert(tk.END, text)
                self.status_label.config(text="📋 Clipboard-тан мәтін енгізілді", fg="#007bff")
            else:
                messagebox.showwarning("Ескерту", "Clipboard бос!")
        except Exception as e:
            messagebox.showerror("Қате", f"Clipboard-тан алу сәтсіз: {e}")

    def start_cleaning(self):
        thread = threading.Thread(target=self.clean_text)
        thread.start()

    def clean_text(self):
        text = self.input_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showerror("Қате", "Мәтін енгізіңіз!")
            return

        self.progress["value"] = 0
        self.status_label.config(text="⏳ Тазалау басталды...", fg="#007bff")
        self.root.update()

        # 1. Көрінбейтін таңбаларды өшіру
        cleaned = clean_hidden_chars(text)
        self.progress["value"] = 30

        # 2. Егер таңдалса — синонимдер арқылы адам стиліне айналдыру
        if self.use_synonyms.get():
            self.status_label.config(text="🧠 Синонимдер қолданылуда...", fg="#ffc107")
            self.root.update()
            cleaned = humanize_text(cleaned)
        self.progress["value"] = 70

        # 3. Егер таңдалса — тіл аудару әдісі (қаз→орыс→қаз) — стилді бұзады
        # (Бұл әзірге макет — нақты тіл аудару үшін googletrans немесе басқа кітапхана қажет)
        if self.use_translate_trick.get():
            self.status_label.config(text="🌍 Тіл аудару әдісі қолданылуда (қаз→орыс→қаз)...", fg="#dc3545")
            self.root.update()
            # Мысал ретінде — бірнеше сөзді ауыстырамыз (нақты тіл аудару үшін кеңейтуге болады)
            translate_trick = {
                "мәтін": "текст",
                "тазалау": "очистка",
                "жасау": "создание",
                "нәтиже": "результат",
                "функция": "функция",
                "қолдану": "использование"
            }
            for kaz, rus in translate_trick.items():
                cleaned = cleaned.replace(kaz, rus)
            for rus, kaz in translate_trick.items():
                cleaned = cleaned.replace(rus, kaz)
        self.progress["value"] = 100

        # Нәтижені шығару
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, cleaned)

        self.status_label.config(text="✅ Тазалау аяқталды! Нәтижені clipboard-қа көшіріңіз", fg="green")

    def copy_to_clipboard(self):
        result = self.output_text.get(1.0, tk.END).strip()
        if result:
            pyperclip.copy(result)
            self.status_label.config(text="📋 Нәтиже clipboard-қа көшірілді!", fg="#28a745")
        else:
            messagebox.showwarning("Ескерту", "Нәтиже бос!")


    def clear_all(self):
        self.input_text.delete(1.0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.progress["value"] = 0
        self.status_label.config(text="✅ Барлығы тазартылды", fg="#666")

def translate_trick(text):
    # Қазақ → Орыс
    translated = GoogleTranslator(source='kk', target='ru').translate(text)
    # Орыс → Қазақ
    back_translated = GoogleTranslator(source='ru', target='kk').translate(translated)
    return back_translated

# Негізгі программа
if __name__ == "__main__":
    root = tk.Tk()
    app = AntiPlagiarismCleanerApp(root)
    root.mainloop()