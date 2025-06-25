import tkinter as tk
from tkinter import messagebox
import json
import threading
import time

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

    show_question_window(questions, selected_char)

def continue_to_category():
    selected_char = character_var.get()
    if not selected_char:
        messagebox.showwarning("Warning", "Please select a character!")
    else:
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
            return all_questions.get(category, {}).get(difficulty, [])
    except:
        return []

def show_question_window(questions, character):
    game_window = tk.Toplevel(root)
    game_window.title("Quiz Time!")
    game_window.geometry("550x500")

    score = tk.IntVar(value=0)
    health = tk.IntVar(value=3)
    question_index = tk.IntVar(value=0)
    selected_answer = tk.StringVar()
    timer = tk.IntVar(value=15)
    hearts_label = tk.Label(game_window, font=("Helvetica", 16))
    countdown_label = tk.Label(game_window, font=("Helvetica", 14))

    def update_hearts():
        hearts_label.config(text="❤️" * health.get())
        if health.get() <= 0:
            messagebox.showinfo("Game Over", f"Nice try {character}!\nFinal Score: {score.get()}")
            game_window.destroy()

    def countdown():
        for t in range(15, 0, -1):
            timer.set(t)
            countdown_label.config(text=f"⏳ Time left: {t}s", fg="red" if t <= 5 else "black")
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
            messagebox.showinfo("Well Done!", f"You finished the game, {character}!\nFinal Score: {score.get()}")
            game_window.destroy()
            return

        q = questions[question_index.get()]
        question_label.config(text=q["question"])
        for i in range(4):
            option_buttons[i].config(text=q["options"][i], value=q["options"][i][0])
        update_hearts()
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

    question_label = tk.Label(game_window, text="", wraplength=500, font=("Helvetica", 14))
    question_label.pack(pady=20)

    option_buttons = []
    for _ in range(4):
        btn = tk.Radiobutton(game_window, text="", variable=selected_answer, font=("Helvetica", 12))
        btn.pack(anchor="w", padx=20)
        option_buttons.append(btn)

    submit_btn = tk.Button(game_window, text="Submit", font=("Helvetica", 12), command=submit_answer)
    submit_btn.pack(pady=10)

    countdown_label.pack()
    hearts_label.pack()

    display_question()

root = tk.Tk()
root.title("Quiz Quest GUI")
root.geometry("400x500")

title_label = tk.Label(root, text="Welcome to Quiz Quest", font=("Helvetica", 16, "bold"))
title_label.pack(pady=10)

character_var = tk.StringVar(value="")
character_frame = tk.Frame(root)
character_frame.pack()

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
categories = ["Math", "Geography", "General Knowledge", "Coding", "History"]
category_buttons = [tk.Radiobutton(root, text=cat, variable=category_var, value=cat, font=("Helvetica", 12)) for cat in categories]

difficulty_label = tk.Label(root, text="Select Difficulty:", font=("Helvetica", 12))
difficulties = ["Easy", "Medium", "Hard", "Extreme"]
difficulty_buttons = [tk.Radiobutton(root, text=diff, variable=difficulty_var, value=diff, font=("Helvetica", 12)) for diff in difficulties]

start_button = tk.Button(root, text="Start Game", font=("Helvetica", 14), command=start_game)

root.mainloop()
