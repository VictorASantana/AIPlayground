import psycopg2

from services.database_connection import init_connection

#Criar tabela files
"""
CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_data BYTEA NOT NULL,
    data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

"""

# Função para salvar arquivo no banco de dados e retornar o id do arquivo
def save_file(agent_id, file_name, file_data):
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO files (agent_id, file_name, file_data) VALUES (%s, %s, %s) RETURNING id", 
                   (agent_id, file_name, psycopg2.Binary(file_data)))
    file_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    return file_id


# Função para baixar arquivo
def get_file(agent_id):
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, file_name, file_data FROM files WHERE agent_id = %s", (agent_id,))
    files = cursor.fetchall()
    cursor.close()
    conn.close()
    return files

# Função para excluir arquivo
def delete_file(file_id):
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM files WHERE agent_id = %s", (file_id,))
    conn.commit()
    cursor.close()
    conn.close()