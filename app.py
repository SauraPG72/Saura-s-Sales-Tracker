from crypt import methods
from typing import ClassVar
from flask import Flask, render_template, request, session, redirect, make_response
import psycopg2
import bcrypt
import os
import csv
from csv import reader
from io import TextIOWrapper
import pdfkit

app = Flask(__name__)

# for making this relevant to my Heroku
DATABASE_URL = os.environ.get('DATABASE_URL', 'dbname=project2')
SECRET_KEY = os.environ.get('SECRET_KEY', 'kdcnbiowe913827fd')
app.config['SECRET_KEY'] = SECRET_KEY

# connect to database code function, which I will use exrttensively later on. 
def database_connect(command, args=[]):
    conn = psycopg2.connect(DATABASE_URL)
    curs = conn.cursor()
    
    if "SELECT" in command:
        if args == []:
            curs.execute(f"{command}")
            result = curs.fetchall()
            conn.commit()
            conn.close()
            return result
        else:
            curs.execute(f"{command}", args)
            result = curs.fetchall()
            conn.commit()
            conn.close()
            return result
    else:
        curs.execute(f"{command}", args)
        conn.commit()
        conn.close()

# This is the home page, basic login page structurted as a form that wil send a post request
@app.route('/')
def hello():
    return render_template('index.html')

# This is the result of the log in details entered, it will connect to user and password table and let you in or keep you out.
@app.route('/youre-in', methods=['POST'])
def login():
# Line 37 to the next comment structures out a command sent to postgres. it calls a function defined above for ease of use database_connect(), and has been used to verify if you are a valid or invalid user. 
    email = request.form.get('email')
    password = request.form.get('password')
    result = database_connect('SELECT id, email, name, password FROM users WHERE email = %s', [email])
    if result == []:
        return redirect('/')
    
    password_hash = result[0][3]
    print(password_hash)
# using bcrypt we can check if the stored and encrypted pw is the same as what you have placed.   
    valid = bcrypt.checkpw(password.encode(), password_hash.encode())
# logic for if you are let in, or if you are not let in. 
    if valid == True:
        session['email'] = email
        # this line is relevant for CRUD operations made to your clients database
        session['unique_id_number'] = result[0][0]
        return redirect('/home')
    else:
        return redirect('/')

# This is the home screen for when you get in 
@app.route('/home')
def logged_in():
    if session:
        user_id = session.get('unique_id_number')
        result = database_connect('SELECT client_id, user_id, client_name, company, phone, email, suburb, status FROM clients WHERE user_id = %s', [user_id])
        list_of_client_dicts = []

        for client in result:
            client_dict = {}
            client_dict['client_id'] = client[0]
            client_dict['name'] = client[2]
            client_dict['company'] = client[3]
            client_dict['phone'] = client[4]
            client_dict['email'] = client[5]
            client_dict['suburb'] = client[6]
            client_dict['status'] = client[7]
            list_of_client_dicts.append(client_dict)
        return render_template('home.html', list_of_client_dicts=list_of_client_dicts)
    else:
        return redirect('/make_note')

# defining a new app route for when I want to find out more about a certain person.  
@app.route('/home/<id>')
def findmore(id):
    # print(id)
    result = database_connect('SELECT client_id, user_id, client_name, company, phone, email, suburb, status FROM clients WHERE client_id = %s', [id])
    client_id = result[0][0]
    notes = database_connect('SELECT note_id, user_id, client_id, note_s, date_time FROM notes WHERE client_id = %s', [client_id])
    print(notes)
    return render_template('more.html', result=result, notes=notes)

# this will store the note in the database, making it viewable for the client 
@app.route('/make_note/<user>/<client>', methods=['POST'])
def make_note(user, client):
    notes = request.form.get('note')
    database_connect('INSERT into notes (user_id, client_id, note_s) VALUES(%s, %s, %s)', [user, client, notes])
    return redirect(f"/home/{client}")
    
# defining a new app route for moving a certain contact to the next collumn 
@app.route('/progress/<id>')
def progress_right(id):
    print(id)
    result = database_connect('SELECT status FROM clients WHERE client_id = %s', [id])
    new_status = int(result[0][0]) + 1
    print(new_status)
    if new_status < 7:
        new_command = database_connect('UPDATE clients SET status = %s WHERE client_id = %s;', [new_status, id])
        return redirect('/home')

