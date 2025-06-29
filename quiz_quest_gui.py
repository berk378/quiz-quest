import tkinter as tk
from tkinter import messagebox
import json
import threading
import time
import random

player_name = ""

# Kategoriler ve zorluklar
categories = ["Math", "Geography", "General Knowledge", "Coding"]
difficulties = ["Easy", "Medium", "Hard", "Extreme"]

def start_game():
    selected_char = character_var.get()
    selected_category = category_var.get()
    selected_difficulty = difficulty_var.get()

    if not selected_char or not selected_category or not selected_difficulty:
        messagebox.showwarning("Warning", "Please select character, category, and difficulty!")
        return

    questions = load_questions(selected_category, selected_difficulty)
    if not questions:
        messagebox.showerror("Error", "No questions found.")
        return

    show_question_window(questions, selected_char, selected_category, selected_difficulty)

def continue_to_category():
    global player_name
    selected_char = character_var.get()
    if is_anonymous.get():
        player_name = "Anonymous Player"
    else:
        player_name = name_entry.get().strip()
        if not player_name:
            messagebox.showwarning("Warning", "Please enter your name!")
            return
    if not selected_char:
        messagebox.showwarning("Warning", "Please select a character!")
        return

    character_frame.pack_forget()
    show_category_selection()

def show_category_selection():
    category_label.pack(pady=5)
    for rb in category_buttons:
        rb.pack(anchor="w")
    difficulty_label.pack(pady=5)
    for rb in difficulty_buttons:
        rb.pack(anchor="w")
    start_button.pack(pady=20)

def load_questions(category, difficulty):
    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            all_questions = json.load(f)
            questions = all_questions.get(category, {}).get(difficulty, [])
            random.shuffle(questions)
            return questions
    except:
        return []

