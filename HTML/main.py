import os
import re
import datetime
from flask import Flask, render_template, session, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, BooleanField, DateTimeField,
                     RadioField, SelectField, TextAreaField, DecimalField)
from flask_wtf.file import FileField, FileAllowed, FileRequired, FileSize
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import LargeBinary
import boto3
from werkzeug.utils import secure_filename


# ###
# GRAB ACCESS_KEY and SECRET_KEY FROM GITHUB. DO NOT COMMIT TO GITHUB WITH ACCESS KEYS IN CODE
# ACCESS_KEY =""
# SECRET_KEY =""
AWS_REGION = "us-east-2"

#artvisionbucket

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
    userName = StringField(validators = [DataRequired()]) 
    profilePhoto = FileField('Profile Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png']), FileSize(max_size=2 * 1024 * 1024, message='No photos larger than 2MB.')])
    bio = TextAreaField()
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
    email = db.Column(db.Text) 
    userName = db.Column(db.Text)
    password = db.Column(db.Text)
    bio = db.Column(db.Text)
    profilePhotoLink = db.Column(db.Text)

    def __init__(self, firstName, lastName, email, userName, password, bio, profilePhotoLink):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.userName = userName
        self.password = password
        self.bio = bio
        self.profilePhotoLink = profilePhotoLink

    def __repr__(self):
        return f"<User {self.userName}>"


class Artwork(db.Model):
    __tablename__="artworks"

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(80), nullable = False)
    description = db.Column(db.String(120), nullable = False)
    price = db.Column(db.Float, nullable = True)
    status = db.Column(db.String(20), nullable = True)
    url = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)

    def __init__(self, title, description, price, status, url, user_id):
        self.title = title
        self.description = description
        self.price = price
        self.status = status
        self.url = url
        self.user_id = user_id

    def __repr__(self):
        return f"<Artwork {self.title}>"

with app.app_context():
    # Create the tables (if not already created)
    db.create_all()

success = False # Login variable

@app.route('/')
def index():
    return render_template('homepage.html')

@app.route('/loginPage', methods = ['GET', 'POST'])
def loginPage():
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
            return redirect(url_for('userProfile', user_id=user.id)) #User's home page
        else:
            error = "Incorrect Login Info"

    return render_template ('loginPage.html', form=form, error=error if 'error' in locals() else None)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/add", methods = ["POST"])
def add():
    genericPhotoLink = 'image/profile_photo.jpeg'

    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    confirmpassword = request.form.get("confirmpassword")
    bio = request.form.get("bio")
    f = request.files["file"]
    # filename = f.filename.split("\\")[-1]
    filename = f"{username}profilepicture.{f.filename.split('.')[-1]}"

    emailCheck = User.query.filter_by(email=email).first()
    if emailCheck: # If email already exists in database
        error = "The email you entered is already taken."
        return render_template ('register.html', error=error)
    
    userNameCheck = User.query.filter_by(userName=username).first()
    if userNameCheck: # If email already exists in database
        error = "The username you entered is already taken."
        return render_template ('register.html', error=error)

    if not passwordValidation(password):
        error = "Password must contain at least one capital letter, one lowercase letter, and end with a number."
        return render_template('register.html', error=error)
    
    if password != confirmpassword:
        error = "Passwords do not match."
        return render_template('register.html', error=error)

    f.save(secure_filename(filename))

    client = boto3.client(
        's3',
        aws_access_key_id = ACCESS_KEY,
        aws_secret_access_key = SECRET_KEY,
        region_name=AWS_REGION
        )
    client.upload_file(filename,"artvisionbucket", "profilephoto/" +filename)
    url = client.generate_presigned_url("get_object",
        Params={
            "Bucket":"artvisionbucket",
            "Key":"profilephoto/"+ filename
        },
        ExpiresIn=3600)

    os.remove(filename)

    newUser = User(firstName=firstname, lastName=lastname, email=email, 
        userName=username, password=password, bio=bio, profilePhotoLink=url)

    db.session.add(newUser)
    db.session.commit()
    return redirect('loginPage')
    # return redirect("/")


@app.route('/userProfile/<int:user_id>')
def userProfile(user_id): 
    if success and 'user_id' in session and session['user_id'] == user_id: # 1st person profile visit
        user = User.query.get(user_id)
        artworks = Artwork.query.filter_by(user_id=user_id).all()
        
        return render_template ('userProfile.html', user=user, isUsersProfile=True, artworks=artworks)

    # elif success and 'user_id' not in session:
    else: # 3rd person profile visit
        user = User.query.get(user_id)
        artworks = Artwork.query.filter_by(user_id=user_id).all()

        return render_template('userProfile.html', user=user, isUsersProfile=False, artworks=artworks)    

    # else:
    #     return redirect(url_for('error404'))
    
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
@app.route('/uploadPage/<int:user_id>', methods = ['GET', 'POST'])
def uploadPage(user_id):
    user = User.query.get(user_id)
    return render_template('upload.html', user=user, user_id=user_id)

