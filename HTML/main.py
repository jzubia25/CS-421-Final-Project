import os
import re
import datetime
import random
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, BooleanField, DateTimeField,
                     RadioField, SelectField, TextAreaField, DecimalField)
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import LargeBinary, func, desc
import boto3
from werkzeug.utils import secure_filename
import random
from dotenv import load_dotenv
import requests # need to pip install requests
import json
from json import dumps
from sqlalchemy.orm import class_mapper

load_dotenv()

# ###
# GRAB ACCESS_KEY and SECRET_KEY FROM DISCORD. DO NOT COMMIT TO GITHUB WITH ACCESS KEYS IN CODE
# ACCESS_KEY = os.getenv("ACCESS_KEY")
# SECRET_KEY = os.getenv("SECRET_KEY")
# AWS_REGION = os.getenv("AWS_REGION")
ACCESS_KEY ="AKIA6IBZYP2JKTBDBS2X"
SECRET_KEY ="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"
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

client = boto3.client(
    's3',
    aws_access_key_id = ACCESS_KEY,
    aws_secret_access_key = SECRET_KEY ,
    region_name=AWS_REGION
    )


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

def delete_photo_from_s3(photo_url):
    if not photo_url:
        return
    url_parts = photo_url.split("/")

    # Get the elements we need from the URL parts
    userName = url_parts[4]
    file_name = url_parts[-1]
    file_name_parts = file_name.split("?")
    fileName = file_name_parts[0]

    # print("User name:", userName)
    # print("File name:", fileName)
  
    # Create a Boto3 client for S3
    # client = boto3.client(
    #     's3',
    #     aws_access_key_id=ACCESS_KEY,
    #     aws_secret_access_key=SECRET_KEY,
    #     region_name=AWS_REGION
    # )

    # s3 = boto3.resource(        
    #     's3',
    #     aws_access_key_id=ACCESS_KEY,
    #     aws_secret_access_key=SECRET_KEY,
    #     region_name=AWS_REGION
    # )
    # Currently not working!!!
    try:
        client.delete_object(Bucket="artvisionbucket", Key="profilephoto/"+ userName + "/" +fileName)
        # s3.Object("artvisionbucket", "profilephoto/" + filename).delete()
        print(f"Photo {fileName} deleted from S3 bucket")
    except Exception as e:
        print(f"Error deleting photo {fileName} from S3 bucket: {e}")


def delete_artwork_from_s3(artwork_url):
    if not artwork_url:
        return
    
    url_parts = artwork_url.split("/")

    # Get the elements we need from the URL parts
    userName = url_parts[4]
    file_name = url_parts[-1]
    file_name_parts = file_name.split("?")
    fileName = file_name_parts[0]
    # Create a Boto3 client for S3
    # client = boto3.client(
    #     's3',
    #     aws_access_key_id=ACCESS_KEY,
    #     aws_secret_access_key=SECRET_KEY,
    #     region_name=AWS_REGION
    # )

    try:
        client.delete_object(Bucket="artvisionbucket", Key="artgallery/" + userName +"/"+ fileName)
        print(f"Artwork {fileName} deleted from S3 bucket")
    except Exception as e:
        print(f"Error deleting artwork {fileName} from S3 bucket: {e}")

