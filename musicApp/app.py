from flask import Flask, render_template, request
import mysql.connector
from mysql.connector import errorcode

DB_NAME = 'music'
TABLE_NAME = 'songs'

TABLES = {}
TABLES['songs'] = (
    "CREATE TABLE `songs` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `title` varchar(14) NOT NULL,"
    "  `artist` varchar(16) NOT NULL,"
    "  `album` varchar(16) NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

cnx = mysql.connector.connect(user='root')
cursor = cnx.cursor(buffered=True)
    
def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

try:
    cursor.execute("USE {}".format(DB_NAME))
except mysql.connector.Error as err:
    print("Database {} does not exists.".format(DB_NAME))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        print("Database {} created successfully.".format(DB_NAME))
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)

for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

app = Flask(__name__)

@app.route('/home')
def home():
    query = ("SELECT * FROM {} ".format(TABLE_NAME))
    cursor.execute(query)
    return render_template('home.html', cursor=cursor)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        add_song = ("INSERT INTO {} "
               "(title, artist, album) "
               "VALUES (%s, %s, %s)".format(TABLE_NAME))
        data_song = list(request.form.values())
        cursor.execute(add_song, data_song)
        id = cursor.lastrowid
        f = request.files['file']
        f.save('static/songs/{}.mp3'.format(id))
    return render_template('uploadForm.html')

app.run(debug=True)
cnx.commit()
cursor.close()
cnx.close()