@app.route("/addArt/<int:user_id>", methods = ["POST"])
def addArt(user_id):
    user = User.query.get(user_id)

    title = request.form.get("title")
    description = request.form.get("description")
    price = request.form.get("price")
    status = request.form.get("status")

    f = request.files["file"]
    filename = f.filename.split("\\")[-1]
    f.save(secure_filename(filename))

    client = boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=AWS_REGION
    )

    # Upload the file to S3 bucket
    client.upload_file(filename, "artvisionbucket", "artgallery/" + filename)
    url = client.generate_presigned_url("get_object",
        Params={
            "Bucket":"artvisionbucket",
            "Key":"artgallery/"+ filename
        },
        ExpiresIn=3600)
    os.remove(filename)
    newArt = Artwork(title =title, description=description, price=price, status=status, url=url, user_id=user_id)
    db.session.add(newArt)
    db.session.commit()
    return redirect(url_for('userProfile', user_id=user_id))

# @app.route('/uploadPage/<int:user_id>', methods = ['GET', 'POST'])
# def uploadPage(user_id):
#     user = User.query.get(user_id)

#     form = UploadForm()
#     if form.validate_on_submit():
#         if form.submit.data:
#             # Save the form data as 'Published'
#             f = form.fileinput.data
#             filename = secure_filename(f.filename)
#             artwork_url = "https://artvisionbucket/" + filename
#             return 'Artwork saved'
#         elif form.saveDraft.data:
#             # Save the form data as 'draft'
#             return 'Artwork saved as draft'
#     return render_template('upload.html', user=user, form=form)

#Selling Page
@app.route('/sellingPage/<int:user_id>', methods=['GET', 'POST'])
def sellingPage(user_id):
    user = User.query.get(user_id)
    
    form = SellingForm()
    if form.validate_on_submit():
        if form.submit.data:
            # Save the form data as 'Published'
            return 'Artwork saved'
        elif form.saveDraft.data:
            # Save the form data as 'draft'
            return 'Artwork saved as draft'
    return render_template('selling.html', user=user, form=form)

@app.route('/error404')
def error404():
    return render_template ('error404.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
    # app.run(debug=True)

#home page or domain is locally represented as http://127.0.0.1:5000/
# to create multiple pages we will use decorators;
#  @app.route("/another-page")







# @app.route('/registrationPage', methods = ['GET', 'POST'])
# def registrationPage():
#     form = RegistrationForm()

#     genericPhotoLink = 'image/profile_photo.jpeg'

#     if form.validate_on_submit():
#         firstNameInput = form.firstName.data
#         lastNameInput = form.lastName.data
#         emailInput = form.email.data
#         passwordInput = form.password.data
#         confirmPasswordInput = form.confirmPassword.data
#         userNameInput = form.userName.data
#         # profilePhotoInput = form.profilePhoto.data
#         bioInput = form.bio.data
#         # profilePhotoInput = form.profilePhoto.data

#         f = request.files["file"]
#         filename = f.filename.split("\\")[-1]
#         f.save(secure_filename(filename))


#         client = boto3.client(
#             's3',
#             aws_access_key_id = ACCESS_KEY,
#             aws_secret_access_key = SECRET_KEY,
#             region_name=AWS_REGION
#             )
#         client.upload_file(filename,"artvisionbucket", "images/" +filename)

#         # else:
#         #     profile_Photo_Link = genericPhotoLink           


#         emailCheck = User.query.filter_by(email=emailInput).first()
#         if emailCheck: # If email already exists in database
#             error = "The email you entered is already taken."
#             return render_template ('registrationPage.html', form=form, error=error)
        
#         userNameCheck = User.query.filter_by(userName=userNameInput).first()
#         if userNameCheck: # If email already exists in database
#             error = "The username you entered is already taken."
#             return render_template ('registrationPage.html', form=form, error=error)

#         if not passwordValidation(passwordInput):
#             error = "Password must contain at least one capital letter, one lowercase letter, and end with a number."
#             return render_template('registrationPage.html', form=form, error=error)
        
#         if passwordInput != confirmPasswordInput:
#             error = "Passwords do not match."
#             return render_template('registrationPage.html', form=form, error=error)

#         newUser = User(firstName=firstNameInput, lastName=lastNameInput, email=emailInput, 
#             userName=userNameInput, password=passwordInput, bio=bioInput, profilePhotoLink=genericPhotoLink)

#         db.session.add(newUser)
#         db.session.commit()
#         return redirect(url_for('loginPage'))
    
#     return render_template ('registrationPage.html', form=form)