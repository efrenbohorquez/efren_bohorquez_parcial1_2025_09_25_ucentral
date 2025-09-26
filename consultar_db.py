#!/usr/bin/env python3
"""
Consultas Simples MongoDB Atlas
==============================

Script básico para consultar las facturas cargadas.
Incluye solo consultas que funcionan correctamente.

Autor: Efren Bohorquez
Universidad Central - Maestría en Analítica de Datos
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

def conectar_mongodb():
    """Conecta a MongoDB Atlas"""
    load_dotenv()
    
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        print("❌ Error: MONGO_URI no encontrado en .env")
        return None, None
    
    try:
        client = MongoClient(mongo_uri)
        db = client['Facturas']
        
        # Probar conexión
        client.admin.command('ping')
        print("✅ Conectado a MongoDB Atlas")
        print(f"🗃️ Base de datos: Facturas")
        
        return client, db
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None, None

def mostrar_resumen(db):
    """Muestra resumen básico de todas las colecciones"""
    
    print("\n" + "="*50)
    print("📊 RESUMEN DE LA BASE DE DATOS")
    print("="*50)
    
    colecciones = db.list_collection_names()
    total_docs = 0
    
    for col_name in colecciones:
        if not col_name.startswith('system'):
            count = db[col_name].count_documents({})
            total_docs += count
            print(f"📁 {col_name:20} → {count:,} documentos")
    
    print("-" * 50)
    print(f"📈 TOTAL: {total_docs:,} documentos")
    
    return [c for c in colecciones if not c.startswith('system')]

def ver_ejemplo_documento(db, coleccion_nombre):
    """Muestra la estructura de un documento"""
    
    print(f"\n🔍 ESTRUCTURA DE DOCUMENTO - {coleccion_nombre}")
    print("-" * 40)
    
    coleccion = db[coleccion_nombre]
    documento = coleccion.find_one()
    
    if documento:
        print("📋 Campos disponibles:")
        for campo, valor in documento.items():
            if campo != '_id':
                tipo = type(valor).__name__
                if isinstance(valor, (str, int, float, bool)):
                    valor_str = str(valor)[:50] + "..." if len(str(valor)) > 50 else str(valor)
                    print(f"   • {campo:15} ({tipo:10}) → {valor_str}")
                elif isinstance(valor, list):
                    print(f"   • {campo:15} ({tipo:10}) → Lista con {len(valor)} elementos")
                elif isinstance(valor, dict):
                    print(f"   • {campo:15} ({tipo:10}) → Objeto con {len(valor)} campos")
                else:
                    print(f"   • {campo:15} ({tipo:10})")
    else:
        print("   ⚠️ No se encontraron documentos")

def buscar_documentos(db, coleccion_nombre, limite=5):
    """Busca y muestra algunos documentos de ejemplo"""
    
    print(f"\n📄 PRIMEROS {limite} DOCUMENTOS - {coleccion_nombre}")
    print("-" * 50)
    
    coleccion = db[coleccion_nombre]
    documentos = list(coleccion.find({}).limit(limite))
    
    for i, doc in enumerate(documentos, 1):
        print(f"\n🔖 Documento {i}:")
        for campo, valor in doc.items():
            if campo != '_id':
                if isinstance(valor, (str, int, float, bool)):
                    print(f"   {campo}: {valor}")
                elif isinstance(valor, list):
                    print(f"   {campo}: Lista con {len(valor)} elementos")
                elif isinstance(valor, dict):
                    print(f"   {campo}: Objeto")

def buscar_por_campo(db, coleccion_nombre):
    """Busca documentos que tengan un campo específico"""
    
    print(f"\n🔎 BUSCAR POR CAMPO - {coleccion_nombre}")
    print("-" * 40)
    
    campo = input("Ingresa el nombre del campo a buscar: ").strip()
    
    if not campo:
        print("   ⚠️ Campo vacío")
        return
    
    coleccion = db[coleccion_nombre]
    
    # Buscar documentos que tengan este campo
    filtro = {campo: {"$exists": True, "$ne": None}}
    documentos = list(coleccion.find(filtro).limit(3))
    
    if documentos:
        print(f"✅ Encontrados documentos con el campo '{campo}':")
        for i, doc in enumerate(documentos, 1):
            valor = doc.get(campo, "N/A")
            print(f"   {i}. {campo}: {valor}")
    else:
        print(f"❌ No se encontraron documentos con el campo '{campo}'")

def main():
    """Función principal"""
    
    print("🔍 CONSULTAS SIMPLES - MONGODB ATLAS")
    print("=" * 50)
    print("Universidad Central - Maestría en Analítica de Datos")
    print("Estudiante: Efren Bohorquez")
    print("=" * 50)
    
    # Conectar
    client, db = conectar_mongodb()
    if not client:
        return
    
    try:
        while True:
            # Mostrar resumen
            colecciones = mostrar_resumen(db)
            
            print(f"\n🔧 OPCIONES:")
            print("1. Ver estructura de documento")
            print("2. Ver documentos de ejemplo")
            print("3. Buscar por campo específico")
            print("0. Salir")
            
            opcion = input("\nSelecciona opción (0-3): ").strip()
            
            if opcion == "0":
                print("👋 ¡Hasta luego!")
                break
                
            elif opcion in ["1", "2", "3"]:
                print(f"\n📁 Selecciona colección:")
                for i, col in enumerate(colecciones, 1):
                    count = db[col].count_documents({})
                    print(f"   {i}. {col} ({count:,} docs)")
                
                try:
                    col_num = int(input("Número de colección: ")) - 1
                    if 0 <= col_num < len(colecciones):
                        coleccion_nombre = colecciones[col_num]
                        
                        if opcion == "1":
                            ver_ejemplo_documento(db, coleccion_nombre)
                        elif opcion == "2":
                            buscar_documentos(db, coleccion_nombre)
                        elif opcion == "3":
                            buscar_por_campo(db, coleccion_nombre)
                    else:
                        print("⚠️ Opción no válida")
                except ValueError:
                    print("⚠️ Número no válido")
            else:
                print("⚠️ Opción no válida")
            
            input("\n⏎ Presiona Enter para continuar...")
            
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
    finally:
        client.close()
        print("🔌 Conexión cerrada")

if __name__ == "__main__":
    main()