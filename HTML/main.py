import os
import re
from flask import Flask, render_template, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, BooleanField, DateTimeField,
                     RadioField, SelectField, TextAreaField)
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__)) 
#__file__ refers to main.py
# abspath -> absolute path -> provides the full directory path

# We render templates by importing the render_template function from flask and 
# returning an .html file from our view function
app = Flask (__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRAC_MODIFICATIONS']=False

app.config['SECRET_KEY'] = 'oursecretkey'

db = SQLAlchemy(app)
Migrate(app,db)

def passwordValidation(PWD):
    regexCapLetter = r'[A-Z]'
    regexLowLetter = r'[a-z]'
    regexEndNumber = r'[0-9]$'
    regexList = [regexCapLetter, regexLowLetter, regexEndNumber]
    count = 0
    for regex in range(0,3):
        match = re.search(regexList[regex],PWD)
        if match:
            count+=1
    if count == 3:
        return True
    else:
        return False

class LoginForm(FlaskForm):
    userName = StringField(validators = [DataRequired()])
    password = StringField(validators = [DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    firstName = StringField(validators = [DataRequired()])
    lastName = StringField(validators = [DataRequired()])
    email = StringField(validators = [DataRequired()])
    password = StringField(validators = [DataRequired()])
    confirmPassword = StringField(validators = [DataRequired()])
    userName = StringField(validators = [DataRequired()]) #Newly added. Needs to be implemented
    submit = SubmitField('Register Now')

class User(db.Model):
    __tablename__="users"

    id = db.Column(db.Integer, primary_key = True)
    firstName = db.Column(db.Text)
    lastName = db.Column(db.Text)
    email = db.Column(db.Text) # Email
    userName = db.Column(db.Text) #Newly added. Needs to be implemented
    password = db.Column(db.Text)

with app.app_context():
    # Create the tables (if not already created)
    db.create_all()

success = False # Login variable

@app.route ('/')
def index ():
    return render_template('homepage.html')

@app.route('/loginPage', methods = ['GET', 'POST'])
def loginPage ():
    form = LoginForm()
    if form.validate_on_submit():
        userName = form.userName.data
        password = form.password.data

        user = User.query.filter_by(userName=userName).first()
        if user and user.password==password:
            global success 
            success = True
            return redirect(url_for('secretPage'))#Needs to be updated to User's home page
        else:
            error = "Incorrect Login Info"

    return render_template ('loginPage.html', form= form, error=error if 'error' in locals() else None)

@app.route('/registrationPage', methods = ['GET', 'POST'])
def registrationPage ():
    form = RegistrationForm()

    if form.validate_on_submit():
        firstName = form.firstName.data
        lastName = form.lastName.data
        email = form.email.data
        password = form.password.data
        confirmPassword = form.confirmPassword.data
        userName = form.userName.data

        emailCheck = User.query.filter_by(email=email).first()
        if emailCheck: # If email already exists in database
            error = "The email you entered is already taken."
            return render_template ('registrationPage.html', form=form, error=error)
        
        userNameCheck = User.query.filter_by(userName=userName).first()
        if userNameCheck: # If username already exists in database
            error = "The username you entered is already taken."
            return render_template ('registrationPage.html', form=form, error=error)

        if not passwordValidation(password):
            error = "Password must contain at least one capital letter, one lowercase letter, and end with a number."
            return render_template('registrationPage.html', form=form, error=error)
        
        if password != confirmPassword:
            error = "Passwords do not match."
            return render_template('registrationPage.html', form=form, error=error)

        newUser = User(firstName=firstName, lastName=lastName, username=email, password=password)

        db.session.add(newUser)
        db.session.commit()
        return redirect(url_for('thankyou'))
    
    return render_template ('registrationPage.html', form=form)


@app.route('/explore', methods = ['GET', 'POST'])
def explore():
    return render_template('explore.html')

# @app.route('/secretPage')
# def secretPage():
#     if success:
#         return render_template ('secretPage.html')
#     else:
#         return redirect(url_for('error404'))

# @app.route('/thankyou')
# def thankyou():
#     return render_template ('thankyou.html')

# @app.route('/error404')
# def error404():
#     return render_template ('error404.html')

if __name__ == '__main__':
    app.run(debug=True)

#home page or domain is locally represented as http://127.0.0.1:5000/
# to create multiple pages we will use decorators;
#  @app.route("/another-page")