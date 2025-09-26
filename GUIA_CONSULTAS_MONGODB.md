📋 GUÍA: CÓMO CONSULTAR MONGODB ATLAS
===========================================

🌐 OPCIÓN 1: INTERFAZ WEB DE ATLAS (RECOMENDADO)
-----------------------------------------------

1. **Acceder a MongoDB Atlas:**
   • Ve a: https://cloud.mongodb.com/
   • Inicia sesión con tu cuenta de Atlas

2. **Navegar a tu base de datos:**
   • Selecciona tu cluster
   • Haz clic en "Browse Collections"
   • Verás tu base de datos "Facturas"

3. **Explorar las colecciones:**
   • despensa_central (22,636 documentos)
   • faladeella (19,929 documentos)  
   • frutiexpress (18,716 documentos)
   • supermercado_exitazo (19,902 documentos)

4. **Realizar consultas:**
   • Haz clic en cualquier colección
   • Usa el campo "Filter" para buscar
   • Ejemplos de filtros:
     - {"total": {"$gt": 50000}}     → Facturas > $50,000
     - {"cliente": "Juan"}           → Facturas de Juan
     - {"fecha": {"$regex": "2024"}} → Facturas del 2024

💻 OPCIÓN 2: MONGODB COMPASS (APLICACIÓN)
-----------------------------------------

1. **Descargar:**
   • https://www.mongodb.com/products/compass
   • Instalar la versión Community (gratuita)

2. **Conectar:**
   • URI de conexión (desde tu .env):
   • mongodb+srv://usuario:password@cluster.mongodb.net/Facturas

3. **Ventajas:**
   • Interfaz visual intuitiva
   • Gráficos automáticos
   • Editor de consultas con autocompletado
   • Análisis de esquemas
   • Índices visuales

🔧 OPCIÓN 3: CONSULTAS DESDE CÓDIGO PYTHON
------------------------------------------

Ejemplos de consultas básicas que SÍ funcionan:

```python
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()
client = MongoClient(os.getenv('MONGO_URI'))
db = client['Facturas']

# 1. Contar documentos por colección
for coleccion in db.list_collection_names():
    if not coleccion.startswith('system'):
        count = db[coleccion].count_documents({})
        print(f"{coleccion}: {count:,} documentos")

# 2. Ver estructura de un documento
coleccion = db['despensa_central']
ejemplo = coleccion.find_one()
print("Campos disponibles:", list(ejemplo.keys()))

# 3. Buscar facturas específicas
facturas_altas = coleccion.find({"total": {"$exists": True}}).limit(5)
for factura in facturas_altas:
    print(f"ID: {factura['_id']}")
    if 'total' in factura:
        print(f"Total: ${factura['total']:,}")
    if 'cliente' in factura:
        print(f"Cliente: {factura['cliente']}")

# 4. Consultas de agregación básicas
pipeline = [
    {"$match": {"total": {"$exists": True, "$ne": None}}},
    {"$group": {
        "_id": None,
        "cantidad": {"$sum": 1},
        "total_suma": {"$sum": "$total"}
    }}
]
resultado = list(coleccion.aggregate(pipeline))
print("Estadísticas:", resultado)
```

📊 CONSULTAS MÁS ÚTILES PARA ANÁLISIS
------------------------------------

**En Atlas Web Interface, usa estos filtros:**

1. **Facturas más altas:**
   {"total": {"$gt": 100000}}

2. **Facturas de un cliente específico:**
   {"cliente": {"$regex": "nombre_cliente", "$options": "i"}}

3. **Facturas por rango de fechas:**
   {"fecha": {"$gte": "2024-01-01", "$lte": "2024-12-31"}}

4. **Facturas con productos específicos:**
   {"productos.nombre": {"$regex": "producto", "$options": "i"}}

5. **Solo mostrar campos específicos (Projection):**
   Filtro: {}
   Projection: {"cliente": 1, "total": 1, "fecha": 1}

🎯 RECOMENDACIÓN FINAL
---------------------

**Para comenzar:**
1. Usa la interfaz web de Atlas (más fácil)
2. Explora tus datos visualmente
3. Cuando te familiarices, prueba MongoDB Compass
4. Para análisis avanzados, usa Python con las consultas básicas

**URLs importantes:**
• Atlas Web: https://cloud.mongodb.com/
• Compass: https://www.mongodb.com/products/compass
• Documentación: https://docs.mongodb.com/manual/

¡Tu base de datos tiene 81,183 documentos listos para consultar! 🚀