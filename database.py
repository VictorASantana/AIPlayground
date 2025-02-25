from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Configurar a URL de conexão com o PostgreSQL
DATABASE_URL = "postgresql://postgres:admin@localhost:5432/AIPlayground"

# Criar a conexão com o banco
engine = create_engine(DATABASE_URL, echo=True)

# Criar a base do SQLAlchemy
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# Definir a tabela de usuários
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow)

# Definir a tabela de agentes
class Agente(Base):
    __tablename__ = "agentes"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    prompt = Column(String, nullable=False)

# Função para criar as tabelas no banco
def criar_banco():
    Base.metadata.create_all(engine)

# Executar a criação do banco ao rodar o script
if __name__ == "__main__":
    criar_banco()
    print("Banco de dados criado com sucesso!")
