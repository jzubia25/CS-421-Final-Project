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


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    transaction_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    buyer_name = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    shipping_address = db.Column(db.Text)

    def __init__(self, buyer_name, amount, shipping_address=None):
        self.buyer_name = buyer_name
        self.amount = amount
        self.shipping_address = shipping_address

    def __repr__(self):
        return f"<Transaction {self.id}>"

with app.app_context():
    # Create the tables (if not already created)
    db.create_all()

@app.route('/')
def index():
    
    all_art = []
    
    all_art_objects = []
    all_user_objects =[]

    for art in Artwork.query.all():
        all_art.append(art.url)
        all_art_objects.append(serialize(art))

    for user in User.query.all():
        all_user_objects.append(serialize(user))

    random.shuffle(all_art)

    return render_template('homepage.html', all_art=all_art, all_art_objects=all_art_objects, all_user_objects=all_user_objects)

@app.route('/loginPage', methods = ['GET', 'POST'])
def loginPage():
    form = LoginForm()
    if form.validate_on_submit():
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
    
    all_art = []

    all_art_objects = []
    all_user_objects = []

    for art in Artwork.query.all():
        all_art.append(art.url)
        all_art_objects.append(serialize(art))

    random.shuffle(all_art)

    for user in User.query.all():
        all_user_objects.append(serialize(user))

    return render_template ('loginPage.html', form=form, error=error if 'error' in locals() else None, all_art=all_art, all_art_objects=all_art_objects, all_user_objects=all_user_objects)

@app.route("/register")
def register():
    all_art = []

    all_art_objects = []
    all_user_objects = []

    for art in Artwork.query.all():
        all_art.append(art.url)
        all_art_objects.append(serialize(art))

    for user in User.query.all():
        all_user_objects.append(serialize(user))

    random.shuffle(all_art)

    return render_template("register.html", all_art=all_art, all_art_objects=all_art_objects, all_user_objects=all_user_objects)

# Adds
@app.route("/add", methods = ["POST"])
def add():
    all_art = []

    all_art_objects = []
    all_user_objects = []
    

    for art in Artwork.query.all():
        all_art.append(art.url)
        all_art_objects.append(serialize(art))

    for user in User.query.all():
        all_user_objects.append(serialize(user))

    random.shuffle(all_art)

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
        return render_template ('register.html', error=error, all_art=all_art, all_art_objects=all_art_objects, all_user_objects=all_user_objects)
    
    userNameCheck = User.query.filter_by(userName=username).first()
    if userNameCheck: # If email already exists in database
        error = "The username you entered is already taken."
        return render_template ('register.html', error=error, all_art=all_art, all_art_objects=all_art_objects, all_user_objects=all_user_objects)

    if not passwordValidation(password):
        error = "Password must contain at least one capital letter, one lowercase letter, and end with a number."
        return render_template('register.html', error=error, all_art=all_art, all_art_objects=all_art_objects, all_user_objects=all_user_objects)
    
    if password != confirmpassword:
        error = "Passwords do not match."
        return render_template('register.html', error=error, all_art=all_art, all_art_objects=all_art_objects, all_user_objects=all_user_objects)

    f.save(secure_filename(filename))

    client.upload_file(filename,"artvisionbucket", "profilephoto/"+ username + "/" +filename)

    bucket_name = "artvisionbucket"
    s3_key = "profilephoto/" + username + "/" + filename
    url = f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
    os.remove(filename)

    newUser = User(name=name, email=email, 
        userName=username, password=password, bio=bio, profilePhotoLink=url, pronouns=pronouns, title=title, registrationDate=datetime.date.today())

    db.session.add(newUser)
    db.session.commit()
    return redirect('loginPage')

@app.route('/user/<int:user_id>')
def userProfile(user_id): 
    if session['logged_in'] == True and 'user_id' in session and session['user_id'] == user_id: # 1st person profile visit
        user = User.query.get(user_id)
        artworks = Artwork.query.filter_by(user_id=user_id).all()
        
        return render_template ('userProfile.html', user=user, currentUser=user, isUsersProfile=True, artworks=artworks)

    elif session['logged_in'] == True and 'user_id' in session and session['user_id'] != user_id:
        # 3rd person profile visit
        currentUser = User.query.get(session['user_id'])
        user = User.query.get(user_id)
        artworks = Artwork.query.filter_by(user_id=user_id).all()

        return render_template('userProfile.html', user=user, currentUser=currentUser, isUsersProfile=False, artworks=artworks)    

    else:
        currentUser=None
        user = User.query.get(user_id)
        artworks = Artwork.query.filter_by(user_id=user_id).all()
        return render_template('userProfile.html', user=user, currentUser=currentUser, isUsersProfile=False, artworks=artworks)    


