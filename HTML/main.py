import os
import re
import datetime
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, BooleanField, DateTimeField,
                     RadioField, SelectField, TextAreaField, DecimalField)
from flask_wtf.file import FileField, FileAllowed, FileRequired, FileSize
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import LargeBinary, or_
import boto3
from werkzeug.utils import secure_filename
import random
from dotenv import load_dotenv

load_dotenv()

# ###
# GRAB ACCESS_KEY and SECRET_KEY FROM DISCORD. DO NOT COMMIT TO GITHUB WITH ACCESS KEYS IN CODE
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")


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
    client = boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=AWS_REGION
    )

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
    client = boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=AWS_REGION
    )

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
    profilePhoto = FileField('Profile Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png']), FileSize(max_size=2 * 1024 * 1024, message='No photos larger than 2MB.'),DataRequired()])
    bio = TextAreaField()
    pronouns = SelectField('Choose your pronouns', choices=[('option1', 'she/her'),('option2', 'he/him'), ('option3', 'they/them'), ('option4', 'she/they'), ('option5', 'he/they'), ('option6', 'any pronouns')])
    title = SelectField('Choose a title', choices=[('title1', 'Professional'), ('title2', 'Student'), ('title3', 'Hobbyist')])
    submit = SubmitField('Sign Up')

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


class CommentForm(FlaskForm):
    text = StringField()
    submit = SubmitField("Comment")

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
    price = db.Column(db.Float, nullable = True)
    status = db.Column(db.String(20), nullable = True)
    url = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    uploadDate = db.Column(db.DateTime)


    def __init__(self, title, description, price, status, url, user_id, uploadDate):
        self.title = title
        self.description = description
        self.price = price
        self.status = status
        self.url = url
        self.user_id = user_id
        self.uploadDate = uploadDate

    def __repr__(self):
        return f"<Artwork {self.title}>"
    

class Comment(db.Model):
    __tablename__="comments"
    id = db.Column(db.Integer, primary_key=True)
    artwork_id = db.Column(db.Integer)
    text = db.Column(db.String(140))
    author = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime(), index=True)

    def __init__(self, artwork_id, text, author, timestamp):
        self.artwork_id = artwork_id
        self.text = text
        self.author = author
        self.timestamp = timestamp

    def __repr__(self):
        return f"<Comment {self.text}>"

with app.app_context():
    # Create the tables (if not already created)
    db.create_all()

success = False # Login variable


@app.route('/')
def index():
    all_art = []
    for art in Artwork.query.all():
        all_art.append(art.url)

    return render_template('homepage.html', all_art=all_art)

@app.route('/loginPage', methods = ['GET', 'POST'])
def loginPage():
    form = LoginForm()
    if form.validate_on_submit():
        userIdentity = form.userIdentity.data
        passwordInput = form.password.data

        user = User.query.filter((User.userName==userIdentity) | (User.email==userIdentity)).first()
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

    client = boto3.client(
        's3',
        aws_access_key_id = ACCESS_KEY,
        aws_secret_access_key = SECRET_KEY ,
        region_name=AWS_REGION
        )
    client.upload_file(filename,"artvisionbucket", "profilephoto/"+ username + "/" +filename)
    url = client.generate_presigned_url("get_object",
        Params={
            "Bucket":"artvisionbucket",
            "Key":"profilephoto/"+ username + "/" +filename
        },
       )

    os.remove(filename)

    newUser = User(name=name, email=email, 
        userName=username, password=password, bio=bio, profilePhotoLink=url, pronouns=pronouns, title=title, registrationDate=datetime.date.today())

    db.session.add(newUser)
    db.session.commit()
    return redirect('loginPage')
    # return redirect("/")


@app.route('/user/<int:user_id>')
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

