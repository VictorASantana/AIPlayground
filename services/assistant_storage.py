import psycopg2
from typing import Dict, Any
from services.database_connection import init_connection, table_exists

# Configurações do banco de dados PostgreSQL (usando as mesmas do file_storage)
DB_CONFIG = {
    "dbname": "PlaygroundAI",
    "user": "postgres",
    "password": "ASPIRE",
    "host": "localhost",
    "port": "5432"
}

# SQL para criar a tabela de assistentes
"""
CREATE TABLE assistants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    system_message TEXT,
    model VARCHAR(50),
    temperature FLOAT DEFAULT 1.0,
    top_p FLOAT DEFAULT 1.0,
    max_tokens INTEGER DEFAULT 2000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def conectar():
    return psycopg2.connect(**DB_CONFIG)

def create_assistants_table():
    if not table_exists("assistants"):
        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE assistants (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    system_message TEXT,
                    model VARCHAR(50),
                    temperature FLOAT DEFAULT 1.0,
                    top_p FLOAT DEFAULT 1.0,
                    max_tokens INTEGER DEFAULT 2000,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            print("Table 'assistants' created successfully.")
        finally:
            cursor.close()
            conn.close()

def create_assistant(
    name: str,
    system_message: str,
    model: str,
    temperature: float = 1.0,
    top_p: float = 1.0,
    max_tokens: int = 2000
) -> int:
    """Cria um novo assistente e retorna seu ID"""
    create_assistants_table()  # Ensure table exists
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO assistants (name, system_message, model, temperature, top_p, max_tokens)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (name, system_message, model, temperature, top_p, max_tokens))
        assistant_id = cursor.fetchone()[0]
        conn.commit()
        print(f"Assistant created with ID: {assistant_id}")
        return assistant_id
    finally:
        cursor.close()
        conn.close()

def get_assistant(assistant_id: int) -> Dict[str, Any]:
    """Recupera as informações de um assistente específico"""
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, system_message, model, temperature, top_p, max_tokens
            FROM assistants WHERE id = %s
        """, (assistant_id,))
        result = cursor.fetchone()
        if result:
            return {
                "id": result[0],
                "name": result[1],
                "system_message": result[2],
                "model": result[3],
                "temperature": result[4],
                "top_p": result[5],
                "max_tokens": result[6]
            }
        return None
    finally:
        cursor.close()
        conn.close()

def get_all_assistants() -> list:
    """Recupera todos os assistentes"""
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, system_message, model, temperature, top_p, max_tokens
            FROM assistants ORDER BY name
        """)
        results = cursor.fetchall()
        return [{
            "id": row[0],
            "name": row[1],
            "system_message": row[2],
            "model": row[3],
            "temperature": row[4],
            "top_p": row[5],
            "max_tokens": row[6]
        } for row in results]
    finally:
        cursor.close()
        conn.close()

def update_assistant(
    assistant_id: int,
    name: str = None,
    system_message: str = None,
    model: str = None,
    temperature: float = None,
    top_p: float = None,
    max_tokens: int = None
) -> bool:
    """Atualiza as informações de um assistente"""
    updates = []
    values = []
    if name is not None:
        updates.append("name = %s")
        values.append(name)
    if system_message is not None:
        updates.append("system_message = %s")
        values.append(system_message)
    if model is not None:
        updates.append("model = %s")
        values.append(model)
    if temperature is not None:
        updates.append("temperature = %s")
        values.append(temperature)
    if top_p is not None:
        updates.append("top_p = %s")
        values.append(top_p)
    if max_tokens is not None:
        updates.append("max_tokens = %s")
        values.append(max_tokens)
    
    if not updates:
        return False

    updates.append("updated_at = CURRENT_TIMESTAMP")
    values.append(assistant_id)

    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(f"""
            UPDATE assistants 
            SET {", ".join(updates)}
            WHERE id = %s
        """, values)
        conn.commit()
        print(f"Assistant updated with ID: {assistant_id}")
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()

def delete_assistant(assistant_id: int) -> bool:
    """Deleta um assistente"""
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM assistants WHERE id = %s", (assistant_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close() 