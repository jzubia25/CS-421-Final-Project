from main import app, db, User
import os
import boto3

ACCESS_KEY ="AKIA6IBZYP2JOCLZAYGT"
SECRET_KEY ="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"
AWS_REGION = "us-east-2"


def delete_photo_from_s3(photo_url):
    if not photo_url:
        return

    # Extract the filename from the photo_url
    filename = photo_url.split("/")[-1]

    # Create a Boto3 client for S3
    client = boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=AWS_REGION
    )
    s3 = boto3.resource(        
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=AWS_REGION
    )
    # Currently not working!!!
    try:
        client.delete_object(Bucket="artvisionbucket", Key="profilephoto/" + filename)
        s3.Object("artvisionbucket", "profilephoto/" + filename).delete()
        print(f"Photo {filename} deleted from S3 bucket")
    except Exception as e:
        print(f"Error deleting photo {filename} from S3 bucket: {e}")

def delete_artwork_from_s3(artwork_url):
    if not artwork_url:
        return

    # Extract the filename from the artwork_url
    filename = artwork_url.split("/")[-1]

    # Create a Boto3 client for S3
    client = boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=AWS_REGION
    )

    try:
        client.delete_object(Bucket="artvisionbucket", Key="artgallery/" + filename)
        print(f"Artwork {filename} deleted from S3 bucket")
    except Exception as e:
        print(f"Error deleting artwork {filename} from S3 bucket: {e}")

# Now, run the database operations within the Flask application context
with app.app_context():
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
    all_users = User.query.all()
    for user in all_users:
        delete_photo_from_s3(user.profilePhotoLink)
        db.session.delete(user)
        print(user.profilePhotoLink)
        print(f"User {user.userName} deleted")

        artworks = Artwork.query.filter_by(user_id=user.id).all()
        for artwork in artworks:
            delete_artwork_from_s3(artwork.url)
            db.session.delete(artwork)

        # Delete the user
        db.session.delete(user)
        print(f"User {user.userName} deleted")


    db.session.commit()
    # new_User = User('Obie', 'C','o@gmail.com','Obie2023','Ambition2023','I like basketball','image/profile_photo.jpeg')
    # db.session.add(new_User)
    # db.session.commit()
    # print(new_User.id)
    # print(new_User.userName)
    # print(new_User.password)    
    # print(new_User.profilePhotoLink)