import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import threading
import time
import random

player_name = ""

categories = ["Math", "Geography", "General Knowledge", "Coding", "Mixed"]
difficulties = ["Easy", "Medium", "Hard", "Extreme", "Mixed"]

def start_game():
    selected_char = character_var.get()
    selected_category = category_var.get()
    selected_difficulty = difficulty_var.get()

    if not selected_char:
        messagebox.showwarning("Warning", "Please select a character!")
        return

    if mixed_mode_active.get():
        selected_category = random.choice(categories[:-1])
        selected_difficulty = random.choice(difficulties)
        category_var.set(selected_category)
        difficulty_var.set(selected_difficulty)

    if not selected_category or not selected_difficulty:
        messagebox.showwarning("Warning", "Please select category and difficulty!")
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

def spin_random_selection():
    spin_time = 1000
    interval = 50
    elapsed = [0]

    def spin():
        cat = random.choice(categories)
        diff = random.choice(difficulties)
        category_var.set(cat)
        difficulty_var.set(diff)
        elapsed[0] += interval
        if elapsed[0] < spin_time:
            root.after(interval, spin)
    spin()

def show_category_selection():
    category_label.pack(pady=5)
    button_frame.pack(pady=5)
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
            if category == "Mixed":
                questions = []
                for cat in all_questions:
                    questions += all_questions[cat].get(difficulty, [])
                random.shuffle(questions)
                return questions
            else:
                questions = all_questions.get(category, {}).get(difficulty, [])
                random.shuffle(questions)
                return questions
    except:
        return []