def write_score_to_file(name, score, category, difficulty):
    # Anonim ise skor kaydetme
    if name == "Anonymous Player":
        return
    score_data = {
        "name": name,
        "score": score,
        "category": category,
        "difficulty": difficulty
    }
    try:
        with open("scores.json", "r", encoding="utf-8") as f:
            scores = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        scores = []

    # Aynı kategori ve zorluk için skorları bul ve ekle
    filtered = [s for s in scores if s["category"] == category and s["difficulty"] == difficulty]
    filtered.append(score_data)
    filtered.sort(key=lambda x: x["score"], reverse=True)
    filtered = filtered[:10]  # Sadece ilk 10

    # Diğer skorları koru
    scores = [s for s in scores if not (s["category"] == category and s["difficulty"] == difficulty)]
    scores.extend(filtered)

    with open("scores.json", "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=4)

def show_question_window(questions, character, category, difficulty):
    game_window = tk.Toplevel(root)
    game_window.title("Quiz Time!")
    game_window.geometry("550x500")

    score = tk.IntVar(value=0)
    health = tk.IntVar(value=3)
    question_index = tk.IntVar(value=0)
    selected_answer = tk.StringVar()
    
    def get_timer_duration(category, difficulty):
        timer_settings = {
            "Math": {"Easy": 5, "Medium": 8, "Hard": 10, "Extreme": 15},
            "General Knowledge": {"Easy": 5, "Medium": 8, "Hard": 10, "Extreme": 15},
            "Coding": {"Easy": 5, "Medium": 8, "Hard": 10, "Extreme": 15},
            "Geography": {"Easy": 5, "Medium": 8, "Hard": 10, "Extreme": 15}
        }
        return timer_settings.get(category, {}).get(difficulty, 15)
    
    timer_duration = get_timer_duration(category, difficulty)
    timer = tk.IntVar(value=timer_duration)

    hearts_label = tk.Label(game_window, font=("Helvetica", 16))
    countdown_label = tk.Label(game_window, font=("Helvetica", 14))

    def update_hearts():
        hearts_label.config(text="❤️" * health.get())
        if health.get() <= 0:
            write_score_to_file(player_name, score.get(), category, difficulty)
            messagebox.showinfo("Game Over", f"Nice try {character}!\nFinal Score: {score.get()}")
            game_window.destroy()

    def countdown():
        for t in range(timer_duration, 0, -1):
            timer.set(t)
            warning_threshold = max(1, timer_duration // 4)
            countdown_label.config(text=f" Time left: {t}s", fg="red" if t <= warning_threshold else "black")
            time.sleep(1)
            if selected_answer.get():
                break
        else:
            health.set(health.get() - 1)
            update_hearts()
            question_index.set(question_index.get() + 1)
            display_question()

    def display_question():
        selected_answer.set("")
        if question_index.get() >= len(questions):
            write_score_to_file(player_name, score.get(), category, difficulty)
            messagebox.showinfo("Well Done!", f"You finished the game, {character}!\nFinal Score: {score.get()}")
            game_window.destroy()
            return

        q = questions[question_index.get()]
        question_label.config(text=q["question"])
        options = q["options"].copy()
        random.shuffle(options)
        for i in range(4):
            option_buttons[i].config(text=options[i], value=options[i][0])
        update_hearts()
        timer.set(timer_duration)  
        threading.Thread(target=countdown, daemon=True).start()

    def submit_answer():
        if not selected_answer.get():
            return
        correct = questions[question_index.get()]["answer"]
        if selected_answer.get() == correct:
            score.set(score.get() + 1)
        else:
            health.set(health.get() - 1)
        question_index.set(question_index.get() + 1)
        display_question()

    # Apply theme to game window
    if is_dark_mode.get():
        game_window.configure(bg="#1d1c1c")
        question_label = tk.Label(game_window, text="", wraplength=500, font=("Helvetica", 14), bg="#2e2e2e", fg="white")
        countdown_label.configure(bg="#2e2e2e", fg="white")
        hearts_label.configure(bg="#2e2e2e", fg="white")
    else:
        game_window.configure(bg="SystemButtonFace")
        question_label = tk.Label(game_window, text="", wraplength=500, font=("Helvetica", 14), bg="SystemButtonFace", fg="black")
        countdown_label.configure(bg="SystemButtonFace", fg="black")
        hearts_label.configure(bg="SystemButtonFace", fg="black")

    question_label.pack(pady=20)

    option_buttons = []
    for _ in range(4):
        if is_dark_mode.get():
            btn = tk.Radiobutton(game_window, text="", variable=selected_answer, font=("Helvetica", 12), 
                               bg="#2e2e2e", fg="white", selectcolor="#404040")
        else:
            btn = tk.Radiobutton(game_window, text="", variable=selected_answer, font=("Helvetica", 12),
                               bg="SystemButtonFace", fg="black", selectcolor="white")
        btn.pack(anchor="w", padx=20)
        option_buttons.append(btn)

    if is_dark_mode.get():
        submit_btn = tk.Button(game_window, text="Submit", font=("Helvetica", 12), command=submit_answer,
                             bg="#404040", fg="white")
    else:
        submit_btn = tk.Button(game_window, text="Submit", font=("Helvetica", 12), command=submit_answer,
                             bg="SystemButtonFace", fg="black")
    submit_btn.pack(pady=10)

    countdown_label.pack()
    hearts_label.pack()

    display_question()

# --- SKOR TABLOSU FONKSİYONU (SEKMELİ, İLK 10 SKOR) ---
def show_scoreboard():
    import tkinter.ttk as ttk

    try:
        with open("scores.json", "r", encoding="utf-8") as f:
            scores = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        scores = []

    sb = tk.Toplevel(root)
    sb.title("Skor Tablosu")
    sb.geometry("700x500")
    sb.resizable(False, False)

    notebook = ttk.Notebook(sb)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    for cat in categories:
        frame = tk.Frame(notebook)
        notebook.add(frame, text=cat)
        for diff in difficulties:
            label = tk.Label(frame, text=f"{diff} - En İyi 10 Skor", font=("Helvetica", 11, "bold"))
            label.pack(pady=(10, 0))
            tree = ttk.Treeview(frame, columns=("rank", "name", "score"), show="headings", height=10)
            tree.heading("rank", text="#")
            tree.heading("name", text="İsim")
            tree.heading("score", text="Skor")
            tree.column("rank", width=30, anchor="center")
            tree.column("name", width=180, anchor="center")
            tree.column("score", width=60, anchor="center")
            tree.pack(pady=2)

            # İlgili skorları filtrele ve sırala
            filtered = [s for s in scores if s["category"] == cat and s["difficulty"] == diff]
            filtered.sort(key=lambda x: x["score"], reverse=True)
            for idx, s in enumerate(filtered[:10], start=1):
                display_name = "Anonim" if s["name"] == "Anonymous Player" else s["name"]
                tree.insert("", "end", values=(idx, display_name, s["score"]))
            if not filtered:
                tree.insert("", "end", values=("", "-", "-"))

# Tema fonksiyonları
def toggle_theme():
    if is_dark_mode.get():
        apply_light_theme()
        is_dark_mode.set(False)
        theme_button.config(text="Dark Mode")
    else:
        apply_dark_theme()
        is_dark_mode.set(True)
        theme_button.config(text="Light Mode")

def apply_dark_theme():
    root.configure(bg="#2e2e2e")
    widgets = [title_label, name_label, char_label, continue_button,
               category_label, difficulty_label, start_button, theme_button, anonymous_check, scoreboard_button]
    for widget in widgets:
        try:
            if isinstance(widget, tk.Button):
                widget.configure(bg="#404040", fg="white")
            else:
                widget.configure(bg="#2e2e2e", fg="white")
        except:
            pass
    try:
        name_entry.configure(bg="#404040", fg="white", insertbackground="white")
    except:
        pass
    character_frame.configure(bg="#2e2e2e")
    for child in character_frame.winfo_children():
        if isinstance(child, tk.Radiobutton):
            try:
                child.configure(bg="#2e2e2e", fg="white", selectcolor="#404040")
            except:
                pass
    all_radiobuttons = category_buttons + difficulty_buttons
    for rb in all_radiobuttons:
        try:
            rb.configure(bg="#2e2e2e", fg="white", selectcolor="#404040")
        except:
            pass

def apply_light_theme():
    root.configure(bg="SystemButtonFace")
    widgets = [title_label, name_label, char_label, continue_button,
               category_label, difficulty_label, start_button, theme_button, anonymous_check, scoreboard_button]
    for widget in widgets:
        try:
            if isinstance(widget, tk.Button):
                widget.configure(bg="SystemButtonFace", fg="black")
            else:
                widget.configure(bg="SystemButtonFace", fg="black")
        except:
            pass
    try:
        name_entry.configure(bg="white", fg="black", insertbackground="black")
    except:
        pass
    character_frame.configure(bg="SystemButtonFace")
    for child in character_frame.winfo_children():
        if isinstance(child, tk.Radiobutton):
            try:
                child.configure(bg="SystemButtonFace", fg="black", selectcolor="white")
            except:
                pass
    all_radiobuttons = category_buttons + difficulty_buttons
    for rb in all_radiobuttons:
        try:
            rb.configure(bg="SystemButtonFace", fg="black", selectcolor="white")
        except:
            pass

root = tk.Tk()
root.title("Quiz Quest GUI")
root.geometry("400x550")

is_dark_mode = tk.BooleanVar(value=False)
is_anonymous = tk.BooleanVar(value=False)

theme_button = tk.Button(root, text="🌙 Dark Mode", command=toggle_theme, font=("Helvetica", 10))
theme_button.pack(pady=5)

scoreboard_button = tk.Button(root, text="Skor Tablosu", font=("Helvetica", 10), command=show_scoreboard)
scoreboard_button.pack(pady=5)

title_label = tk.Label(root, text="Welcome to Quiz Quest", font=("Helvetica", 16, "bold"))
title_label.pack(pady=10)

character_var = tk.StringVar(value="")
character_frame = tk.Frame(root)
character_frame.pack()

name_label = tk.Label(character_frame, text="Enter your name:", font=("Helvetica", 12))
name_label.pack(pady=5)
name_entry = tk.Entry(character_frame, font=("Helvetica", 12))
name_entry.pack()

def toggle_anonymous():
    if is_anonymous.get():
        name_entry.config(state="disabled")
        name_entry.delete(0, tk.END)
        name_entry.insert(0, "Anonymous Player")
    else:
        name_entry.config(state="normal")
        name_entry.delete(0, tk.END)

anonymous_check = tk.Checkbutton(character_frame, text="Play Anonymously", 
                                variable=is_anonymous, font=("Helvetica", 12),
                                command=toggle_anonymous)
anonymous_check.pack(pady=5)

char_label = tk.Label(character_frame, text="Choose your character:", font=("Helvetica", 12))
char_label.pack(pady=5)

chars = [("Warrior", "Warrior"), ("Mage", "Mage"), ("Archer", "Archer")]
for text, value in chars:
    rb = tk.Radiobutton(character_frame, text=text, variable=character_var, value=value, font=("Helvetica", 12))
    rb.pack(anchor="w")

continue_button = tk.Button(character_frame, text="Continue", font=("Helvetica", 14), command=continue_to_category)
continue_button.pack(pady=15)

category_var = tk.StringVar()
difficulty_var = tk.StringVar()

category_label = tk.Label(root, text="Select Category:", font=("Helvetica", 12))
category_buttons = [tk.Radiobutton(root, text=cat, variable=category_var, value=cat, font=("Helvetica", 12)) for cat in categories]

difficulty_label = tk.Label(root, text="Select Difficulty:", font=("Helvetica", 12))
difficulty_buttons = [tk.Radiobutton(root, text=diff, variable=difficulty_var, value=diff, font=("Helvetica", 12)) for diff in difficulties]

start_button = tk.Button(root, text="Start Game", font=("Helvetica", 14), command=start_game)

root.mainloop()