@app.route('/explore', methods=["GET", "POST"])
def explore():
    artworks = Artwork.query.all()
    random.shuffle(artworks)

    randomArtwork = random.choice(Artwork.query.all())

    if 'user_id' in session and session['logged_in'] == True:
        currentUser = User.query.get(session['user_id'])
        user = User.query.get(session['user_id'])

        if request.method == "POST":
            search = request.form.get("search_term")
            print(search)
            artworks = Artwork.query.filter((Artwork.title.like("%"+search+"%")) | (Artwork.artist.like("%"+search+"%")) | (Artwork.description.like("%"+search+"%"))).all()
            
            random.shuffle(artworks)
            return render_template('explore.html', artworks=artworks, currentUser=currentUser, randomArtwork=randomArtwork, user=user, userLoggedIn = True)

        else:
            return render_template('explore.html', artworks=artworks, currentUser=currentUser, randomArtwork=randomArtwork, user=user, userLoggedIn = True)
    else:
        if request.method == "POST":
            search = request.form.get("search_term")
            random.shuffle(artworks)
            return render_template('explore.html', artworks=artworks, randomArtwork=randomArtwork, userLoggedIn = False)
        else:
            return render_template('explore.html', artworks=artworks, randomArtwork=randomArtwork, userLoggedIn = False)

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

    if 'user_id' not in session:  
         user = None  
         userLoggedIn = False  

    else:
        user = User.query.get(session['user_id'])
        userLoggedIn = True  

    comments = Comment.query.filter_by(artwork_id = artwork.id).all()
    commentsCount = db.session.execute(Comment.query.filter_by(artwork_id=artwork.id).statement.with_only_columns(func.count()).order_by(None)).scalar()

    if not artwork:
        return render_template('error.html', message='Artwork not found.')
    
    if request.method == 'POST':
        if user:  
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
    total = calculateCartTotal(session['cart'])
    return render_template('purchase.html', user=user, user_id=user_id, currentUser=user, cart=session['cart'], total=total)

@app.route("/thankyou", methods=["POST"])
def thankyou():
    user_id = session['user_id']
    if 'cart' in session and session['cart']:
        user = User.query.get(user_id)
        # Calculate the total amount from the cart
        total_amount = calculateCartTotal(session['cart'])
        shipping_address = request.form.get('address') + ', ' + \
                           request.form.get('city') + ', ' + \
                           request.form.get('state') + ', ' + \
                           request.form.get('country') + ', ' + \
                           request.form.get('zip-code')

        # Create a new transaction record in the database
        transaction = Transaction(
            buyer_name=user.name,
            amount=total_amount,
            shipping_address=shipping_address,
        )

        # Save the transaction to the database
        db.session.add(transaction)
        db.session.commit()

        # Clear the cart after the successful purchase
        session['cart'] = {}

        message = "Thank you for your order"
        return render_template('thankyou.html', message=message, currentUser=user, user=user)

    return redirect(url_for('purchasePage', user_id=user_id))


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

    # Upload the file to S3 bucket
    client.upload_file(filename, "artvisionbucket", "artgallery/" +str(user.userName)+"/"+ filename)

    bucket_name = "artvisionbucket"
    s3_key = f"artgallery/{user.userName}/{filename}"
    url = f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"

    os.remove(filename)
    newArt = Artwork(title =title, description=description, category=category, price=price, status=status, url=url, user_id=user_id, artist=artist, uploadDate=datetime.date.today(), shop_item=shop_item)
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

#update cart quantity
@app.route('/updateCart', methods=['POST'])
def updateCart():
    data = request.get_json()
    artwork_id = data.get('artwork_id')
    quantity = int(data.get('quantity', 0))
    cart = session['cart']
    cart[artwork_id]['quantity'] = quantity
    session['cart'] = cart
    return jsonify(success=True)

def calculateCartTotal(cart):
    total = 0.00
    for attr in cart.values():
        total += attr['quantity'] * attr['price']
    return total


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

@app.route("/admin")
def admin_page():
    # Fetch data from all the tables
    users = User.query.all()
    artworks = Artwork.query.all()
    comments = Comment.query.all()
    transactions = Transaction.query.all()

    return render_template("admin.html", users=users, artworks=artworks, comments=comments, transactions=transactions)


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
    return redirect(url_for('artworkDetails', artwork=artwork, user=user, currentUser=user, artist=artist, form=form, comments=comments, artwork_id=artwork_id))

