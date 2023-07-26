import os
import re
from flask import Flask, render_template, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, BooleanField, DateTimeField,
                     RadioField, SelectField, TextAreaField, DecimalField)
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import LargeBinary

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
    profilePhoto = FileField('Profile Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    bio = TextAreaField(validators = [DataRequired()])
    submit = SubmitField('Register Now')

#Upload File Form
class UploadForm(FlaskForm):
    title = StringField('Title', validators = [DataRequired(), Length(max=150)])
    fileInput = FileField('Upload File', validators = [FileRequired(), FileAllowed(['png', 'jpg', 'jpeg', 'gif'])])
    description = TextAreaField('Artwork Description', validators = [DataRequired(), Length(max=400)])
    saveDraft = SubmitField('Save Draft')
    submit = SubmitField('Submit')


#Selling Form inherits from UploadForm
class SellingForm(UploadForm):
    price = DecimalField('Price', validators=[DataRequired()])


class User(db.Model):
    __tablename__="users"

    id = db.Column(db.Integer, primary_key = True)
    firstName = db.Column(db.Text)
    lastName = db.Column(db.Text)
    email = db.Column(db.Text) # Email
    userName = db.Column(db.Text) #Newly added. Needs to be implemented
    password = db.Column(db.Text)
    profilePhoto = db.Column(LargeBinary)

# class Artwork(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     title = db.Column(db.String(80), nullable = False)
#     description = db.Column(db.String(120), nullable = False)
#     price = db.Column(db.Float, nullable = False)
#     status = db.Column(db.String(20), nullable = False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

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
        userNameInput = form.userName.data
        passwordInput = form.password.data

        user = User.query.filter_by(userName=userNameInput).first()
        if user and user.password==passwordInput:
            global success 
            success = True
            session['logged_in'] = True
            session['user_id'] = user.id
            return redirect(url_for('userProfile'))#Needs to be updated to User's home page
        else:
            error = "Incorrect Login Info"

    return render_template ('loginPage.html', form=form, error=error if 'error' in locals() else None)

@app.route('/registrationPage', methods = ['GET', 'POST'])
def registrationPage ():
    form = RegistrationForm()

    if form.validate_on_submit():
        firstNameInput = form.firstName.data
        lastNameInput = form.lastName.data
        emailInput = form.email.data
        passwordInput = form.password.data
        confirmPasswordInput = form.confirmPassword.data
        userNameInput = form.userName.data

        emailCheck = User.query.filter_by(email=emailInput).first()
        if emailCheck: # If email already exists in database
            error = "The email you entered is already taken."
            return render_template ('registrationPage.html', form=form, error=error)
        
        userNameCheck = User.query.filter_by(userName=userNameInput).first()
        if userNameCheck: # If email already exists in database
            error = "The username you entered is already taken."
            return render_template ('registrationPage.html', form=form, error=error)

        if not passwordValidation(passwordInput):
            error = "Password must contain at least one capital letter, one lowercase letter, and end with a number."
            return render_template('registrationPage.html', form=form, error=error)
        
        if passwordInput != confirmPasswordInput:
            error = "Passwords do not match."
            return render_template('registrationPage.html', form=form, error=error)

        newUser = User(firstName=firstNameInput, lastName=lastNameInput, email=emailInput, userName=userNameInput, password=passwordInput)

        db.session.add(newUser)
        db.session.commit()
        return redirect(url_for('loginPage'))
    
    return render_template ('registrationPage.html', form=form)

@app.route('/userProfile')
def userProfile():
    if success:
        return render_template ('userProfile.html')
    else:
        return redirect(url_for('error404'))
    
# @app.route('/profilePage')
# def profilePage():
#     if success:
#         return render_template ('profilePage.html')
#     else:
#         return redirect(url_for('error404'))

@app.route('/explore', methods = ['GET', 'POST'])
def explore():
    return render_template('explore.html')

#Upload File Page 
@app.route('/uploadPage', methods = ['GET', 'POST'])
def uploadPage():
    form = UploadForm()
    if form.validate_on_submit():
        if form.submit.data:
            # Save the form data as 'Published'
            return 'Artwork saved'
        elif form.saveDraft.data:
            # Save the form data as 'draft'
            return 'Artwork saved as draft'
    return render_template('upload.html', form=form)

#Selling Page
@app.route('/sellingPage', methods=['GET', 'POST'])
def sellingPage():
    form = SellingForm()
    if form.validate_on_submit():
        if form.submit.data:
            # Save the form data as 'Published'
            return 'Artwork saved'
        elif form.saveDraft.data:
            # Save the form data as 'draft'
            return 'Artwork saved as draft'
    return render_template('selling.html', form=form)

@app.route('/error404')
def error404():
    return render_template ('error404.html')

if __name__ == '__main__':
    app.run(debug=True)

#home page or domain is locally represented as http://127.0.0.1:5000/
# to create multiple pages we will use decorators;
#  @app.route("/another-page")