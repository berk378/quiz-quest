# Quiz Quest GUI

Quiz Quest GUI is a desktop trivia game where you can compete in various categories and difficulty levels, choose unique characters, and play in different game modes.

## Features

- **Category & Difficulty Selection:** Play in Math, Geography, General Knowledge, Coding, History, or Mixed categories.
- **Character Selection:** Choose from Warrior, Wizard, Archer, or Classic, each with unique abilities.
- **Game Modes:**
  - Classic Mode
  - 60 Seconds Challenge
  - 1v1 (Two Player) Mode
  - Mixed & Random Modes
- **Scoreboard:** View top scores by category and difficulty.
- **Dark/Light Theme Support**
- **Animated Character GIFs**

## Installation

### 1. Required Files

- `quiz_quest_gui.py` (main application file)
- `questions.json` (question database)
- `scores.json` (for scores, can be an empty JSON file)
- Character GIF files (e.g., `Warrior.gif`, `Wizard.gif`, `Archer.gif`, etc.)

### 2. Python Requirement

This app is written in Python. You need Python 3.8+ installed on your computer.  
[Download Python](https://www.python.org/downloads/)

### 3. Required Libraries

The app uses only standard Python libraries (`tkinter`, `json`, `threading`, `random`, `os`, `time`).  
No extra packages are needed.

### 4. Running the App

#### To run with Python:

1. Place all files in the same folder.
2. Open a terminal or command prompt in that folder.
3. Run:
   ```
   python quiz_quest_gui.py
   ```

#### To create a Windows .exe:

1. Install [PyInstaller](https://pyinstaller.org/):
   ```
   pip install pyinstaller
   ```
2. Build the .exe:
   ```
   pyinstaller --onefile --noconsole quiz_quest_gui.py
   ```
3. Copy `quiz_quest_gui.exe` from the `dist` folder and all required files (JSON and GIFs) into the same folder.
4. Double-click `quiz_quest_gui.exe` to start the app.

## Usage

1. **Enter your name** or play anonymously.
2. **Choose your character.** Each has a special ability:
   - **Warrior:** Starts with +1 extra life.
   - **Wizard:** +3 seconds extra time per question.
   - **Archer:** +1 bonus point at the end of the game.
   - **Classic:** No special abilities.
3. Click **CONTINUE**.
4. **Select category** and **difficulty**.
5. Choose a game mode:
   - **Start Game:** Classic mode.
   - **60 Seconds Challenge:** Answer as many questions as possible in 60 seconds.
   - **1v1 Mode:** Two players take turns.
   - **Random/Mixed Mode:** Random category and difficulty.
6. At the end, view your score and answers.
7. Use the **Scoreboard** button to see top scores.
8. Switch between dark and light themes with the 🌙/☀️ button.

## FAQ

### Can I run the .exe on my phone?
**No.** The `.exe` file only works on Windows computers. To use on a phone, you would need a separate Android/iOS version.

### Are my scores and questions saved?
Yes, your scores and questions are stored in the JSON files. As long as you don't delete them, your data is safe.

### What if I get an error?
- Make sure all required files are in the same folder.
- Check the error message and contact the developer if needed.

## Contributing

Pull requests and suggestions are welcome!  
To add new questions, edit the `questions.json` file.
