# Simple Finance App
A personal finance dashboard built with **Python**, **Pandas**, **Streamlit**, and **Plotly**.  
This app empowers you to take control of your finances through interactive visualizations and customizable transaction categorization.

This project is inspired by the YouTube tutorial [How To Automate Your Finances with Python](https://youtu.be/wqBlmAWqa6A?si=o4ho_91djL6ZXHY0)


---

## Features

- **Upload Transactions** — Import your CSV bank statements or budget exports  
- **Data Cleaning** — Clean and structure transaction data with Pandas  
- **Categorization** — Add/edit categories and assign keywords for automatic classification  
- **Dynamic Visualizations** — Analyze your spending patterns through:
  - Expense summary tables
  - Donut chart (Expenses vs Remaining Balance)
  - Bar chart (Expenses by Category)
  - Line chart (Daily Expenses over Time)
- **Keyword Learning** — The app “learns” which keywords belong to which categories over time


---


## Tech Stack

- Python 3
- Pandas
- Streamlit
- Plotly

---

## How to Run the App

1. Clone the Repository
```
git clone https://github.com/RosemaryOjwang/finance-automation-python.git
```
2. Navigate to the directory 'finance-automation-python' using the command:
```
cd finance-automation-python
```
3. Create a virtual environment using the command python -m venv env

4. Activate the virtual environment using:  

  - for windows use env\Scripts\activate
  - for Linux and MacOS use source env/bin/activate. The same applies for Gitbash.
5. Run requirements file to install libraries using the following:
```
pip install -r requirements.txt
```
6. Run the App
```
streamlit run main.py
```
7. Open in Browser
Streamlit will automatically open your default browser. If not, visit:

http://localhost:8501

---

## Demo
![Demo](demo.gif)


---

## Work in Progress

This app is constantly being refined! Upcoming improvements may include:

- Exportable reports
- Budget vs actual comparison
- More robust keyword matching
- Enhanced responsive layout

---


This is a practice project by **Rosemary Ojwang**, part of my learning journey in Data Analytics, upskilling in Python, data storytelling, and dashboard development. 

Feel free to fork, use, or contribute!

---