# scripts/seed_ecuador.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.catalog import Region, Province, City

def seed_ecuador():
    """Poblar la base de datos con regiones, provincias y ciudades de Ecuador"""
    print("🌱 Iniciando seed de Ecuador...")
    
    db: Session = SessionLocal()
    
    try:
        # Verificar conexión
        print("📡 Verificando conexión a la base de datos...")
        db.execute(text("SELECT 1"))
        print("✅ Conexión exitosa")
        
        # Verificar si ya hay datos
        existing_regions = db.query(Region).count()
        print(f"📊 Regiones existentes: {existing_regions}")
        
        if existing_regions > 0:
            print(f"⚠️  Ya existen {existing_regions} regiones. Saltando seed.")
            return
        
        # ============ REGIONES ============
        print("\n📍 Insertando regiones...")
        regions_data = [
            {"code": "01", "name": "Costa", "description": "Región Litoral", "order": 1},
            {"code": "02", "name": "Sierra", "description": "Región Interandina", "order": 2},
            {"code": "03", "name": "Amazonía", "description": "Región Amazónica", "order": 3},
            {"code": "04", "name": "Insular", "description": "Región Insular - Galápagos", "order": 4},
        ]
        
        regions = {}
        for r_data in regions_data:
            region = Region(**r_data, is_active=True)
            db.add(region)
            db.flush()
            regions[r_data["code"]] = region.id
            print(f"  ✅ {r_data['name']} (ID: {region.id})")
        
        db.commit()
        print(f"✅ {len(regions_data)} regiones insertadas")
        
        # ============ PROVINCIAS ============
        print("\n🏛️  Insertando provincias...")
        provinces_data = [
            # COSTA
            {"code": "05", "name": "Esmeraldas", "region_code": "01", "capital": "Esmeraldas"},
            {"code": "08", "name": "Manabí", "region_code": "01", "capital": "Portoviejo"},
            {"code": "09", "name": "Guayas", "region_code": "01", "capital": "Guayaquil"},
            {"code": "13", "name": "Los Ríos", "region_code": "01", "capital": "Babahoyo"},
            {"code": "07", "name": "El Oro", "region_code": "01", "capital": "Machala"},
            {"code": "24", "name": "Santa Elena", "region_code": "01", "capital": "Santa Elena"},
            {"code": "23", "name": "Santo Domingo de los Tsáchilas", "region_code": "01", "capital": "Santo Domingo"},
            
            # SIERRA
            {"code": "01", "name": "Carchi", "region_code": "02", "capital": "Tulcán"},
            {"code": "10", "name": "Imbabura", "region_code": "02", "capital": "Ibarra"},
            {"code": "17", "name": "Pichincha", "region_code": "02", "capital": "Quito"},
            {"code": "02", "name": "Cotopaxi", "region_code": "02", "capital": "Latacunga"},
            {"code": "18", "name": "Tungurahua", "region_code": "02", "capital": "Ambato"},
            {"code": "03", "name": "Chimborazo", "region_code": "02", "capital": "Riobamba"},
            {"code": "06", "name": "Bolívar", "region_code": "02", "capital": "Guaranda"},
            {"code": "04", "name": "Cañar", "region_code": "02", "capital": "Azogues"},
            {"code": "19", "name": "Azuay", "region_code": "02", "capital": "Cuenca"},
            {"code": "14", "name": "Loja", "region_code": "02", "capital": "Loja"},
            
            # AMAZONÍA
            {"code": "21", "name": "Sucumbíos", "region_code": "03", "capital": "Nueva Loja"},
            {"code": "15", "name": "Napo", "region_code": "03", "capital": "Tena"},
            {"code": "16", "name": "Orellana", "region_code": "03", "capital": "Puerto Francisco de Orellana"},
            {"code": "22", "name": "Pastaza", "region_code": "03", "capital": "Puyo"},
            {"code": "12", "name": "Morona Santiago", "region_code": "03", "capital": "Macas"},
            {"code": "11", "name": "Zamora Chinchipe", "region_code": "03", "capital": "Zamora"},
            
            # INSULAR
            {"code": "20", "name": "Galápagos", "region_code": "04", "capital": "Puerto Baquerizo Moreno"},
        ]
        
        provinces = {}
        for p_data in provinces_data:
            region_code = p_data.pop("region_code")
            province = Province(
                **p_data,
                region_id=regions[region_code],
                is_active=True
            )
            db.add(province)
            db.flush()
            provinces[p_data["code"]] = province.id
            print(f"  ✅ {p_data['name']} (ID: {province.id})")
        
        db.commit()
        print(f"✅ {len(provinces_data)} provincias insertadas")
        
        # ============ CIUDADES ============
        print("\n🏙️  Insertando ciudades...")
        cities_data = [
            # Guayas
            {"name": "Guayaquil", "province_code": "09", "is_capital": True},
            {"name": "Durán", "province_code": "09"},
            {"name": "Milagro", "province_code": "09"},
            {"name": "Daule", "province_code": "09"},
            {"name": "Samborondón", "province_code": "09"},
            
            # Pichincha
            {"name": "Quito", "province_code": "17", "is_capital": True},
            {"name": "Cayambe", "province_code": "17"},
            {"name": "Sangolquí", "province_code": "17"},
            
            # Manabí
            {"name": "Portoviejo", "province_code": "08", "is_capital": True},
            {"name": "Manta", "province_code": "08"},
            {"name": "Bahía de Caráquez", "province_code": "08"},
            
            # Azuay
            {"name": "Cuenca", "province_code": "19", "is_capital": True},
            {"name": "Gualaceo", "province_code": "19"},
            
            # El Oro
            {"name": "Machala", "province_code": "07", "is_capital": True},
            {"name": "Pasaje", "province_code": "07"},
            
            # Los Ríos
            {"name": "Babahoyo", "province_code": "13", "is_capital": True},
            {"name": "Quevedo", "province_code": "13"},
            
            # Esmeraldas
            {"name": "Esmeraldas", "province_code": "05", "is_capital": True},
            {"name": "Atacames", "province_code": "05"},
            
            # Tungurahua
            {"name": "Ambato", "province_code": "18", "is_capital": True},
            {"name": "Baños de Agua Santa", "province_code": "18"},
            
            # Imbabura
            {"name": "Ibarra", "province_code": "10", "is_capital": True},
            {"name": "Otavalo", "province_code": "10"},
            
            # Loja
            {"name": "Loja", "province_code": "14", "is_capital": True},
            {"name": "Catamayo", "province_code": "14"},
            
            # Chimborazo
            {"name": "Riobamba", "province_code": "03", "is_capital": True},
            {"name": "Alausí", "province_code": "03"},
            
            # Cotopaxi
            {"name": "Latacunga", "province_code": "02", "is_capital": True},
            {"name": "La Maná", "province_code": "02"},
            
            # Santa Elena
            {"name": "Santa Elena", "province_code": "24", "is_capital": True},
            {"name": "Salinas", "province_code": "24"},
            {"name": "La Libertad", "province_code": "24"},
            
            # Santo Domingo
            {"name": "Santo Domingo", "province_code": "23", "is_capital": True},
        ]
        
        city_count = 0
        for c_data in cities_data:
            province_code = c_data.pop("province_code")
            city = City(
                **c_data,
                province_id=provinces[province_code],
                is_active=True
            )
            db.add(city)
            city_count += 1
        
        db.commit()
        print(f"✅ {city_count} ciudades insertadas")
        
        # Resumen final
        total_regions = db.query(Region).count()
        total_provinces = db.query(Province).count()
        total_cities = db.query(City).count()
        
        print("\n" + "="*60)
        print("🎉 SEED COMPLETADO EXITOSAMENTE")
        print("="*60)
        print(f"📊 Total Regiones:   {total_regions}")
        print(f"📊 Total Provincias: {total_provinces}")
        print(f"📊 Total Ciudades:   {total_cities}")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERROR durante el seed:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        import traceback
        print("\n🔍 Traceback completo:")
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_ecuador()