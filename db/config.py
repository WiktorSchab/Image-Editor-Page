import os

# Path to db
db_folder = "db"
db_filename = "main.db"
db_path = os.path.abspath(os.path.join(db_folder, db_filename))

# Configuration of database
# Path to db
SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"