#!/usr/bin/env python3
"""
Consultas Simples MongoDB Atlas
===============================

Script para hacer consultas básicas a las facturas cargadas.
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

def connect_to_mongodb():
    """Conecta a MongoDB Atlas."""
    load_dotenv()
    mongo_uri = os.getenv('MONGO_URI')
    db_name = os.getenv('DATABASE_NAME', 'Facturas')
    
    client = MongoClient(mongo_uri)
    db = client[db_name]
    return client, db

def mostrar_estadisticas(db):
    """Muestra estadísticas básicas de todas las colecciones."""
    print("📊 ESTADÍSTICAS GENERALES")
    print("=" * 40)
    
    collections = db.list_collection_names()
    total_docs = 0
    
    for col_name in collections:
        collection = db[col_name]
        count = collection.estimated_document_count()
        total_docs += count
        print(f"📁 {col_name:<20} → {count:,} documentos")
    
    print("-" * 40)
    print(f"📈 TOTAL: {total_docs:,} documentos")

def mostrar_muestra_documentos(db):
    """Muestra documentos de ejemplo de cada colección."""
    print("\n📄 MUESTRA DE DOCUMENTOS")
    print("=" * 40)
    
    collections = db.list_collection_names()
    
    for col_name in collections[:2]:  # Solo primeras 2 colecciones
        print(f"\n🔍 Colección: {col_name}")
        print("-" * 30)
        
        collection = db[col_name]
        sample_doc = collection.find_one()
        
        if sample_doc:
            print(f"   📋 Campos disponibles ({len(sample_doc)} campos):")
            for key, value in list(sample_doc.items())[:5]:  # Primeros 5 campos
                if key != '_id':
                    print(f"      • {key}: {str(value)[:50]}...")

def consultas_basicas(db):
    """Ejecuta consultas básicas útiles."""
    print("\n🔍 CONSULTAS BÁSICAS")
    print("=" * 40)
    
    collections = db.list_collection_names()
    col_name = collections[0]  # Primera colección
    collection = db[col_name]
    
    print(f"\n📊 Análisis de colección: {col_name}")
    print("-" * 30)
    
    # Contar documentos con diferentes condiciones
    try:
        # Buscar documentos con total > 100000 (si existe el campo)
        high_value = collection.count_documents({"total": {"$gt": 100000}})
        print(f"🔥 Facturas > $100,000: {high_value:,}")
    except:
        print("💡 Campo 'total' no encontrado para filtros por valor")
    
    try:
        # Buscar por cliente específico (si existe el campo)
        cliente_docs = collection.count_documents({"cliente": {"$exists": True}})
        print(f"👥 Documentos con cliente: {cliente_docs:,}")
    except:
        print("💡 Campo 'cliente' no encontrado")
    
    # Mostrar estructura de un documento
    sample = collection.find_one()
    if sample:
        print(f"\n📋 Estructura del documento:")
        for i, (key, value) in enumerate(sample.items()):
            if i < 8:  # Mostrar solo primeros 8 campos
                tipo = type(value).__name__
                valor_str = str(value)[:30] + "..." if len(str(value)) > 30 else str(value)
                print(f"   • {key} ({tipo}): {valor_str}")

def main():
    """Función principal."""
    print("🔍 CONSULTAS SIMPLES - MONGODB ATLAS")
    print("=" * 50)
    print("Universidad Central - Maestría en Analítica de Datos")
    print("Estudiante: Efren Bohorquez")
    print("=" * 50)
    
    try:
        # Conectar
        client, db = connect_to_mongodb()
        print("✅ Conectado exitosamente a MongoDB Atlas")
        
        # Ejecutar consultas
        mostrar_estadisticas(db)
        mostrar_muestra_documentos(db)
        consultas_basicas(db)
        
        print("\n" + "=" * 50)
        print("🎯 CONSULTAS COMPLETADAS")
        print("💡 Para consultas más específicas, usa MongoDB Compass")
        print("🌐 O accede a Atlas desde: https://cloud.mongodb.com")
        
        # Cerrar conexión
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()