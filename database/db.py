import mysql.connector

db = mysql.connector.connect(host="localhost", user="root", password="Ali100000", database="resume_scanner")
cursor = db.cursor()

def save_to_db(name, email, phone, skills):
    query = "INSERT INTO resumes (name, email, phone, skills) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (name, email, phone, ", ".join(skills)))
    db.commit()
