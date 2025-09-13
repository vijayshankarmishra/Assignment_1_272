# 🎉 Missing Letters Word Quiz — Play in Your Browser!

Guess the word with missing letters! Each round shows a hidden word like `a_go_ith_` and gives you 4 choices. Pick the right one to earn points. Simple, fast, and fun.

## ✨ What you get
- 🔤 Random letters hidden (start, middle, or end)
- ❓ 4 choices (MCQ) each round
- 🧠 10 rounds by default
- 🏆 Score goes up when you get it right
- 🌐 Works in your web browser (no install!)

## 🚀 Play locally (no Docker)
1) Open the folder `web/`.
2) Double-click `index.html` to open it in your browser.

That's it!

## �� Run with Docker (recommended)
From the project folder:
```bash
docker compose up --build
```
Now open: `http://localhost:8080`

## 📁 Project structure
```
word-quiz/
  ├── web/
  │   ├── index.html
  │   ├── styles.css
  │   └── app.js
  ├── Dockerfile            # nginx serving the web app
  ├── docker-compose.yml    # publishes port 8080 → http://localhost:8080
  ├── quiz.py               # (optional) terminal version
  ├── requirements.txt
  └── .gitignore
```

## ☁️ Share with the world
- GitHub Pages: host the `web/` folder for free.
- Docker Hub: `docker build -t yourname/word-quiz-web:latest . && docker push yourname/word-quiz-web:latest`

## 🧩 Customize
- Add more words in `web/app.js` (the `WORD_BANK` list).
- Change rounds in `app.js` → `totalRounds`.

Have fun! 🎈
