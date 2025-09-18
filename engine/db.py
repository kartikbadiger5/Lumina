import eel
import sqlite3

# Eel-exposed function to reset (clear) the sys_apps table
@eel.expose
def reset_scanned_apps():
	cursor.execute('DELETE FROM sys_apps')
	con.commit()
	return 'ok'

import eel
import sqlite3

con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

# Create table for storing scanned applications
cursor.execute('''CREATE TABLE IF NOT EXISTS sys_apps (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT,
	extension TEXT,
	location TEXT
)''')
con.commit()

# Eel-exposed function to store scanned apps

import eel
import csv
import sqlite3

con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

# Create table for storing scanned applications
cursor.execute('''CREATE TABLE IF NOT EXISTS sys_apps (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT,
	extension TEXT,
	location TEXT
)''')
con.commit()

# Eel-exposed function to store scanned apps

def store_scanned_apps(apps):
	"""Store a list of app dicts (name, extension, location) in sys_apps table."""
	cursor.execute('DELETE FROM sys_apps')  # Clear previous scan
	for app in apps:
		cursor.execute('INSERT INTO sys_apps (name, extension, location) VALUES (?, ?, ?)',
					   (app.get('name'), app.get('extension'), app.get('location')))
	con.commit()

# con.commit()

# query = "INSERT INTO sys_command VALUES (null,'one note', 'C:\\Program Files\\Microsoft Office\\root\\Office16\\ONENOTE.exe')"
# cursor.execute(query)
# con.commit()

# query = "CREATE TABLE IF NOT EXISTS web_command(id integer primary key, name VARCHAR(100), url VARCHAR(1000))"
# cursor.execute(query)

# query = "INSERT INTO web_command VALUES (null,'youtube', 'https://www.youtube.com/')"
# cursor.execute(query)
# con.commit()


# testing module

	# Eel-exposed function to store scanned apps
	@eel.expose
	def store_scanned_apps(apps):
		"""Store a list of app dicts (name, extension, location) in sys_apps table."""
		cursor.execute('DELETE FROM sys_apps')  # Clear previous scan
		for app in apps:
			cursor.execute('INSERT INTO sys_apps (name, extension, location) VALUES (?, ?, ?)',
						   (app.get('name'), app.get('extension'), app.get('location')))
		con.commit()
		return 'ok'
# app_name = "android studio"
# cursor.execute('SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
# results = cursor.fetchall()
# print(results[0][0])

# Create a table with the desired columns
#cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (id integer primary key, name VARCHAR(200), mobile_no VARCHAR(255), email VARCHAR(255) NULL)''')


# Specify the column indices you want to import (0-based index)
# Example: Importing the 1st and 3rd columns
# desired_columns_indices = [0, 30]

# # Read data from CSV and insert into SQLite table for the desired columns
# with open('contacts.csv', 'r', encoding='utf-8') as csvfile:
#     csvreader = csv.reader(csvfile)
#     for row in csvreader:
#         selected_data = [row[i] for i in desired_columns_indices]
#         cursor.execute(''' INSERT INTO contacts (id, 'name', 'mobile_no') VALUES (null, ?, ?);''', tuple(selected_data))

import eel
import sqlite3

con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

# Create table for storing scanned applications
cursor.execute('''CREATE TABLE IF NOT EXISTS sys_apps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    extension TEXT,
    location TEXT
)''')
con.commit()

# Eel-exposed function to store scanned apps
@eel.expose
def store_scanned_apps(apps):
    """Store a list of app dicts (name, extension, location) in sys_apps table."""
    cursor.execute('DELETE FROM sys_apps')  # Clear previous scan
    for app in apps:
        cursor.execute('INSERT INTO sys_apps (name, extension, location) VALUES (?, ?, ?)',
                       (app.get('name'), app.get('extension'), app.get('location')))
    con.commit()
    return 'ok'