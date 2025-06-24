import json
import time 
def load_questions(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

all_questions = load_questions("question.json")

question_bank = all_questions 

time_limits = {
    'Math': 15,
    'Geography': 10,
    'General Knowledge': 10,
    'Coding': 15
}

class QuizGame:
    def __init__(self, character, category, difficulty):
        self.character = character
        self.health = 5
        self.score = 0
        self.category = category
        self.difficulty = difficulty
        self.questions = question_bank[category][difficulty]

    def ask_question(self, q):
        print(f"\nCategory: {self.category} | Difficulty: {self.difficulty}")
        print(q['question'])
        for opt in q['options']:
            print(opt)

        time_limit = time_limits[self.category]
        start = time.time()
        answer = input(f"You have {time_limit} seconds. Your answer: ").strip().upper()
        elapsed = time.time() - start

        if elapsed > time_limit:
            print(f" Time's up! You took {int(elapsed)} seconds.")
            self.health -= 1
            print(f" Lost 1 health. Remaining: {self.health}")
            return False

        if answer == q['answer']:
            print(" Correct!")
            self.score += 10
            return True
        else:
            self.health -= 1
            print(f"Remaining health: {self.health}")
            return False

    def is_alive(self):
        return self.health > 0

def choose_character():
    print("Choose your character:\n (W)arrior\n (M)age\n (A)rcher")
    while True:
        choice = input("Enter W, M, or A: ").strip().lower()
        if choice == 'w': return "Warrior"
        elif choice == 'm': return "Mage"
        elif choice == 'a': return "Archer"
        else: print("Invalid input! Choose W, M, or A.")

def choose_option(prompt, options):
    print(prompt)
    for i, option in enumerate(options, 1):
        print(f"{i}) {option}")
    while True:
        choice = input("Enter number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice)-1]
        else:
            print("Invalid selection.")

def main():
    print("🎮 Welcome to Quiz Quest!")
    print("Fight with knowledge, protect your health!\n")

    character = choose_character()
    category = choose_option("Choose a category:", list(question_bank.keys()))
    difficulty = choose_option("Choose difficulty:", list(question_bank[category].keys()))

    game = QuizGame(character, category, difficulty)

    print(f"\n You are a {character} with {game.health} health.\n")
    for question in game.questions:
        if not game.is_alive():
            print(" Game Over!")
            break
        game.ask_question(question)

    if game.is_alive():
        print(f"\ Victory! Final score: {game.score}")

if __name__ == "__main__":
    main()