class LoginForm(FlaskForm):
    userIdentity = StringField(validators = [DataRequired()])
    password = StringField(validators = [DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    name = StringField(validators = [DataRequired()])
    email = StringField(validators = [DataRequired()])
    password = StringField(validators = [DataRequired()])
    confirmPassword = StringField(validators = [DataRequired()])
    userName = StringField(validators = [DataRequired()]) 
    #profilePhoto = FileField('Profile Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png']), FileSize(max_size=2 * 1024 * 1024, message='No photos larger than 2MB.'),DataRequired()])
    bio = TextAreaField()
    pronouns = SelectField('Choose your pronouns', choices=[('option1', 'she/her'),('option2', 'he/him'), ('option3', 'they/them'), ('option4', 'she/they'), ('option5', 'he/they'), ('option6', 'any pronouns')])
    title = SelectField('Choose a title', choices=[('title1', 'Professional'), ('title2', 'Student'), ('title3', 'Hobbyist')])
    submit = SubmitField('Sign Up')

#Upload File Form
class UploadForm(FlaskForm):
    title = StringField('Title', validators = [DataRequired(), Length(max=150)])
    fileInput = FileField('Upload File', validators = [FileRequired(), FileAllowed(['png', 'jpg', 'jpeg', 'gif'])])
    description = TextAreaField('Artwork Description', validators = [DataRequired(), Length(max=400)])
    category = SelectField('Select artwork category', validators = [DataRequired()], choices=[('option1', 'Traditional Art'),('option2', 'Digital Art'), ('option3', 'Mixed Media'), ('option4', 'Graphic Design'), ('option5', 'Photography'), ('option6', 'Comics'), ('option7', 'Fan Art'), ('option8', 'Other')])
    saveDraft = SubmitField('Save Draft')
    submit = SubmitField('Submit')


#Selling Form inherits from UploadForm
class SellingForm(UploadForm):
    price = DecimalField('Price', validators=[DataRequired()])


class CommentForm(FlaskForm):
    text = StringField()
    submit = SubmitField("Comment")


def serialize(model):
    columns = [c.key for c in class_mapper(model.__class__).columns]
    return dict((c, getattr(model, c)) for c in columns) 

class User(db.Model):
    __tablename__="users"

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text)
    email = db.Column(db.Text) 
    userName = db.Column(db.Text)
    password = db.Column(db.Text)
    bio = db.Column(db.Text)
    profilePhotoLink = db.Column(db.Text)
    pronouns = db.Column(db.Text)
    title = db.Column(db.Text)
    registrationDate = db.Column(db.DateTime)

    def __init__(self, name, email, userName, password, bio, profilePhotoLink, pronouns, title, registrationDate):
        self.name = name
        self.email = email
        self.userName = userName
        self.password = password
        self.bio = bio
        self.profilePhotoLink = profilePhotoLink
        self.pronouns = pronouns
        self.title = title
        self.registrationDate = registrationDate

    def __repr__(self):
        return f"<User {self.userName}>"


class Artwork(db.Model):
    __tablename__="artworks"

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(80), nullable = False)
    description = db.Column(db.String(120), nullable = False)
    category = db.Column(db.String(32))
    price = db.Column(db.Float, nullable = True)
    status = db.Column(db.String(20), nullable = True)
    url = db.Column(db.Text)
    artist = db.Column(db.String(32))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    uploadDate = db.Column(db.DateTime)
    shop_item = db.Column(db.Boolean, default=False)


    def __init__(self, title, description, category, price, status, url, artist, user_id, uploadDate, shop_item):
        self.title = title
        self.description = description
        self.category = category
        self.price = price
        self.status = status
        self.url = url
        self.artist = artist
        self.user_id = user_id
        self.uploadDate = uploadDate
        self.shop_item = shop_item

    def __repr__(self):
        return f"<Artwork {self.title}>"


class Comment(db.Model):
    __tablename__="comments"
    id = db.Column(db.Integer, primary_key=True)
    artwork_id = db.Column(db.Integer)
    text = db.Column(db.String(140))
    profile_pic = db.Column(db.Text)
    author = db.Column(db.String(32))
    author_id = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(), index=True)

    def __init__(self, artwork_id, text, profile_pic, author, author_id, timestamp):
        self.artwork_id = artwork_id
        self.text = text
        self.profile_pic = profile_pic
        self.author = author
        self.author_id = author_id
        self.timestamp = timestamp

    def __repr__(self):
        return f"<Comment {self.text}>"

with app.app_context():
    # Create the tables (if not already created)
    db.create_all()

# success = False # Login variable


@app.route('/')
def index():
    all_art = ["https://images.unsplash.com/photo-1690737213782-1e957257abc9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=726&q=80",
        "https://images.unsplash.com/photo-1690509118327-5ee97f3764b3?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1740&q=80",
        "https://images.unsplash.com/photo-1690652067906-f52dcffa0ab9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2532&q=80",
        "https://images.unsplash.com/photo-1690565595343-ad4186d2f262?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=774&q=80",
        "https://images.unsplash.com/photo-1690615497820-dbedbfb47dd1?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=774&q=80",
        "https://images.unsplash.com/photo-1690567614925-eb1954507d87?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1858&q=80",
        "https://images.unsplash.com/photo-1690397684550-96f2381f1c65?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=774&q=80",
        "https://images.unsplash.com/photo-1690520847807-0fe664e51973?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=762&q=80"]
    
    all_art_objects = []


    for art in Artwork.query.all():
        all_art.append(art.url)
        all_art_objects.append(serialize(art))

    random.shuffle(all_art)

    return render_template('homepage.html', all_art=all_art, all_art_objects=all_art_objects)

