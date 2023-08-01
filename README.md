# CS-421-Final-Project
ArtVision: A Collaborative E-Commerce Art Gallery Platform. Our team is developing an interactive and user-friendly art gallery website where art enthusiasts can share, discover, and purchase artwork. The platform leverages modern technologies for both front-end (HTML/CSS, JavaScript, React) and back-end development (Python/Django, PostgreSQL).


# ACCESS_KEY SECRET_KEY and AWS_REGION

Please follow the instructions below for setting up the keys:

1. Once you are in your flask environment run:
    pip install python-dotenv

2. Create a .env file inside the HTML folder of the repository

3. Paste the ACCESS_KEY, SECRET_KEY, and AWS_REGION in the .env file without using qoutes for the value:
    
    Example:
        ACCESS_KEY=keyvalue
        SECRET_KEY=keyvalue
        AWS_REGION=keyvalue

    NOTE: Replace keyvalue with actual key from discord.

4. If a .gitignore file isn't already in the root folder of the repository, create one and add the following text to the first line:

    .env

5. In the main.py file and crud.py file ensure that you now have these values for your keys:

    ACCESS_KEY = os.getenv("ACCESS_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")
    AWS_REGION = os.getenv("AWS_REGION")