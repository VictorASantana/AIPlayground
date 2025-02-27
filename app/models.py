from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    google_id = Column(String, unique=True, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

    agentes = relationship("Agente", back_populates="usuario")

class Agente(Base):
    __tablename__ = "agentes"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    nome = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    modelo = Column(String, default="gpt-3.5-turbo")
    criado_em = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="agentes")
    historico = relationship("HistoricoMensagem", back_populates="agente", cascade="all, delete-orphan")

class HistoricoMensagem(Base):
    __tablename__ = "historico_mensagens"
    
    id = Column(Integer, primary_key=True, index=True)
    agente_id = Column(Integer, ForeignKey("agentes.id"))
    mensagem = Column(String, nullable=False)
    resposta = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    agente = relationship("Agente", back_populates="historico")
