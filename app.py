from flask import Flask, render_template, request, session, redirect
import psycopg2
import bcrypt
app = Flask(__name__)
import os
# for making this relevant to my Heroku
DATABASE_URL = os.environ.get('DATABASE_URL', 'dbname=project2')
SECRET_KEY = os.environ.get('SECRET_KEY', 'kdcnbiowe913827fd')
app.config['SECRET_KEY'] = SECRET_KEY

# connect to database code function, which I will use exrttensively later on. 
def database_connect(command, args=[]):
    conn = psycopg2.connect('dbname=project2')
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
    result = database_connect('SELECT id, email, name, password FROM users', [])
    dict_of_users = {}
    for user in result:
        password_hash = user[3]
        dict_of_users[user[1]] = [user[2], password_hash]
# using bcrypt we can check if the stored and encrypted pw is the same as what you have placed.    
    valid = bcrypt.checkpw(password.encode(), password_hash.encode())
# logic for if you are let in, or if you are not let in. 
    if email in dict_of_users and valid == True:
        session['email'] = email
        # this line is relevant for CRUD operations made to your clients database
        session['unique_id_number'] = user[0]
        return redirect('/home')
    else:
        return redirect('/')

# This is the home screen for when you get in 
@app.route('/home')
def logged_in():
    if session:
        result = database_connect('SELECT client_id, user_id, client_name, company, phone, email, suburb, status FROM clients', [])
        list_of_client_dicts = []
# reformatting my SQL call results, so that I can access them more easily
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
        
        # print (list_of_client_dicts)
        return render_template('home.html', list_of_client_dicts=list_of_client_dicts)
    else:
        return redirect('/')
# defining a new app route for when I want to find out more about a certain person.  
@app.route('/home/<id>')
def findmore(id):
    # print(id)
    result = database_connect('SELECT client_id, user_id, client_name, company, phone, email, suburb, status FROM clients WHERE client_id = %s', [id])
    # print(result)
    return render_template('more.html', result=result)
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
    phone_number = int(phone)
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


# just creating a little log out page now that will redirect me to log in. 
@app.route('/logout')
def clear_and_logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)