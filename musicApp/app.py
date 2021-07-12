from flask import Flask, render_template, request, redirect,  url_for, send_from_directory
from flask.helpers import flash
import mysql.connector
from mysql.connector import errorcode
import os

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

@app.route('/home', methods=['GET'])
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
        cnx.commit()
        f = request.files['file']
        f.save('static/songs/{}.mp3'.format(id))
        return redirect(url_for('home'))
    return render_template('uploadForm.html')

@app.route('/play/<id>', methods=['GET'])
def play(id):
    query = ("SELECT * FROM {} WHERE id = {} ".format(TABLE_NAME, id))
    cursor.execute(query)
    _, song, artist, album = list(cursor)[0]
    return render_template('play.html', id=id, song=song, artist=artist, album=album)

@app.route('/delete/<id>', methods=['GET'])
def delete(id):
    query = ("DELETE FROM {} WHERE id = {} ".format(TABLE_NAME, id))
    cursor.execute(query)
    cnx.commit()
    os.remove('static/songs/{}.mp3'.format(id))
    return redirect(url_for('home'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = ("SELECT * FROM {} WHERE {} = '{}' ".format(TABLE_NAME, request.form['in'], request.form['query']))
        cursor.execute(query)
        return render_template('search.html', cursor=cursor)
    return render_template('search.html', cursor=None)

@app.route('/download/<id>', methods=['GET'])
def download(id):
    return send_from_directory('static/songs/','{}.mp3'.format(id), as_attachment = True, download_name='{}.mp3'.format(request.args['song']))

app.run(debug=True)
cursor.close()
cnx.close()