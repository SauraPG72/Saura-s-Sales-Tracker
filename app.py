from flask import Flask, render_template, request, session, redirect
import psycopg2
import bcrypt
app = Flask(__name__)
import os
# for making this relevant to my Heroku
DATABASE_URL = os.environ.get('DATABASE_URL', 'dbname=project2')
SECRET_KEY = os.environ.get('SECRET_KEY', 'kdcnbiowe913827fd')
app.config['SECRET_KEY'] = SECRET_KEY

# connect to database code
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
        session['unique_id_number'] = '789'
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
        
        print (list_of_client_dicts)
        return render_template('home.html', list_of_client_dicts=list_of_client_dicts)
    else:
        return redirect('/')
# defining a new app route for when I want to find out more about a certain person.  
@app.route('/home/<id>')
def findmore(id):
    print(id)
    result = database_connect('SELECT client_id, user_id, client_name, company, phone, email, suburb, status FROM clients WHERE client_id = %s', [id])
    print(result)
    return render_template('more.html', result=result)


# just creating a little log out page now that will redirect me to log in. 
@app.route('/logout')
def clear_and_logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)