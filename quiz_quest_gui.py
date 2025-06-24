import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Quiz Quest GUI")
    root.geometry("400x300")

    label = tk.Label(root, text="Welcome to Quiz Quest GUI!", font=("Arial", 16))
    label.pack(pady=50)

    root.mainloop()

if __name__ == "__main__":
    main()
