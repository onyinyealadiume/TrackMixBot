import sqlite3

def create_connection():
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect('songs.db')  # This will create the file if it does not exist
        return conn
    except Exception as e:
        print(e)

def setup_database():

    """Create tables in the database."""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS users (
                         id INTEGER PRIMARY KEY,
                         username TEXT NOT NULL 
                     );''')
            c.execute('''CREATE TABLE IF NOT EXISTS songs (
                         songId INTEGER PRIMARY KEY,
                         title TEXT,
                         user_id INTEGER,
                         link TEXT,
                         pathToMp3 TEXT,
                         convertedAt TEXT,
                         FOREIGN KEY (user_id) REFERENCES users (id)
                     );''')
            conn.commit()
        except Exception as e:
            print(e)
        finally:
            conn.close()

def insert_user(conn, discord_id, username):
    """Insert or update a user in the database using Discord ID as PK."""
    cursor = conn.cursor()
    # Check if user already exists using Discord ID
    cursor.execute("SELECT username FROM users WHERE id = ?", (discord_id,))
    user = cursor.fetchone()
    if not user:
        # User does not exist, so insert them
        cursor.execute("INSERT INTO users (id, username) VALUES (?, ?)", (discord_id, username))
        print(f"User {username} added to the database with ID {discord_id}.")
    else:
        # If the user exists but the username has changed, update the record
        if user[0] != username:
            cursor.execute("UPDATE users SET username = ? WHERE id = ?", (username, discord_id))
            print(f"User {username}'s username updated in the database.")
    conn.commit()
    return discord_id



# Function to search for songs by keyword and retrieve their file paths
def search_songs(keyword):
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        try:
            query = "SELECT pathToMp3 FROM songs WHERE pathToMp3 LIKE ?"
            cursor.execute(query, ('%' + keyword + '%',))
            return [row[0] for row in cursor.fetchall()]  # Return list of file paths
        except Exception as e:
            print("Error searching for songs:", e)
            return []
        finally:
            conn.close()
    else:
        print("Failed to connect to the database.")
        return []



setup_database()  # Call this function to ensure your tables are set up
