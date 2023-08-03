from main import app, db, User, Artwork
import os
import boto3

# ###
# GRAB ACCESS_KEY and SECRET_KEY FROM GITHUB. DO NOT COMMIT TO GITHUB WITH ACCESS KEYS IN CODE

ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")


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

# Now, run the database operations within the Flask application context
# Reference:
# https://stackoverflow.com/questions/3140779/how-to-delete-files-from-amazon-s3-bucket
with app.app_context():

# NOTE THIS CODE BELOW WILL RESET THE DATABASE. COMMENT OUT PARTS IF NECCESSARY
    # all_users = User.query.all()
    # for user in all_users:
    #     delete_photo_from_s3(user.profilePhotoLink)
    #     print(user.profilePhotoLink)
    #     # db.session.delete(user)
    #     # print(user.profilePhotoLink)
    #     # print(f"User {user.userName} deleted")

    #     artworks = Artwork.query.filter_by(user_id=user.id).all()
    #     for artwork in artworks:
    #         delete_artwork_from_s3(artwork.url)
    #         print(user.profilePhotoLink)
    #         delete_artwork_from_s3(artwork.url)
    #         db.session.delete(artwork)

    #     # Delete the user
    #     db.session.delete(user)
    #     print(f"User {user.userName} deleted")


    # db.session.commit()
    # List all Users
    all_Users = User.query.all()
    for user in all_Users:
        print(user.userName)
        print(user.email)

    userNameCheck = User.query.filter_by(userName="Ambition2015").first()
    if userNameCheck:
        userNameCheck.userName = "Ambition0516"
        artworks = Artwork.query.filter_by(user_id=1).all()
        for artwork in artworks:
            url = artwork.url
            url_parts = url.split("/")

            url_parts[4] = "Ambition0516"
            newUrl = "/".join(url_parts)
            artwork.url = newUrl
        db.session.commit()
    # List all Art
    # all_Art = Artwork.query.all()
    # for art in all_Art:
    #     print(art.url)
    # for art in all_Art:
    #     print(art.url)

    # new_User = User('John', 'James','j@gmail.com','JJsmoove','jjsmoove123','I like basketball','profile_photo.jpeg')
    # db.session.add(new_User)
    # db.session.commit()

    # # List all Users
    # all_Users = User.query.all()
    # print(all_Users)

    # Select the User by id
    # first_User = User.query.get(1)
    # if first_User:
    #     print(first_User.userName)
    #     print(first_User.profilePhotoLink)

    # # Update
    # first_User = User.query.get(1)
    # first_User.lastName = "Charles"
    # db.session.add(first_student)
    # db.session.commit()

    # # delete
    # second_User = User.query.get(2)
    # db.session.delete(second_User)
    # db.session.commit()


    # new_User = User('Obie', 'C','o@gmail.com','Obie2023','Ambition2023','I like basketball','image/profile_photo.jpeg')
    # db.session.add(new_User)
    # db.session.commit()
    # print(new_User.id)
    # print(new_User.userName)
    # print(new_User.password)    
    # print(new_User.profilePhotoLink)

# NOTE CODE BELOW IS FOR DELETING A SINGLE USER
    # user = User.query.filter_by(userName="Ambition0516").first()

    # if user:
    #     # Step 2: Delete the user's profile photo from S3
    #     delete_photo_from_s3(user.profilePhotoLink)

    #     # Step 3: Delete the user's artwork
    #     artworks = Artwork.query.filter_by(user_id=user.id).all()
    #     for artwork in artworks:
    #         delete_artwork_from_s3(artwork.url)
    #         db.session.delete(artwork)

    #     # Step 4: Delete the user
    #     db.session.delete(user)

    #     # Step 5: Commit the changes to the database
    #     db.session.commit()