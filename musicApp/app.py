from flask import Flask, render_template, request, redirect,  url_for, send_from_directory, flash
import mysql.connector
from mysql.connector import errorcode
import eyed3
import os
from os import path


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


DB_NAME = 'music'
TABLE_NAME = 'songs'

TABLES = {}
TABLES['songs'] = (
    "CREATE TABLE `songs` ("
    "  `id` int(10) NOT NULL AUTO_INCREMENT,"
    "  `title` varchar(50) NOT NULL,"
    "  `artist` varchar(50) NOT NULL,"
    "  `album` varchar(50) NOT NULL,"
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

UPLOAD_FOLDER = 'static/songs'
ASSETS_FOLDER = 'static/assets'
ALLOWED_EXTENSIONS = {'mp3'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ASSETS_FOLDER'] = ASSETS_FOLDER


@app.route('/home', methods=['GET'])
def home():
    query = ("SELECT * FROM {} ".format(TABLE_NAME))
    cursor.execute(query)
    return render_template('home.html', cursor=cursor)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(url_for('upload'))
        f = request.files['file']

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if f.filename == '':
            return redirect(url_for('upload'))

        if f and allowed_file(f.filename):
            add_song = ("INSERT INTO {} "
                        "(title, artist, album) "
                        "VALUES (%s, %s, %s)".format(TABLE_NAME))
            data_song = list(request.form.values())
            cursor.execute(add_song, data_song)
            id = cursor.lastrowid

            f.save(os.path.join(
                app.config['UPLOAD_FOLDER'], '{}.mp3'.format(id)))
            audio_file = eyed3.load(os.path.join(
                app.config['UPLOAD_FOLDER'], '{}.mp3'.format(id)))
            for image in audio_file.tag.images:
                image_file = open(os.path.join(
                    app.config['ASSETS_FOLDER'], '{}.jpg'.format(id)), "wb")
                image_file.write(image.image_data)
                image_file.close()
                break

            cnx.commit()
        return redirect(url_for('home'))

    return render_template('uploadForm.html')


@app.route('/play/<id>', methods=['GET'])
def play(id):
    if 'song' in request.args:
        song = request.args['song']
        artist = request.args['artist']
        album = request.args['album']
    else:
        query = ("SELECT * FROM {} WHERE id = {} ".format(TABLE_NAME, id))
        cursor.execute(query)
        _, song, artist, album = list(cursor)[0]
    imgpath = os.path.join(app.config['ASSETS_FOLDER'], '{}.jpg'.format(id))
    if path.exists(imgpath):
        exist = True
    else:
        exist = False
    return render_template('play.html', id=id, song=song, artist=artist, album=album, exist=exist)


@app.route('/delete/<id>', methods=['GET'])
def delete(id):
    query = ("DELETE FROM {} WHERE id = {} ".format(TABLE_NAME, id))
    cursor.execute(query)
    cnx.commit()
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], '{}.mp3'.format(id)))
    imgpath = os.path.join(app.config['ASSETS_FOLDER'], '{}.jpg'.format(id))
    if path.exists(imgpath):
        os.remove(imgpath)
    return redirect(url_for('home'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = ("SELECT * FROM {} WHERE {} = '{}' ".format(TABLE_NAME,
                                                            request.form['in'], request.form['query']))
        cursor.execute(query)
        return render_template('search.html', cursor=cursor)
    return render_template('search.html')


@app.route('/download/<id>', methods=['GET'])
def download(id):
    return send_from_directory(app.config['UPLOAD_FOLDER'], '{}.mp3'.format(id), as_attachment=True, download_name='{}.mp3'.format(request.args['song']))


@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('home'))


app.run()
cursor.close()
cnx.close()
