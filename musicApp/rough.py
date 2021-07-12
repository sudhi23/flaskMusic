from __future__ import print_function

import mysql.connector
from mysql.connector import errorcode

DB_NAME = 'music'
TABLE_NAME = 'songs'

# TABLES = {}
# TABLES['songs'] = (
#     "CREATE TABLE `songs` ("
#     "  `id` int(11) NOT NULL AUTO_INCREMENT,"
#     "  `title` varchar(14) NOT NULL,"
#     "  `artist` varchar(16) NOT NULL,"
#     "  `album` varchar(16) NOT NULL,"
#     "  PRIMARY KEY (`id`)"
#     ") ENGINE=InnoDB")

cnx = mysql.connector.connect(user='root', database=DB_NAME)
cursor = cnx.cursor(buffered=True)
    
# def create_database(cursor):
#     try:
#         cursor.execute(
#             "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
#     except mysql.connector.Error as err:
#         print("Failed creating database: {}".format(err))
#         exit(1)

# try:
#     cursor.execute("USE {}".format(DB_NAME))
# except mysql.connector.Error as err:
#     print("Database {} does not exists.".format(DB_NAME))
#     if err.errno == errorcode.ER_BAD_DB_ERROR:
#         create_database(cursor)
#         print("Database {} created successfully.".format(DB_NAME))
#         cnx.database = DB_NAME
#     else:
#         print(err)
#         exit(1)

# def createTable(table_name):
#     table_description = TABLES[table_name]
#     try:
#         print("Creating table {}: ".format(table_name), end='')
#         cursor.execute(table_description)
#     except mysql.connector.Error as err:
#         print(err.msg)
#     else:
#         print("OK")

# for table_name in TABLES:
#     try:
#         cursor.execute("SHOW TABLES LIKE '{}'".format(table_name))
#     except mysql.connector.Error as err:
#         print(err.msg)
#         createTable(table_name)

# add_song = ("INSERT INTO songs "
#                "(title, artist, album) "
#                "VALUES (%s, %s, %s)")
# data_song = list({'title':'abc', 'artist':'def', 'album':'ghi'}.values())
# cursor.execute(add_song, data_song)
# print(cursor.lastrowid)

# query = ("SELECT * FROM {} ".format(TABLE_NAME))

# cursor.execute(query)

# query = ("SELECT * FROM {} WHERE id = {} ".format(TABLE_NAME, 1))
# cursor.execute(query)

# print(list(cursor)[0])

#for (id, song, artist, album) in cursor:
#    print(id, song, artist, album)

# cnx.commit()
# cursor.close()
# cnx.close()