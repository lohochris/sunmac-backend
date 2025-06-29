# 🌞 SUNMAC Backend – Strategic Unified Network for Mathematics and AI Competence

Welcome to the backend of **SUNMAC** – a Django-based educational platform designed to provide intelligent math assistance to students and teachers. SUNMAC delivers AI-powered step-by-step math solutions, personalized dashboards, and easy-to-use interfaces for educators and learners.

---

## 🚀 Features

- 🎓 **Student Tools** – Upload handwritten math problems or type questions to get instant AI-powered step-by-step solutions.
- 👩‍🏫 **Teacher Tools** – Explore insights and tools to assist in instruction, assessment, and student support.
- 📘 **Digital Solution Book** – Solutions are presented in a book-like interface for better learning experience.
- 📄 **PDF Print Option** – Easily save or print math solutions for offline study.
- 🔒 **Secure Authentication** – User sign up, login, logout with session protection.
- 🧠 **AI Integration** – Powered by GPT to solve equations and explain math concepts clearly.
  
---

## 🛠️ Technologies Used

- **Backend Framework**: Django (Python)
- **Frontend Integration**: HTML, CSS, JavaScript
- **AI Integration**: OpenAI GPT (via API)
- **Styling**: Custom responsive CSS with book-styled layouts
- **Database**: SQLite (development)

---

## 📁 Project Structure

```bash
sunmac_backend/
│
├── core/                    # Django app with views, models, forms, templates
│   ├── templates/core/      # HTML templates
│   ├── static/core/         # CSS, images, JS
│   └── views.py             # Main logic for student/teacher tools
│
├── manage.py                # Django entry point
└── requirements.txt         # Python dependencies

🚦 How to Run the Project
1. Clone the Repository
git clone https://github.com/lohochris/sunmac-backend.git
cd sunmac-backend

2. Create a Virtual Environment
python -m venv env
source env/bin/activate  # or `env\Scripts\activate` on Windows

3. Install Dependencies
pip install -r requirements.txt

4. Run the Server
python manage.py migrate
python manage.py runserver

Visit http://127.0.0.1:8000/ in your browser.

📸 Screenshots
Student AI Tool	Digital Solution Book
Upload/Type Math	View Beautiful Step-by-Step Results

📬 Contribution & Feedback
If you have suggestions, ideas, or bug reports, please open an issue or submit a pull request.

📄 License
This project is licensed under the MIT License.
Created by Loho Christopher with passion for smart, AI-driven education.
