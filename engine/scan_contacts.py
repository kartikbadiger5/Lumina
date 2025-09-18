import sqlite3

def add_contact_by_voice(name, phone_number, email=''):
    con = sqlite3.connect("jarvis.db")
    cursor = con.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('SELECT id FROM contacts WHERE LOWER(name) = ?', (name.lower(),))
    if cursor.fetchone():
        con.close()
        return {'status': 'error', 'message': 'Contact already exists'}
    cursor.execute('INSERT INTO contacts (name, phone_number, email) VALUES (?, ?, ?)', (name, phone_number, email))
    con.commit()
    con.close()
    return {'status': 'success', 'message': f'Contact "{name}" added successfully'}

def search_contact(query):
    con = sqlite3.connect("jarvis.db")
    cursor = con.cursor()
    cursor.execute('SELECT name, phone_number FROM contacts WHERE LOWER(name) LIKE ?', (f'%{query.lower()}%',))
    results = cursor.fetchall()
    con.close()
    if results:
        return results[0]
    return None

def delete_all_contacts():
    """Delete all contacts from the database."""
    con = sqlite3.connect("jarvis.db")
    cursor = con.cursor()
    cursor.execute('DELETE FROM contacts')
    deleted_count = cursor.rowcount
    con.commit()
    con.close()
    return {'status': 'success', 'message': f'Deleted {deleted_count} contacts from database'}

def get_contacts_count():
    """Get the total number of contacts in the database."""
    con = sqlite3.connect("jarvis.db")
    cursor = con.cursor()
    cursor.execute('SELECT COUNT(*) FROM contacts')
    count = cursor.fetchone()[0]
    con.close()
    return count
