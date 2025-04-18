from flask import Flask, render_template, request
from pymysql import connections
import os
import random
import argparse
import boto3
import logging
import time
from pymysql.err import OperationalError


app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "passwors"
DATABASE = os.environ.get("DATABASE") or "employees"
DBPORT = int(os.environ.get("DBPORT"))
BUCKET = os.environ.get("BUCKET")
IMAGE_KEY = os.environ.get("IMAGENAME")
HEADER = os.environ.get("HEADER_NAME")

def download_file(image_key, bucket): #Function to download a given file from an S3 bucket
    s3 = boto3.resource('s3')
    output = f"static/{image_key}"
    s3.Bucket(bucket).download_file(image_key, output)
    logging.info(f"Background image will be served from: {output}")
    return output

download_file(IMAGE_KEY, BUCKET)

# Create a connection to the MySQL database
def get_db_connection(retries=5, delay=2, backoff=2):
    for attempt in range(retries):
        try:
            return connections.Connection(
                host=DBHOST,
                port=DBPORT,
                user=DBUSER,
                password=DBPWD,
                db=DATABASE
            )
        except OperationalError as e:
            logging.warning(f"MySQL connection failed (attempt {attempt+1}): {e}")
            if attempt < retries - 1:
                time.sleep(delay)
                delay *= backoff
            else:
                logging.error("Failed to connect to MySQL after several attempts.")
                raise

output = {}
table = 'employee';

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('addemp.html', header_name=HEADER, bg_image=IMAGE_KEY)

@app.route("/about", methods=['GET','POST'])
def about():
    return render_template('about.html', header_name=HEADER, bg_image=IMAGE_KEY)
    
@app.route("/addemp", methods=['POST'])
def AddEmp():
    db_conn = get_db_connection()
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

  
    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        
        cursor.execute(insert_sql,(emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('addempoutput.html', name=emp_name, header_name=HEADER, bg_image=IMAGE_KEY)

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", header_name=HEADER, bg_image=IMAGE_KEY)


@app.route("/fetchdata", methods=['GET','POST'])
def FetchData():
    db_conn = get_db_connection()
    emp_id = request.form['emp_id']

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location from employee where emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql,(emp_id))
        result = cursor.fetchone()
        
        # Add No Employee found form
        output["emp_id"] = result[0]
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["primary_skills"] = result[3]
        output["location"] = result[4]
        
    except Exception as e:
        print(e)

    finally:
        cursor.close()

    return render_template("getempoutput.html", id=output["emp_id"], fname=output["first_name"],
                           lname=output["last_name"], interest=output["primary_skills"], location=output["location"], header_name=HEADER, bg_image=IMAGE_KEY)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=81,debug=True)
