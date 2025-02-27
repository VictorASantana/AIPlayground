from flask import Blueprint, request, jsonify
from app.database import SessionLocal
from app.models import Agente
import openai

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/agente/<int:agente_id>/chat", methods=["POST"])
def chat(agente_id):
    session = SessionLocal()
    agente = session.query(Agente).filter(Agente.id == agente_id).first()
    
    if not agente:
        return jsonify({"erro": "Agente não encontrado"}), 404

    dados = request.get_json()
    mensagem_usuario = dados.get("mensagem")

    if not mensagem_usuario:
        return jsonify({"erro": "Mensagem não fornecida"}), 400

    resposta = openai.ChatCompletion.create(
        model=agente.modelo,
        messages=[
            {"role": "system", "content": agente.prompt},
            {"role": "user", "content": mensagem_usuario}
        ]
    )

    session.close()
    return jsonify({"resposta": resposta["choices"][0]["message"]["content"]})