#Routes for user galleries
@app.route('/<option>/<int:user_id>')
def gallery(option, user_id):
    user = User.query.get(user_id)
    if option == 'gallery':
        artworks = Artwork.query.filter_by(user_id=user_id, shop_item=False).all()
    elif option == 'shop':
        artworks = Artwork.query.filter_by(user_id=user_id, shop_item=True).all()
    serialized_artworks = {artwork.id: {"id": artwork.id, "title": artwork.title, "price": artwork.price, "url": artwork.url} for artwork in artworks}
    return jsonify(serialized_artworks)


#Routes for explore
@app.route('/category/<category>')
def exploreCategories(category):
    artworks = Artwork.query.filter_by(category=category).all()
    serialized_artworks = {artwork.id: {"id": artwork.id, "title": artwork.title, "price": artwork.price, "url": artwork.url, "user_id" : artwork.user_id, "artist" : artwork.artist} for artwork in artworks}
    return jsonify(serialized_artworks)



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

    if request.method == "POST":
        ##UPDATE USER PROFILE INFORMATION
        if request.form.get('profile-change') == "Update":
            newUsername = request.form.get("newUsername")
            newDisplayName = request.form.get("newDisplayName")
            newPronouns = request.form.get("newPronouns")
            newTitle = request.form.get("newTitle")
            newBio = request.form.get("newBio")

            if newDisplayName:
                user.name = newDisplayName
                update = True

            if newPronouns:
                user.pronouns = newPronouns
                update = True

            if newTitle:
                user.title = newTitle
                update = True

            if newBio:
                user.bio = newBio
                update = True

            userNameCheck = User.query.filter_by(userName=newUsername).first()
            # print(userNameCheck)
            currentUsername = user.userName
            if newUsername and userNameCheck is None:
                user.userName = newUsername

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
                client.delete_object(Bucket="artvisionbucket", Key="profilephoto/" + currentUsername +"/"+ filename)
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
                    client.delete_object(Bucket="artvisionbucket", Key="artgallery/" + currentUsername +"/"+ filename)
                    os.remove(filename)
                    update = True
            db.session.commit()

        ##UPDATE ACCOUNT INFORMATION
        if request.form.get('account-change') == "Update":
            ##Verification
            user = User.query.filter_by(id=user_id).first()
            passwordInDatabase = user.password
            emailInDatabase = user.email

            currentEmail = request.form.get("currentemail")
            currentPassword = request.form.get("currentpassword")

            ##Proposed changes
            newEmail = request.form.get("newemail")
            confirmNewEmail = request.form.get("confirmnewemail")

            newPassword = request.form.get("newpassword")
            confirmNewPassword = request.form.get("confirmnewpassword")
    

            ##Error checking
            errors = []
            #check for inputs for current email and current password
            if currentEmail == "":
                error = "Please enter your current email."
                errors.append(error)
    
            if currentPassword == "":
                error = "Please enter your current password."
                errors.append(error)

            # checks database for email matching current user.
            if currentEmail and currentEmail != emailInDatabase: 
                error = "Incorrect email! Please try again."
                errors.append(error)

            # checks database for password matching current user.
            if currentPassword and currentPassword != passwordInDatabase:
                error = "Incorrect password! Please try again."
                errors.append(error)

            # makes sure new email matches.
            if newEmail and newEmail != confirmNewEmail:
                error = "Your new email inputs do not match. Please try again."
                errors.append(error)

            # makes sure new password matches and meet requirements.
            if newPassword and newPassword != confirmNewPassword and passwordValidation(newPassword)== False:
                error = "Your new password inputs do not match and/or do not meet password requirements."
                errors.append(error)
            
            if (len(errors) > 0):
                return render_template('editAccount.html', user=user, user_id=user_id, artworks=artworks, currentUser=user, errors=errors)

            else:
                if newEmail:
                    user.email = newEmail
                    update = True

                if newPassword:
                    user.password = newPassword
                    update = True

                db.session.commit()

    if update == True:
        message = "Information updated"
    if update == False:
        message = "Information unchanged"
    db.session.commit()
    return redirect(url_for('userProfile', user_id=user_id, message=message))
    

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
Hiding API keys
https://www.youtube.com/watch?v=YdgIWTYQ69A
s3 Bucket
UAB Cloud Computing CS 403 SU2023
Delete from s3 Bucket
https://stackoverflow.com/questions/3140779/how-to-delete-files-from-amazon-s3-bucket
"""