# now defining the opposite movement, whereby if it is moving back a stage
@app.route('/moveback/<id>')
def move_back(id):
    result = database_connect('SELECT status FROM clients WHERE client_id = %s', [id])
    new_status = int(result[0][0]) - 1
    new_command = database_connect('UPDATE clients SET status = %s WHERE client_id = %s;', [new_status, id])
    return redirect('/home')
    
# this is the code for now adding a new contact, it's a form that simply will append itself as a list to the back of your existing database. 
@app.route('/add-new-contact')
def add_new_contact():
    return render_template('newcontact.html')

@app.route('/added-contact', methods=['GET'])
def adding_contact():
    name = request.args.get('name')
    company = request.args.get('company')
    phone = request.args.get('phone')
    if len(phone) == 10:
        phone_number = int(phone)
    else:
        return redirect('/add-new-contact')
    
    email = request.args.get('email')
    suburb = request.args.get('suburb')
    status = request.args.get('status')
    
    if len(name) > 4 and len(company) > 4 and len(phone) == 10 and email and len(suburb) > 4 and status:
        print(f"{name} {company} {phone} {email} {suburb} {status}")
# now establish that the user is the actual user for this deal 
        user_email = session.get('email')
        result = database_connect('SELECT id, name, email, password from users WHERE email = %s', [user_email])
        user_id = result[0][0]
# now that user is established, we can do the insert operation in excel. 
        insert_new_client = database_connect('INSERT INTO clients (user_id, client_name, company, phone, email, suburb, status) VALUES (%s, %s, %s, %s, %s, %s, %s)', [user_id, name, company, phone_number, email, suburb, status])
        return redirect('/home')    
    else:
        return redirect('/add-new-contact')
# now some code for uploading a CSV File
@app.route('/addmultiple', methods=['POST'])
def read_csv():
    csv_file = request.files['file']
    csv_file = TextIOWrapper(csv_file, encoding='utf-8')
    csv_string = csv_file.read()
    csv_list = csv_string.split(",,")
    converted_list = []
    
    for element in csv_list[0:(len(csv_list) - 1)]:
        converted_list.append(element.strip())
    
    for element in converted_list:
        client = element.split(",")
        user_id = session.get('unique_id_number')
        name = client[0]
        company = client[1]
        phone = int(client[2])
        email = client[3]
        suburb = client[4]
        status = 0
        insert_new_client = database_connect('INSERT INTO clients (user_id, client_name, company, phone, email, suburb, status) VALUES (%s, %s, %s, %s, %s, %s, %s)', [user_id, name, company, phone, email, suburb, status])

    return redirect('/home')

# just creating a little log out page now that will redirect me to log in. 
@app.route('/logout')
def clear_and_logout():
    session.clear()
    return redirect('/')

# creating a sign up page for someone to add themselves as a user to my app
@app.route('/signup')
def sign_up():
    return render_template('signup.html')

@app.route('/signedup', methods=['POST'])
def client_signed():
    name = request.form.get('name')
    password_one = request.form.get('password_1')
    password_two = request.form.get('password_2')
    email = request.form.get('email')

    if len(name) >= 4 and password_one == password_two and email:
        password_hash = bcrypt.hashpw(password_one.encode(), bcrypt.gensalt()).decode()
        print(password_hash)
        user_make = database_connect('INSERT into users (email, name, password) VALUES (%s, %s, %s)', [email, name, password_hash])
        return "Big success"
    else:
        return redirect('/')

# last application: invoice maker 
@app.route('/invoice')
def invoice_form():
    return render_template('invoice.html')

# normal tax invoice maker
@app.route('/taxinvoice', methods=['POST'])
def generate_invoice():
    invoice = request.form.get('status')
    you = request.form.get('your_company')
    name = request.form.get('name')
    company = request.form.get('company')
    description = request.form.get('description')
    abn = request.form.get('ABN')
    bsb = request.form.get('BSB')
    amount_not = request.form.get('amount')
    amount = round((int(amount_not)), 2)
    net = round((int(amount)/11 * 10), 2)
    gst = round((int(amount)/11), 2)
    account_number = request.form.get('accountnum')
    invoice_num = request.form.get('invoice')
    rendered = render_template('makeinvoice.html', invoice=invoice, you=you, name=name, company=company, abn=abn, bsb=bsb,account_number=account_number, invoice_num=invoice_num, description=description, amount=amount, net=net, gst=gst)

    pdf = pdfkit.from_string(rendered, False)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=output.pdf'

    return response


if __name__ == '__main__':
    app.run(debug=True)