@app.route('/loginPage', methods = ['GET', 'POST'])
def loginPage():
    form = LoginForm()
    if form.is_submitted() and form.validate():
        userIdentity = form.userIdentity.data
        passwordInput = form.password.data

        user = User.query.filter((User.userName==userIdentity) | (User.email==userIdentity)).first()
        if user and user.password==passwordInput:
            # global success 
            # success = True
            session['logged_in'] = True
            session['user_id'] = user.id
            session['cart'] = {}
            return redirect(url_for('userProfile', user_id=user.id)) #User's home page
        else:
            error = "Incorrect Login Info"
    all_art = ["https://images.unsplash.com/photo-1690737213782-1e957257abc9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=726&q=80",
    "https://images.unsplash.com/photo-1690509118327-5ee97f3764b3?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1740&q=80",
    "https://images.unsplash.com/photo-1690652067906-f52dcffa0ab9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2532&q=80",
    "https://images.unsplash.com/photo-1690565595343-ad4186d2f262?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=774&q=80",
    "https://images.unsplash.com/photo-1690615497820-dbedbfb47dd1?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=774&q=80",
    "https://images.unsplash.com/photo-1690567614925-eb1954507d87?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1858&q=80",
    "https://images.unsplash.com/photo-1690397684550-96f2381f1c65?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=774&q=80",
    "https://images.unsplash.com/photo-1690520847807-0fe664e51973?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=762&q=80"]

    all_art_objects = []

    for art in Artwork.query.all():
        all_art.append(art.url)
        all_art_objects.append(serialize(art))

    random.shuffle(all_art)

    return render_template ('loginPage.html', form=form, error=error if 'error' in locals() else None, all_art=all_art, all_art_objects=all_art_objects)

@app.route("/register")
def register():
    all_art = ["https://images.unsplash.com/photo-1690737213782-1e957257abc9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=726&q=80",
    "https://images.unsplash.com/photo-1690509118327-5ee97f3764b3?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1740&q=80",
    "https://images.unsplash.com/photo-1690652067906-f52dcffa0ab9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2532&q=80",
    "https://images.unsplash.com/photo-1690565595343-ad4186d2f262?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=774&q=80",
    "https://images.unsplash.com/photo-1690615497820-dbedbfb47dd1?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=774&q=80",
    "https://images.unsplash.com/photo-1690567614925-eb1954507d87?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1858&q=80",
    "https://images.unsplash.com/photo-1690397684550-96f2381f1c65?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=774&q=80",
    "https://images.unsplash.com/photo-1690520847807-0fe664e51973?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=762&q=80"]

    all_art_objects = []

    for art in Artwork.query.all():
        all_art.append(art.url)
        all_art_objects.append(serialize(art))

    random.shuffle(all_art)

    return render_template("register.html", all_art=all_art, all_art_objects=all_art_objects)

# Adds
@app.route("/add", methods = ["POST"])
def add():
    genericPhotoLink = 'image/profile_photo.jpeg'

    name = request.form.get("name")
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    confirmpassword = request.form.get("confirmpassword")
    bio = request.form.get("bio")
    f = request.files["file"]
    pronouns = request.form.get("pronouns")
    title = request.form.get("title")
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
    
    # if ' ' in filename:
    #     error = "photo name cannot contain a space."
    #     return render_template('register.html', error=error)        

    f.save(secure_filename(filename))

    # client = boto3.client(
    #     's3',
    #     aws_access_key_id = ACCESS_KEY,
    #     aws_secret_access_key = SECRET_KEY ,
    #     region_name=AWS_REGION
    #     )
    client.upload_file(filename,"artvisionbucket", "profilephoto/"+ username + "/" +filename)
    # presigned_url = client.generate_presigned_url("get_object",
    #     Params={
    #         "Bucket":"artvisionbucket",
    #         "Key":"profilephoto/"+ username + "/" +filename
    #     },
    #    )
    bucket_name = "artvisionbucket"
    s3_key = "profilephoto/" + username + "/" + filename
    url = f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
    os.remove(filename)

    newUser = User(name=name, email=email, 
        userName=username, password=password, bio=bio, profilePhotoLink=url, pronouns=pronouns, title=title, registrationDate=datetime.date.today())

    db.session.add(newUser)
    db.session.commit()
    return redirect('loginPage')
    # return redirect("/")


