import sqlite3

class SQLiteDB:
    def __init__(self):
        self.conn = sqlite3.connect('db.sqlite3')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_quota (
                username TEXT PRIMARY KEY,
                quota TEXT NOT NULL,
                count INTEGER NOT NULL
            )
        ''')
        self.conn.commit()

    def get_user_data(self, username):
        self.cursor.execute('SELECT * FROM user_quota WHERE username=?', (username,))
        return self.cursor.fetchone()

    def update_count(self, username):
        self.cursor.execute('UPDATE user_quota SET count = count - 1 WHERE username=?', (username,))
        self.conn.commit()

# Create the database and table
if __name__ == "__main__":
    db = SQLiteDB()
    print("Database and table created successfully.")
