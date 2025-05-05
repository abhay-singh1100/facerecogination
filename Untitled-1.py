import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Add a new column to the users table
cursor.execute("ALTER TABLE users ADD COLUMN face_image BLOB")

conn.commit()
conn.close()