@app.route('/user/<int:user_id>')
def userProfile(user_id): 
    if session['logged_in'] == True and 'user_id' in session and session['user_id'] == user_id: # 1st person profile visit
        user = User.query.get(user_id)
        artworks = Artwork.query.filter_by(user_id=user_id).all()
        
        return render_template ('userProfile.html', user=user, currentUser=user, isUsersProfile=True, artworks=artworks)

    elif session['logged_in'] == True and 'user_id' not in session:
        # 3rd person profile visit
        currentUser = User.query.get(session['user_id'])
        user = User.query.get(user_id)
        artworks = Artwork.query.filter_by(user_id=user_id).all()

        return render_template('userProfile.html', user=user, currentUser=currentUser, isUsersProfile=False, artworks=artworks)    

    elif session['logged_in'] == False:
        currentUser=None
        user = User.query.get(user_id)
        artworks = Artwork.query.filter_by(user_id=user_id).all()
        return render_template('userProfile.html', user=user, currentUser=currentUser, isUsersProfile=False, artworks=artworks)    

    # else:
    #     return redirect(url_for('error404'))
    

@app.route('/explore/<sort>', methods=["GET", "POST"])
def explore(sort):
    artworks = Artwork.query.all()
    random.shuffle(artworks)

    randomArtwork = random.choice(Artwork.query.all())

    newestArtworks = Artwork.query.order_by(desc(Artwork.uploadDate)).all()


    if 'user_id' in session and session['logged_in'] == True:
        currentUser = User.query.get(session['user_id'])
        user = User.query.get(session['user_id'])

        if request.method == "POST":
            search = request.form.get("search_term")
            print(search)
            artworks = Artwork.query.filter((Artwork.title.like("%"+search+"%")) | (Artwork.artist.like("%"+search+"%")) | (Artwork.description.like("%"+search+"%"))).all()
            
            random.shuffle(artworks)
            return render_template('explore.html', sort=sort, artworks=artworks, newestArtworks=newestArtworks, currentUser=currentUser, randomArtwork=randomArtwork, user=user, userLoggedIn = True)

        else:
            return render_template('explore.html', sort=sort, artworks=artworks, newestArtworks=newestArtworks, currentUser=currentUser, randomArtwork=randomArtwork, user=user, userLoggedIn = True)
    else:
        if request.method == "POST":
            search = request.form.get("search_term")
            random.shuffle(artworks)
            return render_template('explore.html', sort=sort, artworks=artworks, newestArtworks=newestArtworks, randomArtwork=randomArtwork, userLoggedIn = False)
        else:
            return render_template('explore.html', sort=sort, artworks=artworks, newestArtworks=newestArtworks, randomArtwork=randomArtwork, userLoggedIn = False)

#shop page
@app.route('/shop')
def shop():
    artworks = Artwork.query.filter_by(shop_item=True).all()
    random.shuffle(artworks)
    if 'user_id' in session and session['logged_in'] == True:
        currentUser = User.query.get(session['user_id'])
        user = User.query.get(session['user_id'])
        return render_template('shop.html', artworks=artworks, user=user, userLoggedIn = True, currentUser=currentUser)
    
@app.route('/artwork/<int:artwork_id>', methods=["GET", "POST"])
def artworkDetails(artwork_id):
    form=CommentForm()
    artwork = Artwork.query.get(artwork_id)
    print(artwork_id)
    artist = User.query.get(artwork.user_id)

    if 'user_id' not in session:  # add this line
        # handle the case when the user is not logged in
         user = None  # or whatever is appropriate in your case
         userLoggedIn = False  # add this line

    else:
        user = User.query.get(session['user_id'])
        userLoggedIn = True   # add this line

    comments = Comment.query.filter_by(artwork_id = artwork.id).all()
    commentsCount = db.session.execute(Comment.query.filter_by(artwork_id = artwork.id).statement.with_only_columns([func.count()]).order_by(None)).scalar()


    if not artwork:
        return render_template('error.html', message='Artwork not found.')
    
    if request.method == 'POST':
        if user:  # add this line
            text = request.form.get("text")
            newComment = Comment(artwork_id=artwork_id, text=text, author=user.userName, profile_pic=user.profilePhotoLink, author_id=user.id, timestamp=datetime.date.today())

            db.session.add(newComment)
            db.session.commit()
            return redirect(url_for('artworkDetails', artwork=artwork, user=user, currentUser=user, artist=artist, form=form, comments=comments, commentsCount=commentsCount, artwork_id=artwork_id, userLoggedIn=userLoggedIn))

    return render_template('artworkDetails.html', artwork=artwork, user=user, currentUser=user, artist=artist, form=form, comments=comments, commentsCount=commentsCount, userLoggedIn=userLoggedIn)

