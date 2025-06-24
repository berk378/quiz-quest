import json

def load_questions(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

all_questions = load_questions("question.json")
question_bank = all_questions 

class QuizGame:
    def __init__(self, category, difficulty):
        self.score = 0
        self.category = category
        self.difficulty = difficulty
        self.questions = question_bank[category][difficulty]

    def ask_question(self, q):
        print(f"\nCategory: {self.category} | Difficulty: {self.difficulty}")
        print(q['question'])
        for opt in q['options']:
            print(opt)

        answer = input("Your answer: ").strip().upper()

        if answer == q['answer']:
            print("✅ Correct!")
            self.score += 10
            return True
        else:
            print("❌ Wrong!")
            return False

def main():
    print("🎮 Welcome to Quiz Quest!")
    
    # Simple hardcoded category and difficulty
    category = "Math"
    difficulty = "Easy"
    
    game = QuizGame(category, difficulty)
    
    for question in game.questions:
        game.ask_question(question)
    
    print(f"\nGame finished! Final score: {game.score}")

if __name__ == "__main__":
    main()
