from flask import Flask, render_template, request, session, redirect, flash
from werkzeug.security import check_password_hash, generate_password_hash
import pika
import messaging
import os

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']


@app.route('/')
def hello_world():
	return 'Flask works in docker container!'
    
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        passwd = request.form['hashed']
        mesg = messaging.Messaging()
        mesg.send('GETHASH', {'username': username })
        response = mesg.receive()
        if response['success'] != True:
            return "Login failed."
        if check_password_hash(response['hash'], passwd):
            session['username'] = username
            return redirect('/')
        else:
            return "Failed, invalid."
    return render_template('login.html')
    
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        passwd = request.form['hashed']
        #mseg stuff
        mesg = messaging.Messaging()
        mesg.send(
            'REGISTER',
            {
                'username' : username,
                'hashed': generate_password_hash(passwd)
            }
        )
        response = mesg.receive()
        if response['success']:
                session['username'] = username
                return redirect('/')
        else:
                return f"{response['message']}"
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')