#Upload File Page 
@app.route('/uploadPage/<int:user_id>', methods = ['GET', 'POST'])
def uploadPage(user_id):
    user = User.query.get(user_id)
    return render_template('upload.html', user=user, user_id=user_id, currentUser=user)

#Upload Comission Page 
@app.route('/sellingPage/<int:user_id>', methods = ['GET', 'POST'])
def sellingPage(user_id):
    user = User.query.get(user_id)
    return render_template('selling.html', user=user, user_id=user_id, currentUser=user)

#Checkout Page
@app.route('/purchasePage/<int:user_id>', methods = ['GET', 'POST'])
def purchasePage(user_id):
    user = User.query.get(user_id)
    return render_template('purchase.html', user=user, user_id=user_id, currentUser=user, cart=session['cart'])

#add to cart
@app.route("/addArt/<int:user_id>", methods = ["POST"])
def addArt(user_id):
    user = User.query.get(user_id)
    artist = user.userName

    title = request.form.get("title")
    description = request.form.get("description")
    category = request.form.get("category")
    price = request.form.get("price")
    status = request.form.get("status")
    shop_item = "price" in request.form

    f = request.files["file"]
    filename = f.filename.split("\\")[-1]
    f.save(secure_filename(filename))

    # client = boto3.client(
    #     's3',
    #     aws_access_key_id= ACCESS_KEY,
    #     aws_secret_access_key= SECRET_KEY,
    #     region_name=AWS_REGION
    # )

    # Upload the file to S3 bucket
    client.upload_file(filename, "artvisionbucket", "artgallery/" +str(user.userName)+"/"+ filename)
    # presigned_url = client.generate_presigned_url("get_object",
    #     Params={
    #         "Bucket":"artvisionbucket",
    #         "Key":"artgallery/" +str(user.userName)+"/"+ filename
    #     },
    #     )

    bucket_name = "artvisionbucket"
    s3_key = f"artgallery/{user.userName}/{filename}"
    url = f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"

    os.remove(filename)
    newArt = Artwork(title =title, description=description, category=category, price=price, status=status, url=url, user_id=user_id, artist=artist, uploadDate=datetime.datetime.now(), shop_item=shop_item)
    db.session.add(newArt)
    db.session.commit()
    return redirect(url_for('userProfile', user_id=user_id))


#add artwork to cart
@app.route("/addCart/<int:artwork_id>", methods = ["POST"])
def addCart(artwork_id):
    artwork = Artwork.query.get(artwork_id) 
    quantity = int(request.form.get('quantity'))
    if not artwork:
        return render_template('error.html', message='Artwork not found.')
    cart = session['cart']

    if str(artwork.id) not in cart:
        cart[str(artwork.id)] = {'quantity': 0,'price': artwork.price,'image_url': artwork.url,'title' : artwork.title,'id' : artwork.id}

    cart[str(artwork.id)]['quantity'] += quantity
    session['cart'] = cart
    return redirect(url_for('artworkDetails', artwork_id=artwork_id))


#delete item from cart
@app.route('/deleteCartItem/<int:artwork_id>')
def deleteCartItem(artwork_id):
    cart = session.get('cart', {})
    if str(artwork_id) in cart:
        del cart[str(artwork_id)]
        session['cart'] = cart
    return redirect(url_for('purchasePage', user_id=session['user_id']))




#Upload File Page 
@app.route('/deletePage/<int:user_id>', methods = ['GET', 'POST'])
def deletePage(user_id):
    user = User.query.get(user_id)
    artworks = Artwork.query.filter_by(user_id=user_id).all()
    return render_template('deleteArt.html', user=user, user_id=user_id, artworks=artworks, currentUser=user)

