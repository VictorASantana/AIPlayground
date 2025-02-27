import streamlit as st
from services.database_connection import init_connection, table_exists

def create_user_table():
  if not table_exists("users"):
    conn = init_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            google_id TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("Tabela 'users' criada com sucesso.")

def insert_user(google_id, email):
  conn = init_connection()
  cursor = conn.cursor()

  create_user_table()

  cursor.execute("SELECT * FROM users WHERE google_id = %s;", (google_id,))
  existing_user = cursor.fetchone()

  if not existing_user:
    cursor.execute("INSERT INTO users (google_id, email) VALUES (%s, %s)", (google_id, email))
    conn.commit()
  
  cursor.close()
  conn.close()


  