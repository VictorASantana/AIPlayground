
import psycopg2

#Criar tabela files
"""
CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    dados BYTEA NOT NULL,
    data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

"""

# Configurações do banco de dados PostgreSQL
DB_CONFIG = {
    "dbname": "PlaygroundAI",
    "user": "postgres",
    "password": "ASPIRE",
    "host": "localhost",
    "port": "5432"
}

# Função para conectar ao banco
def conectar():
    return psycopg2.connect(**DB_CONFIG)

# Função para salvar arquivo no banco de dados e retornar o id do arquivo
def save_file(file_name, file_data):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO files (file_name, file_data) VALUES (%s, %s)", 
                   (file_name, psycopg2.Binary(file_data)))
    file_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    return file_id


# Função para baixar arquivo
def get_file(file_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT file_name, file_data FROM files WHERE id = %s", (file_id,))
    file = cursor.fetchone()
    cursor.close()
    conn.close()
    return file

# Função para excluir arquivo
def delete_file(file_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM files WHERE id = %s", (file_id,))
    conn.commit()
    cursor.close()
    conn.close()