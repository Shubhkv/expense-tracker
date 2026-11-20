from db import get_connection

def create_tables():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id SERIAL PRIMARY KEY,
                date DATE DEFAULT CURRENT_DATE,
                category TEXT NOT NULL,
                description TEXT,
                amount NUMERIC(10, 2) NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        print("Tables created successfully.")

if __name__ == "__main__":
    create_tables()
