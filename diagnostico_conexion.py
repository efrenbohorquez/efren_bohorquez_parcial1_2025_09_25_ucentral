#!/usr/bin/env python3
"""
Diagnóstico de Conexión MongoDB Atlas
====================================

Script simple para diagnosticar problemas de conexión y rendimiento.
"""

import os
import time
from pymongo import MongoClient
from dotenv import load_dotenv

def test_connection():
    """Prueba la conexión paso a paso para identificar problemas."""
    
    print("🔍 DIAGNÓSTICO DE CONEXIÓN MONGODB ATLAS")
    print("=" * 50)
    
    # 1. Verificar archivo .env
    print("1️⃣ Verificando archivo .env...")
    load_dotenv()
    
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        print("❌ MONGO_URI no encontrado en .env")
        return False
    
    print("✅ MONGO_URI encontrado")
    
    # 2. Probar conexión básica
    print("\n2️⃣ Probando conexión básica...")
    start_time = time.time()
    
    try:
        # Timeout corto para detectar problemas rápido
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Ping simple
        client.admin.command('ping')
        connection_time = time.time() - start_time
        print(f"✅ Conexión exitosa en {connection_time:.2f} segundos")
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # 3. Verificar base de datos
    print("\n3️⃣ Verificando base de datos...")
    try:
        db_name = os.getenv('DATABASE_NAME', 'Facturas')
        db = client[db_name]
        collections = db.list_collection_names()
        print(f"✅ Base de datos '{db_name}' encontrada")
        print(f"📁 Colecciones: {collections}")
        
    except Exception as e:
        print(f"❌ Error accediendo a base de datos: {e}")
        return False
    
    # 4. Contar documentos (operación más lenta)
    print("\n4️⃣ Contando documentos...")
    start_time = time.time()
    
    try:
        total_docs = 0
        for collection_name in collections:
            collection = db[collection_name]
            count = collection.estimated_document_count()
            total_docs += count
            print(f"   📊 {collection_name}: {count:,} documentos")
        
        count_time = time.time() - start_time
        print(f"\n✅ Total: {total_docs:,} documentos")
        print(f"⏱️ Tiempo de conteo: {count_time:.2f} segundos")
        
        if count_time > 10:
            print("⚠️ ADVERTENCIA: El conteo es lento (>10s)")
            print("💡 Esto podría indicar problemas de red o índices")
        
    except Exception as e:
        print(f"❌ Error contando documentos: {e}")
        return False
    
    # 5. Consulta simple
    print("\n5️⃣ Probando consulta simple...")
    start_time = time.time()
    
    try:
        # Consulta a la primera colección disponible
        if collections:
            collection = db[collections[0]]
            sample_doc = collection.find_one()
            query_time = time.time() - start_time
            
            print(f"✅ Consulta exitosa en {query_time:.3f} segundos")
            if sample_doc:
                print(f"📄 Documento ejemplo tiene {len(sample_doc)} campos")
            
            if query_time > 2:
                print("⚠️ ADVERTENCIA: Consulta lenta (>2s)")
                print("💡 Posibles causas: red lenta, sin índices, cluster ocupado")
        
    except Exception as e:
        print(f"❌ Error en consulta: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNÓSTICO COMPLETADO")
    
    if connection_time > 3:
        print("⚠️ CONEXIÓN LENTA detectada")
        print("💡 Soluciones:")
        print("   • Verificar conexión a internet")
        print("   • Cambiar región del cluster Atlas")
        print("   • Usar VPN si hay restricciones geográficas")
    
    return True

if __name__ == "__main__":
    test_connection()