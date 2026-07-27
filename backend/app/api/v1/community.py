from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.api import deps
from app.schemas.community import MessageRead
from typing import List

router = APIRouter()

# --- 1. LEER MENSAJES ---
@router.get("/messages/{channel_name}", response_model=List[MessageRead])
def get_community_messages(channel_name: str, db: Session = Depends(deps.get_db)):
    # Buscamos el ID del canal
    query_channel = text("SELECT id FROM community_channels WHERE name = :name")
    channel = db.execute(query_channel, {"name": channel_name}).fetchone()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Canal no encontrado")

    # Traemos los mensajes
    query_msgs = text("""
        SELECT id, channel_id, user_email, content, created_at 
        FROM community_messages 
        WHERE channel_id = :cid 
        ORDER BY created_at ASC
    """)
    result = db.execute(query_msgs, {"cid": channel[0]}).fetchall()
    return result

# --- 2. ENVIAR NUEVOS MENSAJES (LO QUE FALTABA) ---
@router.post("/messages/{channel_name}")
def post_message(
    channel_name: str,
    content: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user) # Esto asegura que sepas quién escribe
):
    # Verificamos que el canal exista
    query_channel = text("SELECT id FROM community_channels WHERE name = :name")
    channel = db.execute(query_channel, {"name": channel_name}).fetchone()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Canal no encontrado")

    # Insertamos el mensaje en la base de datos
    query_insert = text("""
        INSERT INTO community_messages (channel_id, user_email, content)
        VALUES (:cid, :email, :content)
    """)
    db.execute(query_insert, {
        "cid": channel[0], 
        "email": current_user.email, # Usamos el email del usuario logueado
        "content": content
    })
    db.commit()
    
    return {"status": "success", "message": "Mensaje publicado"}