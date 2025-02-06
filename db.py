import sqlite3

DB_NAME = "users.db"

def init_db():
    """Initialize the database and create the required table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            chat_id INTEGER PRIMARY KEY,
            time_str TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def save_user_preference(chat_id, time_str):
    """Save or update the user's preferred affirmation time."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_preferences (chat_id, time_str) 
        VALUES (?, ?)
        ON CONFLICT(chat_id) DO UPDATE SET time_str=excluded.time_str
    """, (chat_id, time_str))

    conn.commit()
    conn.close()

def get_user_time(chat_id):
    """Retrieve the preferred time of a user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT time_str FROM user_preferences WHERE chat_id = ?", (chat_id,))
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else None

def get_all_users():
    """Retrieve all users with their preferred times."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT chat_id, time_str FROM user_preferences")
    users = cursor.fetchall()

    conn.close()
    return users

# Initialize the database (run this once when setting up)
if __name__ == "__main__":
    init_db()
    print("Database initialized.")
