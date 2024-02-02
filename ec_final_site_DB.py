from flask import Flask, redirect, url_for, render_template, request, session, flash
import mysql.connector
import logging
import os 

key = os.getenv("SERVER_PW")
# sql start
def create_connection():
    conn = None
    try:
        conn = mysql.connector.connect(user='root', password=key, host='localhost', database='ec_final')
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DATABASE()")
        info = cursor.fetchone()
        logging.info(f"Connection established to: {info}")

    except Exception as e:
        logging.error(f"Ran into an issue: {e}")
    return conn

def get_data_from_db(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''SELECT * FROM signup_form''')
    rs = cursor.fetchall()
    return rs

def get_item_data(conn, item):
    cursor = conn.cursor()
    cursor.execute(f'SELECT user_id FROM ec_final.signup_form WHERE user_id = {item}')
    rs = cursor.fetchall()
    return rs

def insert_data(conn, user):
    with conn.cursor() as cur:
        # add a context manager here to handle close() automatically
        sql = ''' INSERT INTO signup_form(first_name,last_name,email,type_of_pet,breed,pet_DOB,male_female,visit_reason)
              VALUES(%s,%s,%s,%s,%s,%s,%s,%s) '''
        cur.execute(sql, user)
        conn.commit()
    return cur.lastrowid

def delete_data(conn, id):
    
    sql = f'DELETE FROM ec_final.signup_form WHERE user_id = {id};'
    with conn.cursor(dictionary=True) as cur:
        # cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
    return cur.lastrowid

def get_data_from_user(first_name,last_name, email, pet_type, breed, dob, pet_s, exam):
    return (first_name,last_name, email, pet_type, breed, dob, pet_s, exam)
# sql end

# flask code
app = Flask(__name__)
# db_data = 0

@app.route("/", methods=['GET','POST'])
def main():
    
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    pet_type = request.form.get("pet_type")
    breed = request.form.get("breed")
    dob = request.form.get("dob")
    pet_s = request.form.get("pet_s")
    exam = request.form.get("exam")
    if request.method == "POST":
        insert_data(create_connection(),get_data_from_user(first_name,last_name, email, pet_type, breed, dob, pet_s, exam))
    
    db_data = get_data_from_db(create_connection())
    return render_template("form.html", db_data=db_data)
    
@app.route("/delete", methods=["POST"])
def remove_record():
    db_data = get_data_from_db(create_connection())
    id = request.form.get("delete_user")    
    try:
        for index in db_data:
            if index['user_id'] == int(id):
                delete_data(create_connection(), index['user_id'])
        return f'<h1>Deleted User With User ID of {id}</h1> <br> <a href="{url_for("main")}">Click Here to Go Back to Main Page</a>'
    except Exception as e:
        logging.error(e)
        return f"Error: {str(e)}"
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(message)s')
    app.run(debug=True, port=5002)