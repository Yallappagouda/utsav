# Utsavai Event Vendor Recommendation Web

A Flask-based web app that helps users plan events by recommending vendors according to event type, location, and budget. The app supports user accounts (email login/registration), vendor comparison, budget tracking, ASCII-based data visualizations, and lets users export recommendations to a text file.

---

## Features

- **User Authentication:** Register and log in securely with email and password.
- **Event Planning:** Input event type, location, and budget to get tailored vendor recommendations.
- **Vendor Comparison Table:** View and compare all filtered vendors in a sortable table.
- **Budget Utilization Summary:** See how much of your budget is spent and what remains.
- **ASCII Data Visualization:** Visual bar charts for scores and budget utilization.
- **Export/Share:** Download your personalized vendor recommendations as a `.txt` file.
- **Responsive UI:** Modern, mobile-friendly interface with welcoming login page.

---

## Getting Started

### 1. Clone the Repository

```sh
git clone https://github.com/Yallappagouda/utsavai-event-web.git
cd utsavai-event-web
```

### 2. Set Up a Virtual Environment

```sh
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

> If you don't have a `requirements.txt`, install manually:
> ```sh
> pip install flask flask-login flask-sqlalchemy
> ```

### 4. Run the Application

```sh
python app.py
```

The app will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Usage

1. **Register** a new account or **login** with your email and password.
2. **Enter event details** (type, location, budget) on the main page.
3. **View recommendations, vendor comparison, budget summary, and ASCII visualizations**.
4. **Download** your recommendations as a text file for easy sharing.

---

## Project Structure

```
utsavai-event-web/
│
├── app.py
├── users.db               # Created automatically
├── requirements.txt
├── static/
│   └── style.css
└── templates/
    ├── index.html
    ├── login.html
    ├── register.html
    └── result.html
```

---

## Screenshots

> Add screenshots here for UI demonstration.

---

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## License

[MIT](LICENSE)

---

## Author

[Yallappagouda](https://github.com/Yallappagouda)