@app.route("/deleteArt/<int:user_id>", methods = ["GET","POST"])
def deleteArt(user_id):
    user = User.query.get(user_id)
    artworksSelected = request.form.getlist("artworkToDelete")

    
    if request.method == 'POST':
        for artwork_id in artworksSelected:
            artwork = Artwork.query.get(artwork_id)
            filename = (artwork.url).partition(user.userName)[2]
            if artwork:
                client = boto3.client(
                    's3',
                    aws_access_key_id= ACCESS_KEY,
                    aws_secret_access_key= SECRET_KEY,
                    region_name=AWS_REGION
                )
                client.delete_object(Bucket="artvisionbucket", Key="artgallery/" + user.userName +"/"+ filename)
                db.session.delete(artwork)
                
                db.session.commit()
        return redirect(url_for('userProfile', user_id=user_id, currentUser=user))
    else:
        return (redirect(url_for('explore')))
    # Need query to find and delete art from database


@app.route('/error404')
def error404():
    return render_template ('error404.html')

@app.route('/logout')
def logout():
    # session.pop('logged_in', None)
    session['logged_in'] = False
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/deleteAccount')
def deleteAccount():
    user_id = session['user_id']
    user = User.query.get(user_id)
    artworks = Artwork.query.filter_by(user_id=user_id).all()
    comments = Comment.query.filter_by(author_id=user.id).all()

    for artwork in artworks:
        delete_artwork_from_s3(artwork.url)
        db.session.delete(artwork)

    for comment in comments:
        db.session.delete(comment)

    db.session.delete(user)  
    db.session.commit()

    session['logged_in'] = False
    session.pop('user_id', None)

    return redirect(url_for('explore', sort='random'))


@app.route('/deleteComment/<int:comment_id>/<int:artwork_id>')
def deleteComment(comment_id, artwork_id):
    form=CommentForm()
    artwork = Artwork.query.get(artwork_id)
    artist = User.query.get(artwork.user_id)
    user = User.query.get(session['user_id'])
    Comment.query.filter_by(id=comment_id).delete()
    comments = Comment.query.filter(artwork_id==artwork.id).all()

    db.session.commit()
    return redirect(url_for('artworkDetails', artwork=artwork, user=user, currentUser=user, artist=artist, form=form, comments=comments, artwork_id=artwork_id))

#Routes for user galleries
@app.route('/<option>/<int:user_id>')
def gallery(option, user_id):
    user = User.query.get(user_id)
    if option == 'gallery':
        artworks = Artwork.query.filter_by(user_id=user_id, shop_item=False).all()
        serialized_artworks = {artwork.id: {"id": artwork.id, "title": artwork.title, "price": artwork.price, "url": artwork.url} for artwork in artworks}
        return jsonify(serialized_artworks)
    elif option == 'shop':
        artworks = Artwork.query.filter_by(user_id=user_id, shop_item=True).all()
        serialized_artworks = {artwork.id: {"id": artwork.id, "title": artwork.title, "price": artwork.price, "url": artwork.url} for artwork in artworks}
        return jsonify(serialized_artworks)
    # elif option == 'shop':
    #     #get selling items

@app.route('/editPage/<int:user_id>', methods = ['GET', 'POST'])
def editPage(user_id):
    user = User.query.get(user_id)
    artworks = Artwork.query.filter_by(user_id=user_id).all()
    return render_template('editAccount.html', user=user, user_id=user_id, artworks=artworks, currentUser=user)

