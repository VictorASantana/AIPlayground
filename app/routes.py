from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from .database import SessionLocal
from .database import get_db
from .models import Usuario, Agente, HistoricoMensagem
from .openai_client import chat_with_openai

routes = Blueprint('routes', __name__)

@routes.route("/usuarios", methods=["POST"])
def criar_usuario():
    data = request.json
    db: Session = next(get_db())
    
    usuario_existente = db.query(Usuario).filter(Usuario.email == data["email"]).first()
    if usuario_existente:
        return jsonify({"erro": "Usuário já cadastrado"}), 400

    usuario = Usuario(nome=data["nome"], email=data["email"], google_id=data["google_id"])
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return jsonify({"id": usuario.id, "nome": usuario.nome})

@routes.route("/agentes", methods=["POST"])
def criar_agente():
    data = request.json
    db: Session = next(get_db())

    agente = Agente(usuario_id=data["usuario_id"], nome=data["nome"], prompt=data["prompt"], modelo=data["modelo"])
    db.add(agente)
    db.commit()
    db.refresh(agente)

    return jsonify({"id": agente.id, "nome": agente.nome})

@routes.route("/agentes/<int:agente_id>/chat", methods=["POST"])
def interagir_com_agente(agente_id):
    data = request.json
    db: Session = next(get_db())

    agente = db.query(Agente).filter(Agente.id == agente_id).first()
    if not agente:
        return jsonify({"erro": "Agente não encontrado"}), 404

    resposta = chat_with_openai(agente.prompt, data["mensagem"], agente.modelo)

    historico = HistoricoMensagem(agente_id=agente.id, mensagem=data["mensagem"], resposta=resposta)
    db.add(historico)
    db.commit()

    return jsonify({"resposta": resposta})


@routes.route("/agentes/<int:agente_id>", methods=["PUT"])
def editar_agente(agente_id):
    session = SessionLocal()
    agente = session.query(Agente).filter_by(id=agente_id).first()

    if not agente:
        session.close()
        return jsonify({"error": "Agente não encontrado"}), 404

    data = request.json
    agente.nome = data.get("nome", agente.nome)
    agente.prompt = data.get("prompt", agente.prompt)
    agente.modelo = data.get("modelo", agente.modelo)
    session.commit()
    session.close()

    return jsonify({"message": "Agente atualizado com sucesso"})

@routes.route("/agentes", methods=["GET"])
def listar_agentes():
    session = SessionLocal()
    agentes = session.query(Agente).all()
    session.close()

    return jsonify([{"id": agente.id, "nome": agente.nome, "modelo": agente.modelo} for agente in agentes])

@routes.route("/agentes/<int:agente_id>", methods=["GET"])
def obter_agente_id(agente_id):
    session = SessionLocal()
    
    agente = session.query(Agente).filter(Agente.id == agente_id).first()
    
    if not agente:
        session.close()
        return jsonify({"error": "Agente não encontrado"}), 404

    session.close()

    return jsonify({
        "id": agente.id,
        "usuario_id": agente.usuario_id,
        "nome": agente.nome,
        "prompt": agente.prompt,
        "modelo": agente.modelo
    })

@routes.route("/agentes/<int:agente_id>", methods=["DELETE"])
def deletar_agente(agente_id):
    session = SessionLocal()
    
    agente = session.query(Agente).filter(Agente.id == agente_id).first()
    
    if not agente:
        session.close()
        return jsonify({"error": "Agente não encontrado"}), 404

    session.query(HistoricoMensagem).filter(HistoricoMensagem.agente_id == agente_id).delete()

    session.delete(agente)
    session.commit()
    session.close()

    return jsonify({"message": "Agente excluído com sucesso"})


@routes.route("/agentes/<int:agente_id>/historico", methods=["GET"])
def obter_historico(agente_id):
    db: Session = next(get_db())
    
    agente = db.query(Agente).filter(Agente.id == agente_id).first()
    if not agente:
      return jsonify({"erro": "Agente não encontrado"}), 404

    historico = db.query(HistoricoMensagem).filter(HistoricoMensagem.agente_id == agente_id).order_by(HistoricoMensagem.timestamp.desc()).all()

    return jsonify([
        {
            "mensagem": h.mensagem,
            "resposta": h.resposta,
            "timestamp": h.timestamp
        } 
        for h in historico
    ])


