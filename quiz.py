import random
import sys
from dataclasses import dataclass
from typing import List, Tuple

# Simple word bank; can be expanded
WORD_BANK = [
    "python", "developer", "keyboard", "notebook", "algorithm", "function", "variable",
    "compose", "docker", "github", "machine", "learning", "network", "browser",
    "package", "library", "module", "integer", "string", "boolean", "operator",
    "system", "process", "thread", "memory", "storage", "buffer", "socket", "server",
    "client", "request", "response", "timeout", "session", "cookie", "token",
]

@dataclass
class Question:
    answer: str
    masked: str
    options: List[str]
    correct_index: int


def mask_word(word: str) -> str:
    if len(word) <= 2:
        return "_" * len(word)
    # randomly hide between 1 and max(len-1) characters
    num_to_hide = random.randint(1, max(1, len(word) - 1))
    indices = list(range(len(word)))
    random.shuffle(indices)
    hide = set(indices[:num_to_hide])
    return "".join("_" if i in hide else ch for i, ch in enumerate(word))


def generate_options(answer: str, bank: List[str], k: int = 4) -> Tuple[List[str], int]:
    # Choose k-1 distractors of same length if possible
    same_len = [w for w in bank if w != answer and len(w) == len(answer)]
    pool = same_len if len(same_len) >= k - 1 else [w for w in bank if w != answer]
    distractors = random.sample(pool, k - 1) if len(pool) >= k - 1 else random.choices(pool, k=k - 1)
    options = distractors + [answer]
    random.shuffle(options)
    return options, options.index(answer)


def make_question(bank: List[str]) -> Question:
    answer = random.choice(bank)
    masked = mask_word(answer)
    options, idx = generate_options(answer, bank, 4)
    return Question(answer=answer, masked=masked, options=options, correct_index=idx)


def ask_question(q: Question, question_num: int, score: int) -> int:
    print(f"\nQuestion {question_num}")
    print(f"Word:  {q.masked}")
    for i, opt in enumerate(q.options, 1):
        print(f"  {i}) {opt}")
    while True:
        choice = input("Choose option (1-4) or q to quit: ").strip().lower()
        if choice == 'q':
            print("Exiting quiz.")
            sys.exit(0)
        if choice in {'1','2','3','4'}:
            sel = int(choice) - 1
            if sel == q.correct_index:
                print("Correct! +1 point")
                return score + 1
            else:
                print(f"Wrong. Correct answer was '{q.answer}'.")
                return score
        print("Invalid input. Try again.")


def main():
    print("Missing Letters Word Quiz (MCQ)")
    print("- Underscores (_) mark missing letters")
    print("- Answer by choosing 1-4; 'q' to quit")
    rounds = 10
    try:
        rounds_in = input("How many rounds? [10]: ").strip()
        if rounds_in:
            rounds = max(1, int(rounds_in))
    except Exception:
        pass

    score = 0
    asked = 0
    used = set()
    while asked < rounds:
        q = make_question(WORD_BANK)
        # avoid repeating same answer consecutively
        if q.answer in used and len(used) < len(WORD_BANK):
            continue
        used.add(q.answer)
        score = ask_question(q, asked + 1, score)
        asked += 1

    print(f"\nYour final score: {score}/{rounds}")


if __name__ == "__main__":
    main()
