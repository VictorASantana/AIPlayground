import streamlit as st
import psycopg2

DB_CONFIG = {
    "dbname": st.secrets["DB_NAME"],
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASSWORD"],
    "host": st.secrets["DB_HOST"],
    "port": st.secrets["DB_PORT"]
}

def init_connection():
    return psycopg2.connect(**DB_CONFIG)

def table_exists(table_name):
  conn = init_connection()
  cur = conn.cursor()
  
  cur.execute("""
      SELECT EXISTS (
          SELECT FROM information_schema.tables 
          WHERE table_name = %s
      );
  """, (table_name,))
  
  exists = cur.fetchone()[0]
  
  cur.close()
  conn.close()
  return exists