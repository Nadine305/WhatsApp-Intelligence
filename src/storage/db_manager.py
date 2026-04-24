# This file will contain a Class that handles all the SQL work so you
#  don't have to write SQL queries inside your AI logic.
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        # Construct the connection string
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        dbname = os.getenv("DB_NAME")
        
        self.connection_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        self.engine = create_engine(self.connection_string)

    def execute_query(self, query, params=None):
        """Helper method to execute any SQL query."""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), params or {})
                connection.commit()
                return result
        except SQLAlchemyError as e:
            print(f"Database Error: {e}")
            return None

    # --- USER METHODS ---
    def add_user(self, user_id, phone_number, name):
        query = """
        INSERT INTO users (user_id, phone_number, name)
        VALUES (:user_id, :phone_number, :name)
        ON CONFLICT (user_id) DO NOTHING;
        """
        self.execute_query(query, {"user_id": user_id, "phone_number": phone_number, "name": name})

    # --- MESSAGE METHODS ---
    def add_message(self, user_id, content, timestamp):
        query = """
        INSERT INTO messages (user_id, content, timestamp, is_processed)
        VALUES (:user_id, :content, :timestamp, FALSE);
        """
        self.execute_query(query, {"user_id": user_id, "content": content, "timestamp": timestamp})

    def get_unprocessed_messages(self):
        """Fetch all messages that haven't been analyzed yet."""
        query = "SELECT message_id, user_id, content, timestamp FROM messages WHERE is_processed = FALSE;"
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                return result.fetchall()
        except SQLAlchemyError as e:
            print(f"Error fetching messages: {e}")
            return []

    def mark_as_processed(self, message_id):
        query = "UPDATE messages SET is_processed = TRUE WHERE message_id = :msg_id;"
        self.execute_query(query, {"msg_id": message_id})

    # --- INTEREST METHODS ---
    def add_interest(self, label, description):
        """Adds a new interest and returns its ID."""
        query = """
        INSERT INTO interests (cluster_label, description)
        VALUES (:label, :description)
        RETURNING interest_id;
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), {"label": label, "description": description})
                connection.commit()
                return result.fetchone()[0]
        except SQLAlchemyError as e:
            print(f"Error adding interest: {e}")
            return None

    def link_user_to_interest(self, user_id, interest_id, confidence):
        query = """
        INSERT INTO user_interests (user_id, interest_id, confidence_score)
        VALUES (:user_id, :interest_id, :confidence)
        ON CONFLICT DO NOTHING;
        """
        self.execute_query(query, {"user_id": user_id, "interest_id": interest_id, "confidence": confidence})