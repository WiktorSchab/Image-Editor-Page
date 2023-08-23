"""Module to display flash communicates and use session var"""
from flask import session, flash
import bcrypt


# Class to user of program
class UserClass:
    """Class to manage users"""

    def __init__(self, nick, password):
        """init of user_class takes nick and password to create instance of class.
        Other parameters will be updated in other function.

        nick - identification od user
        password - key that allows to verify user
        email - Contact email to user
        isPremium - True/False user have account with height priority
        isAdmin - True/False user have account with higher authority
        """
        self.nick = nick
        self.password = password
        self.email = ''
        self.is_premium = ''
        self.is_admin = ''

    def verify_user(self, User):
        """Function that verifies if user with certain combination of password and login exists
        User - table in database

        Function return info about process"""

        user_login = User.query.filter(User.nick == self.nick).first()

        if user_login:
            # Checking if password is corrected using bcrypt because password on db is secured
            if bcrypt.checkpw(self.password.encode('utf-8'), user_login.password):
                message = 'Login process is successful'
                session['user'] = user_login.nick
            else:
                message = 'Invalid password'
        else:
            message = 'There is no user with that login'

        # Passing message about status of login
        flash(message)
        return message

    def verify_register(self, User, repeat_password, email):
        """ Function that verifies if data given in registry is correct
        User - table in database
        repeat_password - second field with password in registry form
        email - email given in registry form

        Function returns 1 if verification was successful and none if not"""
        # Checking if nick is unique
        nick_exist = User.query.filter(User.nick == self.nick).first()
        if nick_exist:
            flash('There is user with that nick registered already!')
            return

        # Checking if email is unique
        email_exist = User.query.filter(User.email == email).first()
        if email_exist:
            flash('There is user with that email registered already!')
            return

        # Checking passwords are the same
        if repeat_password != self.password:
            flash('Both passwords should be the same!')
            return

        flash('You have been registered successfully!')
        self.email = email
        return 1

    @staticmethod
    def secure_password(password):
        """Function to secure given password.
        To password salt is added and then password is hashed
        Function returns hashed password"""

        # Encoding password
        password_encoded = password.encode('utf-8')

        # Generating salt using bcrypt
        salt = bcrypt.gensalt()

        # Hashing password with salt using bcrypt
        hashed = bcrypt.hashpw(password_encoded, salt)
        return hashed

    def creating_user(self, db, User):
        """Function that creates user in database
        db - database
        User - Table in database"""

        # Assigning data for new account
        new_user = User(
            nick=self.nick,
            password=self.secure_password(self.password),
            email=self.email,
            premium=False,
            admin=False
        )

        # Creating new user
        db.session.add(new_user)
        db.session.commit()

        return 'User created'
