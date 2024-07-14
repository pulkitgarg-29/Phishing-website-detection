#importing required libraries
import numpy as np
import pandas as pd
from sklearn import metrics 
import pickle
from feature import FeatureExtraction
import os
from flask import Flask, request, render_template, session, redirect, url_for
import sqlite3
import datetime
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Configure SQLite database
DATABASE = 'database.db'

def create_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users 
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL
                )''')

     # Create feedback table
    c.execute('''CREATE TABLE IF NOT EXISTS feedback 
                 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    name TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    comment TEXT NOT NULL,
                    FOREIGN KEY (username) REFERENCES users(username)
                 )''')
    conn.commit()
    conn.close()

def insert_user(username, email, password, name, age):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    sql_query = "INSERT INTO users (username, email, password, name, age) VALUES (?, ?, ?, ?, ?)"

    print(sql_query)
    params = (username, email, password, name, age)
    print("SQL Query:", sql_query)
    print("Parameters:", params)
    c.execute(sql_query, params)
    conn.commit()
    conn.close()


def get_user(username):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user


@app.route("/")
def home():
    return render_template("landing.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        age = request.form['age']
        
        if get_user(username):
            message = "User already exists!"
            return render_template('login.html', message=message)
        insert_user(username, email, password, name, age)
        message = "Account successfully created"
        return render_template('login.html', message=message)
    return render_template('login.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)

        if user and user[3] == password:
            session['username'] = username
            return redirect(url_for('index'))
        return render_template('login.html', message="Invalid username or password!")
    return render_template('login.html')

@app.route('/publishfeedback', methods=["GET", "POST"])
def publishfeedback():
    if request.method == 'POST':

        feedback = request.form['feedback']
 
        username = session.get('username')
        
        timestamp = datetime.datetime.now()
   
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO feedback (username, name, timestamp, comment) VALUES (?, ?, ?, ?)',
                       (username, username, timestamp, feedback))
                       
        conn.commit()
        conn.close()

        return render_template('publishfeedback.html', message='Thank you for your feedback!')

    else:
        return render_template('publishfeedback.html')

    
def get_latest_comments():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("SELECT name, comment, SUBSTR(timestamp, 1, 19) FROM feedback ORDER BY timestamp DESC")

    rows = c.fetchall()

    conn.close()
    return rows

@app.route('/feedback')
def feedback():
    rows = get_latest_comments()
    print(rows)
    return render_template('feedback.html', rows=rows)


@app.route('/index')
def index():
    user = session.get('username')
    print(user)

    phishing_count_each, legit_count_each = get_url_counts_each_user()
    phishing_total_count = get_url_total_counts_each_user()

    if user == 'admin':
        return render_template('index_admin.html', user=user, x = phishing_total_count, y = phishing_count_each, z = legit_count_each)
    else:
        return render_template("index_admin.html", user=user, x = phishing_total_count, y = phishing_count_each, z = legit_count_each)

@app.route("/logout", methods=["POST"])
def logout():
    session.pop('username', None)
    return redirect(url_for('landing'))

file = open("pickle/model.pkl","rb")
gbc = pickle.load(file)
file.close()

@app.route("/landing")
def landing():
    return render_template("landing.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

def get_user_profile():

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    username = session.get('username')
    c.execute("SELECT name, age, email, username FROM users where username=?", (username,))

    rows = c.fetchall()

    conn.close()

    return rows

def get_url_counts_each_user():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    username = session.get('username')

    # Count phishing URLs
    cursor.execute("SELECT COUNT(*) FROM Activity WHERE urlType = 'phishing' and username=?", (username,))
    phishing_count = cursor.fetchone()[0]

    # Count legit URLs
    cursor.execute("SELECT COUNT(*) FROM Activity WHERE urlType = 'legit' and username=?", (username,))
    legit_count = cursor.fetchone()[0]

    conn.close()

    return phishing_count, legit_count

def get_url_total_counts_each_user():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    username = session.get('username')

    # Count phishing URLs
    cursor.execute("SELECT COUNT(*) FROM Activity where username=?", (username,))
    phishing_total_count = cursor.fetchone()[0]

    conn.close()

    return phishing_total_count


@app.route("/profile")
def profile():

    rows = get_user_profile()
    phishing_count_each, legit_count_each = get_url_counts_each_user()
    phishing_total_count = get_url_total_counts_each_user()

    return render_template("profile.html", x = phishing_total_count, y = phishing_count_each, z = legit_count_each, rows = rows)

def get_url_counts():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Count phishing URLs
    cursor.execute("SELECT COUNT(*) FROM Activity WHERE urlType = 'phishing'")
    phishing_count = cursor.fetchone()[0]

    # Count legit URLs
    cursor.execute("SELECT COUNT(*) FROM Activity WHERE urlType = 'legit'")
    legit_count = cursor.fetchone()[0]

    conn.close()

    return phishing_count, legit_count

def get_comment_counts():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("select count(*) from feedback")
    comment_count = cursor.fetchone()[0]

    conn.close()

    return comment_count

def get_latest_urls():
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT username, url, urlDate, urlType, blockedFlag FROM Activity ORDER BY urlDate DESC LIMIT 7")
    latest_urls = cursor.fetchall()

    conn.close()

    return latest_urls

@app.route("/dashboard")
def dashboard():
    phishing_count, legit_count = get_url_counts()
    comment_count = get_comment_counts()
    urls = get_latest_urls()
    return render_template("dashboard.html", legit_count = legit_count, phishing_count = phishing_count, comment_count= comment_count, latest_urls = urls)



# Example usage
phishing_count, legit_count = get_url_counts()
print("Total number of phishing URLs:", phishing_count)
print("Total number of legit URLs:", legit_count)



@app.route("/error", methods=['GET', 'POST'])
def error():

    blocked = False

    if request.method == "POST":
        url = request.form["url"]
        obj = FeatureExtraction(url)
        x = np.array(obj.getFeaturesList()).reshape(1,30) 
        y_pro_non_phishing = gbc.predict_proba(x)[0,1]

        percentage = round(y_pro_non_phishing * 100)

        if 0 <= percentage < 50:
            percentage = 100 - percentage
            prediction_label = f"Website is {percentage:.2f}% unsafe to use..."
            blocked = True
        else:
            prediction_label = f"Website is {percentage:.2f}% safe to use..."
            blocked = False

        url_copy = url

        if blocked:
            prediction_label += " Website is blocked."
            url = ""

        username = session.get('username')

        url_date = datetime.datetime.now()
        url_type = "phishing" if blocked else "legit"

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        sql = "INSERT INTO Activity (username, url, urlDate, urlType, blockedFlag) VALUES (?, ?, ?, ?, ?)"
        values = (username, url_copy, url_date, url_type, blocked)

        cursor.execute(sql, values)
        
        conn.commit()
        conn.close()

        return render_template('outcome.html', prediction_label=prediction_label, url=url_copy, user=username)
    
    return redirect(url_for('index'))



if __name__ == "__main__":
    app.secret_key = 'fgxfhcgjvhkbl8674566ohihi987r6754'
    app.run(debug=True)