@app.route("/editAccount/<int:user_id>", methods = ["GET","POST"])
def editAccount(user_id):
    user = User.query.get(user_id)
    artworks = Artwork.query.filter_by(user_id=user_id).all()
    update = False
    
    email = request.form.get("currentemail")
    password = request.form.get("currentpassword")
    username = request.form.get("currentusername")

    newUsername = request.form.get("newusername")
    confirmNewUsername = request.form.get("confirmnewusername")

    newEmail = request.form.get("newemail")
    confirmNewEmail = request.form.get("confirmnewemail")

    newPassword = request.form.get("newpassword")
    confirmNewPassword = request.form.get("confirmnewpassword")

    user = User.query.filter_by(id=user_id).first()
    passwordInDatabase = user.password
    emailInDatabase = user.email
    userNameInDatabase = user.userName

    userNameCheck = User.query.filter_by(userName=newUsername).first()
    # print(userNameCheck)
    # checks database for email matching current user.
    if email != emailInDatabase: 
        error = "incorrect email"
        return render_template('editAccount.html', user=user, user_id=user_id, artworks=artworks, currentUser=user, error=error) 
    # checks database for password matching current user.
    if password != passwordInDatabase:
        error = "incorrect password"
        return render_template('editAccount.html', user=user, user_id=user_id, artworks=artworks, currentUser=user, error=error)
    # checks database for username matching current user.
    if username != userNameInDatabase:
        error = "incorrect username"
        return render_template('editAccount.html', user=user, user_id=user_id, artworks=artworks, currentUser=user, error=error)
    # makes sure new email matches.
    if newEmail and newEmail != confirmNewEmail:
        error = "new email inputs do not match"
        return render_template('editAccount.html', user=user, user_id=user_id, artworks=artworks, currentUser=user, error=error)
    # makes sure new username matches.
    if newUsername and newUsername != confirmNewUsername:
        error = "new Username inputs do not match"
        return render_template('editAccount.html', user=user, user_id=user_id, artworks=artworks, currentUser=user, error=error)
    # makes sure new password matches and meet requirements.
    if newPassword and newPassword != confirmNewPassword and passwordValidation(newPassword)== False:
        error = "new password inputs do not match or meet password requirements"
        return render_template('editAccount.html', user=user, user_id=user_id, artworks=artworks, currentUser=user, error=error)

    if newUsername and userNameCheck is None:
        user.userName = newUsername

        # setting up client
        # client = boto3.client(
        #     's3',
        #     aws_access_key_id = ACCESS_KEY,
        #     aws_secret_access_key = SECRET_KEY ,
        #     region_name=AWS_REGION
        #     )

        # transferring profile photo to new userName

        # Saving profile photo
        response = requests.get(user.profilePhotoLink)
        url_parts = user.profilePhotoLink.split("/")
        filename = url_parts[-1]

        with open(filename, 'wb') as f:
            f.write(response.content)

        # uploading profile photo
        client.upload_file(filename,"artvisionbucket", "profilephoto/" + user.userName + "/" + filename)
        
        bucket_name = "artvisionbucket"
        s3_key = "profilephoto/" + user.userName + "/" + filename
        url = f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        user.profilePhotoLink = url
        client.delete_object(Bucket="artvisionbucket", Key="profilephoto/" + username +"/"+ filename)
        os.remove(filename)

        for artwork in artworks:
            url = artwork.url
            url_parts = url.split("/")

            url_parts[4] = newUsername
            newUrl = "/".join(url_parts)
            artwork.url = newUrl

            response = requests.get(url)
            filename = url_parts[-1]

            with open(filename, 'wb') as f:
                f.write(response.content)

            client.upload_file(filename,"artvisionbucket", "artgallery/" + user.userName + "/" + filename)
            bucket_name = "artvisionbucket"
            s3_key = "artgallery/" + user.userName + "/" + filename
            url = f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
            client.delete_object(Bucket="artvisionbucket", Key="artgallery/" + username +"/"+ filename)
            os.remove(filename)
            update = True

    if newEmail:
        user.email = newEmail
        update = True
    if newPassword:
        user.password = newPassword
        update = True
    if update == True:
        message = "Information updated"
    if update == False:
        message = "Information unchanged"
    db.session.commit()
    return redirect(url_for('userProfile', user_id=user_id, message=message))
    

if __name__ == '__main__':
    #app.run(host='0.0.0.0',debug=True)
    app.run(debug=True)

#home page or domain is locally represented as http://127.0.0.1:5000/
# to create multiple pages we will use decorators;
#  @app.route("/another-page")


#  REFERENCES
"""
HTML <input type="file">
https://www.w3schools.com/tags/att_input_type_file.asp#:~:text=The%20%3Cinput%20type%3D%22file,tag%20for%20best%20accessibility%20practices!
Flask HTML loops
https://www.geeksforgeeks.org/python-using-for-loop-in-flask/#
https://stackoverflow.com/questions/45167508/flask-template-for-loop-iteration-keyvalue

"""