from main import app, db, User

# Now, run the database operations within the Flask application context
with app.app_context():
    new_User = User('John', 'James','j@gmail.com','JJsmoove','jjsmoove123','I like basketball','profile_photo.jpeg')
    db.session.add(new_User)
    db.session.commit()

    # List all Users
    all_Users = User.query.all()
    print(all_Users)

    # Select the User by id
    first_User = User.query.get(1)
    if first_User:
        print(first_User.userName)
        print(first_User.profilePhotoLink)

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
        db.session.delete(user)
        print(f"User {user.userName} deleted")
    db.session.commit()

    new_User = User('Obie', 'C','o@gmail.com','Obie2023','Ambition2023','I like basketball','image/profile_photo.jpeg')
    db.session.add(new_User)
    db.session.commit()
    print(new_User.id)
    print(new_User.userName)
    print(new_User.password)    
    print(new_User.profilePhotoLink)