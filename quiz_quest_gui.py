import tkinter as tk
from tkinter import messagebox

def start_game():
    selected_char = character_var.get()
    if selected_char == "":
        messagebox.showwarning("Warning", "Please select a character before starting!")
    else:
        messagebox.showinfo("Quiz Quest", f"Welcome {selected_char}! The visual game will start soon...")

root = tk.Tk()
root.title("Quiz Quest GUI Version")
root.geometry("400x350")

title_label = tk.Label(root, text="Welcome to Quiz Quest", font=("Helvetica", 16, "bold"))
title_label.pack(pady=10)

character_var = tk.StringVar(value="")

char_label = tk.Label(root, text="Choose your character:", font=("Helvetica", 12))
char_label.pack(pady=5)

chars = [("Warrior", "Warrior"), ("Mage", "Mage"), ("Archer", "Archer")]
for text, value in chars:
    rb = tk.Radiobutton(root, text=text, variable=character_var, value=value, font=("Helvetica", 12))
    rb.pack(anchor="w")

start_button = tk.Button(root, text="Start Game", font=("Helvetica", 14), command=start_game)
start_button.pack(pady=20)

root.mainloop()