@app.route('/explore')
def explore():
    if (session['logged_in'] == True):
        artworks = Artwork.query.all()
        random.shuffle(artworks)
        user = User.query.get(session['user_id'])
        return render_template('explore.html', artworks=artworks, user=user, userLoggedIn = True)
    else:
        artworks = Artwork.query.all()
        random.shuffle(artworks)
        return render_template('explore.html',artworks=artworks, userLoggedIn = False)

@app.route('/artwork/<int:artwork_id>', methods=["GET", "POST"])
def artworkDetails(artwork_id):
    form=CommentForm()
    artwork = Artwork.query.get(artwork_id)
    artist = User.query.get(artwork.user_id)
    user = User.query.get(session['user_id'])
    comments = Comment.query.filter(artwork_id==artwork.id).all()

    if not artwork:
        # Handle the case if the artwork with the given ID doesn't exist
        # For example, you can return an error page or redirect to the Explore page
        return render_template('error.html', message='Artwork not found.')
    
    if request.method == 'POST':
        text = request.form.get("text")
        newComment = Comment(artwork_id=artwork_id, text=text, author=user.userName, timestamp=datetime.date.today())

        db.session.add(newComment)
        db.session.commit()
        return render_template ('artworkDetails.html', artwork=artwork, user=user, artist=artist, form=form, comments=comments)

    return render_template('artworkDetails.html', artwork=artwork, user=user, artist=artist, form=form, comments=comments)


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
        aws_access_key_id= ACCESS_KEY,
        aws_secret_access_key= SECRET_KEY,
        region_name=AWS_REGION
    )

    # Upload the file to S3 bucket
    client.upload_file(filename, "artvisionbucket", "artgallery/" +str(user.userName)+"/"+ filename)
    url = client.generate_presigned_url("get_object",
        Params={
            "Bucket":"artvisionbucket",
            "Key":"artgallery/" +str(user.userName)+"/"+ filename
        },
        )
    os.remove(filename)
    newArt = Artwork(title =title, description=description, price=price, status=status, url=url, user_id=user_id, uploadDate=datetime.date.today())
    db.session.add(newArt)
    db.session.commit()
    return redirect(url_for('userProfile', user_id=user_id))

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

#Upload File Page 
@app.route('/deletePage/<int:user_id>', methods = ['GET', 'POST'])
def deletePage(user_id):
    user = User.query.get(user_id)
    artworks = Artwork.query.filter_by(user_id=user_id).all()
    return render_template('deleteArt.html', user=user, user_id=user_id, artworks=artworks)

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
        return redirect(url_for('userProfile', user_id=user_id))
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

    for artwork in artworks:
        delete_artwork_from_s3(artwork.url)

    for artwork in artworks:
        db.session.delete(artwork)

    db.session.delete(user)  
    db.session.commit()

    session['logged_in'] = False
    session.pop('user_id', None)

    return redirect(url_for('explore'))


@app.route('/deleteComment/<int:comment_id>/<int:artwork_id>')
def deleteComment(comment_id, artwork_id):
    form=CommentForm()
    artwork = Artwork.query.get(artwork_id)
    artist = User.query.get(artwork.user_id)
    user = User.query.get(session['user_id'])
    Comment.query.filter_by(id=comment_id).delete()
    comments = Comment.query.filter(artwork_id==artwork.id).all()

    db.session.commit()
    return redirect(url_for('artworkDetails', artwork=artwork, user=user, artist=artist, form=form, comments=comments, artwork_id=artwork_id))

#Routes for user galleries
@app.route('/<option>/<int:user_id>')
def gallery(option, user_id):
    user = User.query.get(user_id)
    if option == 'gallery':
        artworks = Artwork.query.filter_by(user_id=user_id).all()
        serialized_artworks = {artwork.id: {"id": artwork.id, "title": artwork.title, "price": artwork.price, "url": artwork.url} for artwork in artworks}
        return jsonify(serialized_artworks)
    # elif option == 'favorites':
    #     #get favorites
    # elif option == 'shop':
    #     #get selling items


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
    # app.run(debug=True)

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