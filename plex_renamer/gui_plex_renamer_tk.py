import threading
from tkinter import (Tk, Button, Checkbutton, IntVar, Text, END,
                     filedialog, Label, Entry, Scrollbar, RIGHT,
                     Y, LEFT, BOTH, Frame)
from pathlib import Path
from plex_renamer.core import run_renamer  # Импортируем функцию из core.py


def append_log(msg):
    """Вывод лог-сообщения в Text"""
    log_text.config(state='normal')
    log_text.insert(END, msg + '\n')
    log_text.see(END)
    log_text.config(state='disabled')


def choose_path():
    """Диалог выбора файла или папки"""
    selected_file = filedialog.askopenfilename(
        title="Выберите файл")  # сначала файл
    if selected_file:
        path_var.set(selected_file)
        return
    selected_dir = filedialog.askdirectory(
        title="Выберите папку")  # если файл не выбран, каталог
    if selected_dir:
        path_var.set(selected_dir)


def start_renamer():
    """Запуск переименования в отдельном потоке"""
    path = path_var.get()
    if not path:
        append_log("❌ Укажите путь до файла или папки!")
        return
    apply_flag = apply_var.get()

    def worker():
        run_renamer(path, apply=bool(apply_flag), callback=append_log)
        append_log("--- ✅ Готово ---")
        start_btn.config(state='normal')

    start_btn.config(state='disabled')
    threading.Thread(target=worker, daemon=True).start()


# --- Создание окна ---
root = Tk()
root.title("Plex Renamer")

# Путь
path_frame = Frame(root)
Label(path_frame, text="Файл или папка:").pack(side=LEFT)
path_var = ""
path_entry = Entry(path_frame, width=60, textvariable=path_var)
path_entry.pack(side=LEFT, padx=5)
Button(path_frame, text="Обзор", command=choose_path).pack(side=LEFT)
path_frame.pack(pady=5)

# Опция apply
apply_var = IntVar()
Checkbutton(root, text="Применить изменения (--apply)",
            variable=apply_var).pack()

# Кнопка запуска
start_btn = Button(root, text="Запустить", command=start_renamer)
start_btn.pack(pady=5)

# Лог с прокруткой
log_frame = Frame(root)
scrollbar = Scrollbar(log_frame)
scrollbar.pack(side=RIGHT, fill=Y)
log_text = Text(log_frame, width=80, height=20, yscrollcommand=scrollbar.set,
                state='disabled')
log_text.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.config(command=log_text.yview)
log_frame.pack(padx=5, pady=5, fill=BOTH, expand=True)

# --- Запуск GUI ---
root.mainloop()
