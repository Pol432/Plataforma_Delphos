from app.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    print("Conectado a la base de datos...")
    
    # 1. Insertar progreso con status 'finished'
    try:
        db.execute(text("""
            INSERT INTO user_simulation_progress (user_id, simulation_id, status, score)
            VALUES (4, 4, 'finished', 5.0)
            ON CONFLICT DO NOTHING;
        """))
        db.commit()
        print("Progreso insertado con éxito.")
    except Exception as e2:
        db.rollback()
        print("Aviso en progreso:", e2)
    
    # 2. Inyectar habilidades de usuario
    try:
        db.execute(text("""
            INSERT INTO habilidades_usuario (usuario_id, skill_id, nivel_dominio)
            VALUES (4, 1, 95.5), (4, 2, 88.0), (4, 3, 90.0)
            ON CONFLICT DO NOTHING;
        """))
        db.commit()
        print("¡Skills inyectadas con éxito!")
    except Exception as e3:
        db.rollback()
        print("Error en skills:", e3)

except Exception as e:
    print("Error general:", e)
finally:
    db.close()