def write_score_to_file(name, score, category, difficulty):
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

    filtered = [s for s in scores if s["category"] == category and s["difficulty"] == difficulty]
    filtered.append(score_data)
    filtered.sort(key=lambda x: x["score"], reverse=True)
    filtered = filtered[:10]

    scores = [s for s in scores if not (s["category"] == category and s["difficulty"] == difficulty)]
    scores.extend(filtered)

    with open("scores.json", "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=4)

def show_results_window(answer_list):
    results_win = tk.Toplevel(root)
    results_win.title("Results")
    results_win.geometry("400x550")

    tk.Label(results_win, text="Answered Questions", font=("Helvetica", 14, "bold")).pack(pady=10)

    list_frame = tk.Frame(results_win)
    list_frame.pack(fill="both", expand=True)

    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")

    results_listbox = tk.Listbox(list_frame, font=("Helvetica", 12), yscrollcommand=scrollbar.set)
    results_listbox.pack(fill="both", expand=True)
    scrollbar.config(command=results_listbox.yview)

    detail_frame = tk.Frame(results_win)
    detail_frame.pack(fill="x", padx=10, pady=10)

    detail_question = tk.Label(detail_frame, text="", wraplength=350, font=("Helvetica", 12, "bold"))
    detail_question.pack(pady=5)
    detail_options = []
    for _ in range(4):
        lbl = tk.Label(detail_frame, text="", wraplength=350, font=("Helvetica", 11))
        lbl.pack(anchor="w", padx=20)
        detail_options.append(lbl)
    detail_explanation = tk.Label(
        detail_frame,
        text="",
        wraplength=350,
        font=("Helvetica", 13, "bold"),
        fg="#2e2e2e",
        bg="#f0f0f0",
        justify="center"
    )
    detail_explanation.pack(pady=15, fill="x")

    for idx, ans in enumerate(answer_list, 1):
        status = "✅" if ans["is_correct"] else "❌"
        results_listbox.insert("end", f"Question {idx} {status}")

    def on_select(event):
        selection = results_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        ans = answer_list[idx]
        q = ans["question"]

        detail_question.config(text=q["question"])
        for i, opt in enumerate(q["options"]):
            opt_text = opt
            if opt[0] == q["answer"]:
                opt_text += " (Correct Answer)"
            if opt[0] == ans["selected"]:
                opt_text += " (Your Answer)"
            detail_options[i].config(text=opt_text)
        for i in range(len(q["options"]), 4):
            detail_options[i].config(text="")
        explanation = q.get("explanation", "No explanation available.")
        detail_explanation.config(text=f"Explanation: {explanation}")

    results_listbox.bind("<<ListboxSelect>>", on_select)

def show_question_window(questions, character, category, difficulty):
    game_window = tk.Toplevel(root)
    game_window.title("Quiz Time!")
    game_window.geometry("550x500")

    score = tk.IntVar(value=0)
    health = tk.IntVar(value=3)
    question_index = tk.IntVar(value=0)
    selected_answer = tk.StringVar()
    answer_list = []

    # Karakter özellikleri için flagler
    warrior_shield_used = [False]  # Warrior için bir kez can koruma
    archer_retry_used = [False]    # Archer için bir kez tekrar hakkı (her soru için sıfırlanır)

    def get_timer_duration(category, difficulty):
        timer_settings = {
            "Math": {"Easy": 5, "Medium": 8, "Hard": 10, "Extreme": 15},
            "General Knowledge": {"Easy": 5, "Medium": 8, "Hard": 10, "Extreme": 15},
            "Coding": {"Easy": 5, "Medium": 8, "Hard": 10, "Extreme": 15},
            "Geography": {"Easy": 5, "Medium": 8, "Hard": 10, "Extreme": 15}
        }
        if category == "Mixed":
            return 10
        return timer_settings.get(category, {}).get(difficulty, 15)

    # Mage için süreye +2 ekle
    base_timer_duration = get_timer_duration(category, difficulty)
    def get_character_timer():
        if character == "Mage":
            return base_timer_duration + 2
        return base_timer_duration

    timer = tk.IntVar(value=get_character_timer())

    hearts_label = tk.Label(game_window, font=("Helvetica", 16))
    countdown_label = tk.Label(game_window, font=("Helvetica", 14))

    def update_hearts():
        hearts_label.config(text="❤️" * health.get())
        if health.get() <= 0:
            write_score_to_file(player_name, score.get(), category, difficulty)
            show_results_window(answer_list)
            messagebox.showinfo("Game Over", f"Nice try {character}!\nFinal Score: {score.get()}")
            game_window.destroy()

    def countdown():
        timer_duration = get_character_timer()
        for t in range(timer_duration, 0, -1):
            timer.set(t)
            warning_threshold = max(1, timer_duration // 4)
            countdown_label.config(text=f" Time left: {t}s", fg="red" if t <= warning_threshold else "black")
            time.sleep(1)
            if selected_answer.get():
                break
        else:
            # Süre bitti, yanlış say
            handle_wrong_answer(timeout=True)

    def display_question():
        selected_answer.set("")
        archer_retry_used[0] = False  # Archer için tekrar hakkı sıfırlanır
        if question_index.get() >= len(questions):
            write_score_to_file(player_name, score.get(), category, difficulty)
            show_results_window(answer_list)
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
        timer.set(get_character_timer())
        threading.Thread(target=countdown, daemon=True).start()

    def handle_wrong_answer(timeout=False):
        q = questions[question_index.get()]
        # Warrior: İlk yanlışta can kaybetmez, ama soru atlanır
        if character == "Warrior" and not warrior_shield_used[0]:
            warrior_shield_used[0] = True
            answer_list.append({
                "question": q,
                "selected": selected_answer.get() if selected_answer.get() else "",
                "is_correct": False
            })
            messagebox.showinfo("Warrior Shield", "Warrior özelliği ile bu seferlik can kaybetmedin!")
            question_index.set(question_index.get() + 1)
            display_question()
            return
        # Archer: Yanlışta bir kez tekrar hakkı
        if character == "Archer" and not archer_retry_used[0]:
            archer_retry_used[0] = True
            messagebox.showinfo("Archer Retry", "Archer özelliği ile bu soruyu tekrar deneyebilirsin!")
            return  # Aynı soruda tekrar şans ver
        # Normal yanlış
        health.set(health.get() - 1)
        answer_list.append({
            "question": q,
            "selected": selected_answer.get() if selected_answer.get() else "",
            "is_correct": False
        })
        question_index.set(question_index.get() + 1)
        display_question()

    def submit_answer():
        if not selected_answer.get():
            return
        correct = questions[question_index.get()]["answer"]
        is_correct = selected_answer.get() == correct
        if is_correct:
            answer_list.append({
                "question": questions[question_index.get()],
                "selected": selected_answer.get(),
                "is_correct": True
            })
            score.set(score.get() + 1)
            question_index.set(question_index.get() + 1)
            display_question()
        else:
            handle_wrong_answer(timeout=False)

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

def show_scoreboard():
    import tkinter.ttk as ttk

    try:
        with open("scores.json", "r", encoding="utf-8") as f:
            scores = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        scores = []

    sb = tk.Toplevel(root)
    sb.title("Scoreboard")
    sb.geometry("1100x600")
    sb.resizable(True, True)

    notebook = ttk.Notebook(sb)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Category tabs, each with all difficulties as columns
    for cat in categories:
        if cat == "Mixed":
            continue  # Skip Mixed for scoreboard
        frame = tk.Frame(notebook)
        notebook.add(frame, text=cat)

        # Table with all difficulties as columns
        columns = ["rank"]
        columns += [f"{diff}_name" for diff in difficulties[:-1]]
        columns += [f"{diff}_score" for diff in difficulties[:-1]]

        tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        tree.heading("rank", text="#")
        for diff in difficulties[:-1]:
            tree.heading(f"{diff}_name", text=f"{diff} Name")
            tree.heading(f"{diff}_score", text=f"{diff} Score")
            tree.column(f"{diff}_name", width=120, anchor="center")
            tree.column(f"{diff}_score", width=80, anchor="center")
        tree.column("rank", width=30, anchor="center")
        tree.pack(fill="both", expand=True, side="left")

        # Add horizontal scrollbar
        xscroll = tk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=xscroll.set)
        xscroll.pack(side="bottom", fill="x")

        # Prepare top 10 for each difficulty
        tops = {}
        max_len = 0
        for diff in difficulties[:-1]:
            filtered = [s for s in scores if s["category"] == cat and s["difficulty"] == diff]
            filtered.sort(key=lambda x: x["score"], reverse=True)
            tops[diff] = filtered[:10]
            max_len = max(max_len, len(tops[diff]))
        # Fill rows
        for idx in range(max_len):
            row = [str(idx + 1)]
            for diff in difficulties[:-1]:
                if idx < len(tops[diff]):
                    s = tops[diff][idx]
                    display_name = "Anonymous" if s["name"] == "Anonymous Player" else str(s["name"])
                    row.append(display_name)
                    row.append(str(s["score"]))
                else:
                    row.append("-")
                    row.append("-")
            tree.insert("", "end", values=row)

    # History tab (all scores, all categories/difficulties, sorted by date if possible)
    history_frame = tk.Frame(notebook)
    notebook.add(history_frame, text="History")
    label = tk.Label(history_frame, text="All Scores", font=("Helvetica", 12, "bold"))
    label.pack(pady=(10, 0))
    tree = ttk.Treeview(history_frame, columns=("name", "category", "difficulty", "score"), show="headings", height=20)
    tree.heading("name", text="Name")
    tree.heading("category", text="Category")
    tree.heading("difficulty", text="Difficulty")
    tree.heading("score", text="Score")
    tree.column("name", width=180, anchor="center")
    tree.column("category", width=120, anchor="center")
    tree.column("difficulty", width=100, anchor="center")
    tree.column("score", width=60, anchor="center")
    tree.pack(pady=2, fill="both", expand=True)

    # Add vertical scrollbar for history
    yscroll = tk.Scrollbar(history_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=yscroll.set)
    yscroll.pack(side="right", fill="y")

    # Show all scores (most recent last)
    for s in scores:
        display_name = "Anonymous" if s["name"] == "Anonymous Player" else str(s["name"])
        tree.insert("", "end", values=(display_name, s["category"], s["difficulty"], str(s["score"])))

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

# --- Start 60 Seconds Challenge Mode ---
def show_60s_challenge_window(questions, character, category, difficulty):
    challenge_win = tk.Toplevel(root)
    challenge_win.title("60 Seconds Challenge")
    challenge_win.geometry("550x500")

    score = tk.IntVar(value=0)
    time_left = tk.IntVar(value=60)
    q_index = tk.IntVar(value=0)
    selected_answer = tk.StringVar()
    answer_list = []
    health = tk.IntVar(value=3)

    time_bonus = {"Easy": 2, "Medium": 3, "Hard": 4, "Extreme": 5}

    def update_hearts():
        hearts_label.config(text="❤️" * health.get())
        if health.get() <= 0:
            write_score_to_file(player_name, score.get(), category, difficulty)
            show_results_window(answer_list)
            messagebox.showinfo("Game Over", f"Out of lives!\nScore: {score.get()}")
            challenge_win.destroy()

    def next_question():
        selected_answer.set("")
        if q_index.get() >= len(questions) or time_left.get() <= 0 or health.get() <= 0:
            write_score_to_file(player_name, score.get(), category, difficulty)
            show_results_window(answer_list)
            messagebox.showinfo("Challenge Over", f"Score: {score.get()}")
            challenge_win.destroy()
            return
        q = questions[q_index.get()]
        question_label.config(text=q["question"])
        opts = q["options"].copy()
        random.shuffle(opts)
        for i in range(4):
            option_buttons[i].config(text=opts[i], value=opts[i][0])
        timer_label.config(text=f"Time Left: {time_left.get()} s")
        update_hearts()

    def submit():
        if not selected_answer.get():
            return
        q = questions[q_index.get()]
        is_correct = selected_answer.get() == q["answer"]
        answer_list.append({
            "question": q,
            "selected": selected_answer.get(),
            "is_correct": is_correct
        })
        if is_correct:
            score.set(score.get() + 1)
            diff = difficulty
            for d in difficulties:
                if d.lower() in q["question"].lower() or d.lower() in category.lower():
                    diff = d
            bonus = time_bonus.get(diff, 2)
            time_left.set(time_left.get() + bonus)
        else:
            health.set(health.get() - 1)
        q_index.set(q_index.get() + 1)
        next_question()

    def timer_countdown():
        while time_left.get() > 0 and health.get() > 0:
            time.sleep(1)
            time_left.set(time_left.get() - 1)
            timer_label.config(text=f"Time Left: {time_left.get()} s")
            if time_left.get() <= 0 or health.get() <= 0:
                submit_btn.config(state="disabled")
                break

    question_label = tk.Label(challenge_win, text="", wraplength=500, font=("Helvetica", 14))
    question_label.pack(pady=20)
    option_buttons = []
    for _ in range(4):
        btn = tk.Radiobutton(challenge_win, text="", variable=selected_answer, font=("Helvetica", 12))
        btn.pack(anchor="w", padx=20)
        option_buttons.append(btn)
    submit_btn = tk.Button(challenge_win, text="Submit", font=("Helvetica", 12), command=submit)
    submit_btn.pack(pady=10)
    timer_label = tk.Label(challenge_win, text="Time Left: 60 s", font=("Helvetica", 14))
    timer_label.pack()
    hearts_label = tk.Label(challenge_win, text="❤️❤️❤️", font=("Helvetica", 16))
    hearts_label.pack(pady=5)

    next_question()
    threading.Thread(target=timer_countdown, daemon=True).start()
# --- End 60 Seconds Challenge Mode ---

# --- 1v1 Mode Integration ---
def ask_player_name(title, prompt):
    win = tk.Toplevel(root)
    win.title(title)
    win.grab_set()
    win.focus_force()
    tk.Label(win, text=prompt, font=("Helvetica", 12)).pack(padx=10, pady=10)
    entry = tk.Entry(win, font=("Helvetica", 12))
    entry.pack(padx=10, pady=5)
    result = {"name": ""}
    def submit():
        name = entry.get().strip()
        if name:
            result["name"] = name
            win.destroy()
    tk.Button(win, text="OK", font=("Helvetica", 12), command=submit).pack(pady=10)
    entry.focus_set()
    win.wait_window()
    return result["name"]

def start_1v1_mode():
    player1 = ask_player_name("1v1 Mode", "Player 1 name:")
    if not player1:
        return
    player2 = ask_player_name("1v1 Mode", "Player 2 name:")
    if not player2:
        return

    def player_turn(player, after_done):
        mode_win = tk.Toplevel(root)
        mode_win.title(f"{player} - Choose Options")
        tk.Label(mode_win, text=f"{player}, choose your mode:", font=("Helvetica", 13)).pack(pady=10)
        mode_var = tk.StringVar(value="classic")
        tk.Radiobutton(mode_win, text="Classic", variable=mode_var, value="classic", font=("Helvetica", 12)).pack(anchor="w", padx=20)
        tk.Radiobutton(mode_win, text="60 Seconds Challenge", variable=mode_var, value="60s", font=("Helvetica", 12)).pack(anchor="w", padx=20)
        tk.Label(mode_win, text="Select category and difficulty, then lives, then click Start.", font=("Helvetica", 10)).pack(pady=5)
        cat_var = tk.StringVar()
        diff_var = tk.StringVar()
        cat_frame = tk.Frame(mode_win)
        cat_frame.pack(pady=5)
        tk.Label(cat_frame, text="Category:", font=("Helvetica", 11)).pack(anchor="w")
        for cat in categories:
            tk.Radiobutton(cat_frame, text=cat, variable=cat_var, value=cat, font=("Helvetica", 11)).pack(anchor="w")
        diff_frame = tk.Frame(mode_win)
        diff_frame.pack(pady=5)
        tk.Label(diff_frame, text="Difficulty:", font=("Helvetica", 11)).pack(anchor="w")
        for diff in difficulties[:-1]:
            tk.Radiobutton(diff_frame, text=diff, variable=diff_var, value=diff, font=("Helvetica", 11)).pack(anchor="w")
        lives_var = tk.IntVar(value=3)
        lives_frame = tk.Frame(mode_win)
        lives_frame.pack(pady=5)
        tk.Label(lives_frame, text="Number of lives:", font=("Helvetica", 11)).pack(anchor="w")
        tk.Spinbox(lives_frame, from_=1, to=10, textvariable=lives_var, width=5, font=("Helvetica", 11)).pack(anchor="w")

        def start_player_game():
            mode = mode_var.get()
            category = cat_var.get()
            difficulty = diff_var.get()
            lives = lives_var.get()
            if not category or not difficulty:
                messagebox.showwarning("Warning", "Please select category and difficulty!")
                return
            questions = load_questions(category, difficulty)
            if not questions:
                messagebox.showerror("Error", "No questions found.")
                return
            mode_win.destroy()
            if mode == "classic":
                play_1v1_round(player, questions, category, difficulty, lives, after_done)
            else:
                play_1v1_60s(player, questions, category, difficulty, lives, after_done)
        tk.Button(mode_win, text="Start", font=("Helvetica", 12, "bold"), command=start_player_game).pack(pady=10)

    def after_p1(p1_result):
        player_turn(player2, lambda p2_result: show_1v1_results(player1, p1_result, player2, p2_result))

    player_turn(player1, after_p1)

def play_1v1_round(player, questions, category, difficulty, lives, callback):
    game_window = tk.Toplevel(root)
    game_window.title(f"{player}'s Turn (Classic)")
    game_window.geometry("550x500")

    score = tk.IntVar(value=0)
    health = tk.IntVar(value=lives)
    question_index = tk.IntVar(value=0)
    selected_answer = tk.StringVar()
    answer_list = []

    def get_timer_duration(category, difficulty):
        timer_settings = {
            "Math": {"Easy": 5, "Medium": 8, "Hard": 10, "Extreme": 15},
            "General Knowledge": {"Easy": 5, "Medium": 8, "Hard": 10, "Extreme": 15},
            "Coding": {"Easy": 5, "Medium": 8, "Hard": 10, "Extreme": 15},
            "Geography": {"Easy": 5, "Medium": 8, "Hard": 10, "Extreme": 15}
        }
        if category == "Mixed":
            return 10
        return timer_settings.get(category, {}).get(difficulty, 15)

    timer_duration = get_timer_duration(category, difficulty)
    timer = tk.IntVar(value=timer_duration)

    hearts_label = tk.Label(game_window, font=("Helvetica", 16))
    countdown_label = tk.Label(game_window, font=("Helvetica", 14))

    def update_hearts():
        hearts_label.config(text="❤️" * health.get())
        if health.get() <= 0:
            question_index.set(len(questions))

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
        if question_index.get() >= len(questions) or health.get() <= 0:
            game_window.destroy()
            callback({
                "score": score.get(),
                "answers": answer_list,
                "category": category,
                "difficulty": difficulty,
                "mode": "classic"
            })
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
        is_correct = selected_answer.get() == correct
        answer_list.append({
            "question": questions[question_index.get()],
            "selected": selected_answer.get(),
            "is_correct": is_correct
        })
        if is_correct:
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

def play_1v1_60s(player, questions, category, difficulty, lives, callback):
    challenge_win = tk.Toplevel(root)
    challenge_win.title(f"{player}'s Turn (60 Seconds Challenge)")
    challenge_win.geometry("550x500")

    score = tk.IntVar(value=0)
    time_left = tk.IntVar(value=60)
    q_index = tk.IntVar(value=0)
    selected_answer = tk.StringVar()
    answer_list = []
    health = tk.IntVar(value=lives)

    time_bonus = {"Easy": 2, "Medium": 3, "Hard": 4, "Extreme": 5}

    def update_hearts():
        hearts_label.config(text="❤️" * health.get())
        if health.get() <= 0:
            q_index.set(len(questions))

    def next_question():
        selected_answer.set("")
        if q_index.get() >= len(questions) or time_left.get() <= 0 or health.get() <= 0:
            challenge_win.destroy()
            callback({
                "score": score.get(),
                "answers": answer_list,
                "category": category,
                "difficulty": difficulty,
                "mode": "60s"
            })
            return
        q = questions[q_index.get()]
        question_label.config(text=q["question"])
        opts = q["options"].copy()
        random.shuffle(opts)
        for i in range(4):
            option_buttons[i].config(text=opts[i], value=opts[i][0])
        timer_label.config(text=f"Time Left: {time_left.get()} s")
        update_hearts()

    def submit():
        if not selected_answer.get():
            return
        q = questions[q_index.get()]
        is_correct = selected_answer.get() == q["answer"]
        answer_list.append({
            "question": q,
            "selected": selected_answer.get(),
            "is_correct": is_correct
        })
        if is_correct:
            score.set(score.get() + 1)
            diff = difficulty
            for d in difficulties:
                if d.lower() in q["question"].lower() or d.lower() in category.lower():
                    diff = d
            bonus = time_bonus.get(diff, 2)
            time_left.set(time_left.get() + bonus)
        else:
            health.set(health.get() - 1)
        q_index.set(q_index.get() + 1)
        next_question()

    def timer_countdown():
        while time_left.get() > 0 and health.get() > 0:
            time.sleep(1)
            time_left.set(time_left.get() - 1)
            timer_label.config(text=f"Time Left: {time_left.get()} s")
            if time_left.get() <= 0 or health.get() <= 0:
                submit_btn.config(state="disabled")
                break

    question_label = tk.Label(challenge_win, text="", wraplength=500, font=("Helvetica", 14))
    question_label.pack(pady=20)
    option_buttons = []
    for _ in range(4):
        btn = tk.Radiobutton(challenge_win, text="", variable=selected_answer, font=("Helvetica", 12))
        btn.pack(anchor="w", padx=20)
        option_buttons.append(btn)
    submit_btn = tk.Button(challenge_win, text="Submit", font=("Helvetica", 12), command=submit)
    submit_btn.pack(pady=10)
    timer_label = tk.Label(challenge_win, text="Time Left: 60 s", font=("Helvetica", 14))
    timer_label.pack()
    hearts_label = tk.Label(challenge_win, text="❤️" * lives, font=("Helvetica", 16))
    hearts_label.pack(pady=5)

    next_question()
    threading.Thread(target=timer_countdown, daemon=True).start()

def show_1v1_results(player1, result1, player2, result2):
    win = tk.Toplevel(root)
    win.title("1v1 Results")
    win.geometry("700x600")

    if result1["score"] > result2["score"]:
        winner = player1
    elif result2["score"] > result1["score"]:
        winner = player2
    else:
        winner = "Draw!"

    confetti_label = tk.Label(win, text="", font=("Helvetica", 30))
    confetti_label.pack(pady=10)
    def confetti():
        for _ in range(10):
            confetti_label.config(text="🎉" * random.randint(5, 15))
            win.update()
            time.sleep(0.15)
        confetti_label.config(text="🎉" * 10)
    threading.Thread(target=confetti, daemon=True).start()

    tk.Label(win, text=f"Winner: {winner}", font=("Helvetica", 18, "bold"), fg="green").pack(pady=10)

    frame = tk.Frame(win)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    tk.Label(frame, text=player1, font=("Helvetica", 14, "bold")).grid(row=0, column=0, padx=10)
    tk.Label(frame, text=player2, font=("Helvetica", 14, "bold")).grid(row=0, column=1, padx=10)

    listbox1 = tk.Listbox(frame, font=("Helvetica", 11), width=35, height=15)
    listbox2 = tk.Listbox(frame, font=("Helvetica", 11), width=35, height=15)
    listbox1.grid(row=1, column=0, padx=5, pady=2)
    listbox2.grid(row=1, column=1, padx=5, pady=2)

    detail_frame1 = tk.Frame(frame)
    detail_frame1.grid(row=2, column=0, padx=5, pady=5, sticky="n")
    detail_frame2 = tk.Frame(frame)
    detail_frame2.grid(row=2, column=1, padx=5, pady=5, sticky="n")

    detail_q1 = tk.Label(detail_frame1, text="", wraplength=300, font=("Helvetica", 12, "bold"))
    detail_q1.pack(pady=2)
    detail_opts1 = [tk.Label(detail_frame1, text="", wraplength=300, font=("Helvetica", 11)) for _ in range(4)]
    for lbl in detail_opts1:
        lbl.pack(anchor="w", padx=10)
    detail_exp1 = tk.Label(detail_frame1, text="", wraplength=300, font=("Helvetica", 12, "italic"), fg="#2e2e2e", bg="#f0f0f0", justify="center")
    detail_exp1.pack(pady=5, fill="x")

    detail_q2 = tk.Label(detail_frame2, text="", wraplength=300, font=("Helvetica", 12, "bold"))
    detail_q2.pack(pady=2)
    detail_opts2 = [tk.Label(detail_frame2, text="", wraplength=300, font=("Helvetica", 11)) for _ in range(4)]
    for lbl in detail_opts2:
        lbl.pack(anchor="w", padx=10)
    detail_exp2 = tk.Label(detail_frame2, text="", wraplength=300, font=("Helvetica", 12, "italic"), fg="#2e2e2e", bg="#f0f0f0", justify="center")
    detail_exp2.pack(pady=5, fill="x")

    for idx, ans in enumerate(result1["answers"], 1):
        status = "✅" if ans["is_correct"] else "❌"
        listbox1.insert("end", f"Q{idx} {status}")
    for idx, ans in enumerate(result2["answers"], 1):
        status = "✅" if ans["is_correct"] else "❌"
        listbox2.insert("end", f"Q{idx} {status}")

    def update_detail(detail_q, detail_opts, detail_exp, ans):
        q = ans["question"]
        detail_q.config(text=q["question"])
        for i, opt in enumerate(q["options"]):
            opt_text = opt
            if opt[0] == q["answer"] and opt[0] == ans["selected"]:
                opt_text += " (Correct Answer, Your Answer)"
            elif opt[0] == q["answer"]:
                opt_text += " (Correct Answer)"
            elif opt[0] == ans["selected"]:
                opt_text += " (Your Answer)"
            detail_opts[i].config(text=opt_text)
        for i in range(len(q["options"]), 4):
            detail_opts[i].config(text="")
        explanation = q.get("explanation", "No explanation available.")
        detail_exp.config(text=f"Explanation: {explanation}")

    def on_select1(event):
        sel = listbox1.curselection()
        if not sel: return
        idx = sel[0]
        ans = result1["answers"][idx]
        update_detail(detail_q1, detail_opts1, detail_exp1, ans)

    def on_select2(event):
        sel = listbox2.curselection()
        if not sel: return
        idx = sel[0]
        ans = result2["answers"][idx]
        update_detail(detail_q2, detail_opts2, detail_exp2, ans)

    listbox1.bind("<<ListboxSelect>>", on_select1)
    listbox2.bind("<<ListboxSelect>>", on_select2)

    tk.Label(win, text=f"{player1} Score: {result1['score']}", font=("Helvetica", 13)).pack()
    tk.Label(win, text=f"{player2} Score: {result2['score']}", font=("Helvetica", 13)).pack()
# --- End 1v1 Mode Integration ---

root = tk.Tk()
root.title("Quiz Quest GUI")
root.geometry("400x550")

is_dark_mode = tk.BooleanVar(value=False)
is_anonymous = tk.BooleanVar(value=False)

theme_button = tk.Button(root, text="🌙 Dark Mode", command=toggle_theme, font=("Helvetica", 10))
theme_button.pack(pady=5)

scoreboard_button = tk.Button(root, text="Scoreboard", font=("Helvetica", 10), command=show_scoreboard)
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
button_frame = tk.Frame(root)

mixed_mode_active = tk.BooleanVar(value=False)

def activate_mixed_mode():
    mixed_mode_active.set(True)
    category_var.set("Mixed")

def deactivate_mixed_mode():
    mixed_mode_active.set(False)

random_button = tk.Button(button_frame, text="🎲 Random", font=("Helvetica", 12, "bold"), command=lambda: [deactivate_mixed_mode(), spin_random_selection()])
random_button.pack(side="left", padx=5)

mixed_button = tk.Button(button_frame, text="🎲 Mixed Mode", font=("Helvetica", 12, "bold"), command=activate_mixed_mode)
mixed_button.pack(side="left", padx=5)

def start_60s_challenge():
    selected_char = character_var.get()
    selected_category = category_var.get()
    selected_difficulty = difficulty_var.get()

    if not selected_char:
        messagebox.showwarning("Warning", "Please select a character!")
        return

    if mixed_mode_active.get():
        selected_category = random.choice(categories[:-1])
        selected_difficulty = random.choice(difficulties)
        category_var.set(selected_category)
        difficulty_var.set(selected_difficulty)

    if not selected_category or not selected_difficulty:
        messagebox.showwarning("Warning", "Please select category and difficulty!")
        return

    questions = load_questions(selected_category, selected_difficulty)
    if not questions:
        messagebox.showerror("Error", "No questions found.")
        return

    show_60s_challenge_window(questions, selected_char, selected_category, selected_difficulty)

challenge_button = tk.Button(button_frame, text="⏱ 60 Seconds Challenge", font=("Helvetica", 12, "bold"), command=start_60s_challenge)
challenge_button.pack(side="left", padx=5)

onevone_button = tk.Button(button_frame, text="🤝 1v1 Mode", font=("Helvetica", 12, "bold"), command=start_1v1_mode)
onevone_button.pack(side="left", padx=5)

root.mainloop()