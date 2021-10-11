from logging import error
from re import A
from flask import Flask, render_template, request,redirect, session
from flask_mail import Message
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import redirect
from flask_session import Session
import smtplib
import os
from dotenv import load_dotenv
load_dotenv() 
from flask import Flask, request, url_for
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from datetime import timedelta
import urllib.request


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///NotesAndPasswordManager.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)

app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=20)

senderEmail = os.getenv("SENDER_EMAIL")
senderPassword = os.getenv("SENDER_PASSWORD")

mail = Mail(app)
s = URLSafeTimedSerializer(os.getenv("VERIFICATION_KEY"))

class PasswordManager(db.Model):
    __tablename__ = 'passwordManager'
    username = db.Column(db.String(200),primary_key=True)
    email = db.Column(db.String(200),nullable=False)
    password = db.Column(db.String(200),nullable=False)
    
class NotesManager(db.Model):
    __tablename__ = 'notesManager'
    sno= db.Column(db.Integer(),primary_key=True)
    username = db.Column(db.String(200),db.ForeignKey(PasswordManager.username),nullable=False)
    title = db.Column(db.String(200),nullable=False)
    desc = db.Column(db.String(500),nullable=False)
    date_created= db.Column(db.DateTime, default=datetime.utcnow)


errors = {0:['success','User Registered Successfully!'],1:['danger','Passwords do not match!'],
          2:['danger','Username has been taken! Please choose new username!'],3:['danger','Invalid Login Credentials!'],
          -1:['no error','blank']}


@app.route("/", methods=['GET','POST'])
def home():   
    return render_template('home_page.html',error=[-1,errors[-1]])

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method=='POST':
        userDetails = request.form
        username = userDetails['regUserName']
        password = userDetails['regPassword']
        confirmPass = userDetails['regConPassword']
        if password!=confirmPass:
            print()
            return render_template("home_page.html",error=[1,errors[1]])

        try:
            newUser = PasswordManager(username=username ,email='',password=password)
            db.session.add(newUser)
            db.session.commit()
            return render_template('home_page.html',error=[0,errors[0]])
        except:
            return render_template('home_page.html',error=[2,errors[2]])
    return render_template('home_page.html',error=[-1,errors[-1]])

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method=='POST':
        userDetails = request.form
        username = userDetails['logUserName']
        password = userDetails['logPassword']
        logUser = PasswordManager.query.filter_by(username=username,password=password).first()
        if logUser:
            print("Login Successful!",username)
            session['username'] = username
            session['email'] = ''
            return redirect('/notesHome')
        else:
            return render_template('home_page.html',error=[3,errors[3]])
    return render_template('home_page.html',error=[-1,errors[-1]])

@app.route("/recovery", methods=['GET','POST'])
def recover():
    if request.method=='POST':
        userDetails = request.form
        newEmail = userDetails['newEmail']
        token = s.dumps(newEmail, salt='email-confirm')
        server = smtplib.SMTP("smtp.gmail.com",587)
        server.starttls()
        server.login(senderEmail,senderPassword)
        SUBJECT = "Confirmation Email for Notes Manager"
        link = url_for('confirm_email', token=token, _external=True)
        link = link+"123"
        TEXT = 'Your link is {}'.format(link)
        TEXT = TEXT + ' \nCopy and Paste this link into the website'
        message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
        server.sendmail(senderEmail,newEmail,message)
        server.quit()
        return render_template('add_recovery.html',email=session['email'],type='success',msg=f'A verification email has been sent to {newEmail}')
    logUser = PasswordManager.query.filter_by(username=session['username']).first()
    return render_template('add_recovery.html',email = logUser.email,type='',msg='')


@app.route('/confirmEmail',methods=['GET','POST'])
def checkEmail():
    if request.method=='POST':
        link = request.form['link']
        length = (len(link)) - 3
        link = link[0:length]
        if link.startswith('http://127.0.0.1:8000/confirm_email/'):
            try:
                return redirect(link)
            except:
                return redirect('/recovery')
        else:
            return render_template('add_recovery.html',email=session['email'],type='danger',msg='Invalid Verification!')  
    return render_template('add_recovery.html',email=session['email'],type='',msg='')

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        newEmail = s.loads(token, salt='email-confirm', max_age=3600)
        username = session['username']
        update_email = PasswordManager.query.filter_by(username=username).update(dict(email=newEmail))
        db.session.commit()
        session['email'] = newEmail
        return render_template('add_recovery.html',email = session['email'],type='success',msg='Email has been added successfully!')
    except:
        return render_template('add_recovery.html',email=session['email'],type='danger',msg='Invalid Verification')
    
@app.route("/notesHome", methods=['GET','POST'])
def display():
    username= session['username']
    allNotes= NotesManager.query.filter_by(username=username).all()
    return render_template('my_notes.html',allNotes=allNotes)

@app.route("/addNote", methods=['GET','POST'])
def add():
    if request.method=='POST':
        username = session['username']
        title=request.form['title']
        desc = request.form['desc']
        newNote = NotesManager(username=username ,title=title, desc=desc)
        db.session.add(newNote)
        db.session.commit()
    return redirect('/notesHome')

@app.route("/deleteNote/<int:sno>")
def delete(sno):
    delNote=NotesManager.query.filter_by(username=session['username'],sno=sno).first()
    db.session.delete(delNote)
    db.session.commit()
    return redirect("/notesHome")

@app.route("/forgotPassword", methods=['GET','POST'])
def forgot():
    if request.method=='POST':
        username = request.form['username']
        frgtUser = PasswordManager.query.filter_by(username=username).first()
        if frgtUser:
            try:
                receiverEmail = frgtUser.email
                server = smtplib.SMTP("smtp.gmail.com",587)
                server.starttls()
                server.login(senderEmail,senderPassword)
                SUBJECT = "Recovery Email for Notes Manager"
                TEXT = f"The password for your Notes Manager is {frgtUser.password}"
                message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
                server.sendmail(senderEmail,receiverEmail,message)
                server.quit()
                return render_template('forgot_user.html',type='success',msg=f"An email has been sent to {frgtUser.email}")
            except:
                return render_template('forgot_user.html',type='danger',msg=f"Email ID {frgtUser.email} does not exist! Please update email-id!")
        else:
            return render_template('forgot_user.html',type='danger',msg='Invalid Username!')
        
    return render_template('forgot_user.html',type='',msg='')
    
    
@app.route("/logout")
def logout():
    session.pop('username', None)
    session.pop('email', None)
    return redirect('/')


if __name__=='__main__':
    db.create_all()
    app.run(debug=True,port=8000)