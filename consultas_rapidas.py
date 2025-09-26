#!/usr/bin/env python3
"""
Consultas Rápidas MongoDB Atlas - Ejemplos Prácticos
===================================================

Script para mostrar consultas básicas y útiles sobre las facturas
cargadas en MongoDB Atlas.

Autor: Efren Bohorquez
Universidad Central - Maestría en Analítica de Datos
"""

import os
from pymongo import MongoClient
from datetime import datetime
import json

def connect_to_mongodb():
    """Conecta a MongoDB Atlas usando las credenciales del .env"""
    
    # Leer variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    # Obtener URI de conexión
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        print("❌ Error: MONGO_URI no encontrado en .env")
        return None, None
    
    try:
        # Conectar a MongoDB
        client = MongoClient(mongo_uri)
        
        # Seleccionar base de datos
        db_name = os.getenv('DB_NAME', 'Facturas')
        db = client[db_name]
        
        # Probar conexión
        client.admin.command('ping')
        print(f"✅ Conectado exitosamente a MongoDB Atlas")
        print(f"🗃️ Base de datos: {db_name}")
        
        return client, db
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None, None

def mostrar_estadisticas_basicas(db):
    """Muestra estadísticas básicas de todas las colecciones"""
    
    print("\n" + "="*60)
    print("📊 ESTADÍSTICAS BÁSICAS DE LA BASE DE DATOS")
    print("="*60)
    
    colecciones = db.list_collection_names()
    total_documentos = 0
    
    for coleccion_nombre in colecciones:
        if not coleccion_nombre.startswith('system'):
            coleccion = db[coleccion_nombre]
            count = coleccion.count_documents({})
            total_documentos += count
            
            print(f"📁 {coleccion_nombre:20} → {count:,} documentos")
    
    print("-" * 60)
    print(f"📈 TOTAL GENERAL: {total_documentos:,} documentos")
    
    return colecciones

def consultas_por_totales(db, coleccion_nombre):
    """Ejemplos de consultas por rangos de totales"""
    
    print(f"\n💰 CONSULTAS POR TOTALES - {coleccion_nombre.upper()}")
    print("-" * 50)
    
    coleccion = db[coleccion_nombre]
    
    # Facturas con total mayor a $100,000
    facturas_altas = list(coleccion.find(
        {"total": {"$gt": 100000}}, 
        {"cliente": 1, "total": 1, "fecha": 1}
    ).limit(5))
    
    print("🔥 Top 5 facturas con total > $100,000:")
    for factura in facturas_altas:
        total = factura.get('total', 0)
        cliente = factura.get('cliente', 'No especificado')
        fecha = factura.get('fecha', 'No especificada')
        print(f"   💵 ${total:,} - {cliente} ({fecha})")
    
    # Promedio de totales
    pipeline = [
        {"$group": {
            "_id": None,
            "promedio": {"$avg": "$total"},
            "minimo": {"$min": "$total"},
            "maximo": {"$max": "$total"},
            "cantidad": {"$sum": 1}
        }}
    ]
    
    resultado = list(coleccion.aggregate(pipeline))
    if resultado:
        stats = resultado[0]
        print(f"\n📊 Estadísticas de totales:")
        print(f"   📈 Promedio: ${stats['promedio']:,.2f}")
        print(f"   📉 Mínimo: ${stats['minimo']:,}")
        print(f"   📈 Máximo: ${stats['maximo']:,}")
        print(f"   🧮 Cantidad: {stats['cantidad']:,}")

def consultas_por_clientes(db, coleccion_nombre):
    """Ejemplos de consultas agrupadas por cliente"""
    
    print(f"\n👥 ANÁLISIS POR CLIENTES - {coleccion_nombre.upper()}")
    print("-" * 50)
    
    coleccion = db[coleccion_nombre]
    
    # Top 10 clientes por cantidad de facturas
    pipeline = [
        {"$group": {
            "_id": "$cliente",
            "cantidad_facturas": {"$sum": 1},
            "total_gastado": {"$sum": "$total"}
        }},
        {"$sort": {"cantidad_facturas": -1}},
        {"$limit": 10}
    ]
    
    resultados = list(coleccion.aggregate(pipeline))
    
    print("🏆 Top 10 clientes por cantidad de facturas:")
    for i, cliente_data in enumerate(resultados, 1):
        cliente = cliente_data['_id'] or 'Cliente no especificado'
        cantidad = cliente_data['cantidad_facturas']
        total = cliente_data['total_gastado']
        print(f"   {i:2}. {cliente:30} → {cantidad:3} facturas (${total:,})")

def consultas_por_productos(db, coleccion_nombre):
    """Ejemplos de consultas sobre productos más vendidos"""
    
    print(f"\n🛒 PRODUCTOS MÁS VENDIDOS - {coleccion_nombre.upper()}")
    print("-" * 50)
    
    coleccion = db[coleccion_nombre]
    
    # Productos más vendidos (por cantidad)
    pipeline = [
        {"$unwind": "$productos"},
        {"$group": {
            "_id": "$productos.nombre",
            "cantidad_vendida": {"$sum": "$productos.cantidad"},
            "veces_comprado": {"$sum": 1},
            "ingreso_total": {"$sum": {"$multiply": ["$productos.cantidad", "$productos.precio"]}}
        }},
        {"$sort": {"cantidad_vendida": -1}},
        {"$limit": 10}
    ]
    
    try:
        resultados = list(coleccion.aggregate(pipeline))
        
        if resultados:
            print("🥇 Top 10 productos por cantidad vendida:")
            for i, producto in enumerate(resultados, 1):
                nombre = producto['_id'] or 'Producto sin nombre'
                cantidad = producto['cantidad_vendida']
                veces = producto['veces_comprado']
                ingreso = producto['ingreso_total']
                print(f"   {i:2}. {nombre:25} → {cantidad:4} unidades ({veces} facturas) ${ingreso:,}")
        else:
            print("   ℹ️  Esta colección no tiene estructura de productos detallada")
            
    except Exception as e:
        print(f"   ⚠️  Error al consultar productos: {e}")
        print("   ℹ️  Posible estructura de datos diferente")

def consulta_personalizada(db):
    """Permite hacer consultas personalizadas simples"""
    
    print(f"\n🔧 CONSULTA PERSONALIZADA")
    print("-" * 40)
    
    colecciones = db.list_collection_names()
    colecciones_filtradas = [c for c in colecciones if not c.startswith('system')]
    
    print("📁 Colecciones disponibles:")
    for i, col in enumerate(colecciones_filtradas, 1):
        count = db[col].count_documents({})
        print(f"   {i}. {col} ({count:,} docs)")
    
    try:
        opcion = int(input("\nSelecciona colección (número): ")) - 1
        if 0 <= opcion < len(colecciones_filtradas):
            coleccion_nombre = colecciones_filtradas[opcion]
            coleccion = db[coleccion_nombre]
            
            print(f"\n🔍 Ejemplo de documento de {coleccion_nombre}:")
            ejemplo = coleccion.find_one()
            if ejemplo:
                # Mostrar solo las claves principales
                print("   Campos disponibles:")
                for key in ejemplo.keys():
                    if key != '_id':
                        valor = ejemplo[key]
                        tipo = type(valor).__name__
                        if isinstance(valor, (str, int, float)):
                            print(f"   • {key} ({tipo}): {valor}")
                        else:
                            print(f"   • {key} ({tipo})")
            
            # Buscar por total específico
            print(f"\n💰 Buscar facturas con total mayor a:")
            try:
                minimo = float(input("   Ingresa monto mínimo: $"))
                resultados = list(coleccion.find(
                    {"total": {"$gt": minimo}}, 
                    {"cliente": 1, "total": 1, "fecha": 1}
                ).limit(5))
                
                print(f"\n🎯 Encontradas {len(resultados)} facturas (mostrando primeras 5):")
                for r in resultados:
                    cliente = r.get('cliente', 'N/A')
                    total = r.get('total', 0)
                    fecha = r.get('fecha', 'N/A')
                    print(f"   💵 ${total:,} - {cliente} ({fecha})")
                    
            except ValueError:
                print("   ⚠️  Valor no válido")
                
    except (ValueError, IndexError):
        print("   ⚠️  Opción no válida")

def main():
    """Función principal con menú interactivo"""
    
    print("🔍 CONSULTAS RÁPIDAS - MONGODB ATLAS")
    print("=" * 50)
    print("Universidad Central - Maestría en Analítica de Datos")
    print("Estudiante: Efren Bohorquez")
    print("=" * 50)
    
    # Conectar a la base de datos
    client, db = connect_to_mongodb()
    if not client:
        return
    
    try:
        while True:
            # Mostrar estadísticas básicas
            colecciones = mostrar_estadisticas_basicas(db)
            colecciones_filtradas = [c for c in colecciones if not c.startswith('system')]
            
            print(f"\n🔧 OPCIONES DE CONSULTA:")
            print("1. Análisis por totales (colección específica)")
            print("2. Análisis por clientes (colección específica)")
            print("3. Productos más vendidos (colección específica)")
            print("4. Consulta personalizada")
            print("0. Salir")
            
            try:
                opcion = input("\nSelecciona opción (0-4): ").strip()
                
                if opcion == "0":
                    print("👋 ¡Hasta luego!")
                    break
                    
                elif opcion in ["1", "2", "3"]:
                    print(f"\n📁 Selecciona colección:")
                    for i, col in enumerate(colecciones_filtradas, 1):
                        count = db[col].count_documents({})
                        print(f"   {i}. {col} ({count:,} docs)")
                    
                    try:
                        col_opcion = int(input("Número de colección: ")) - 1
                        if 0 <= col_opcion < len(colecciones_filtradas):
                            coleccion_nombre = colecciones_filtradas[col_opcion]
                            
                            if opcion == "1":
                                consultas_por_totales(db, coleccion_nombre)
                            elif opcion == "2":
                                consultas_por_clientes(db, coleccion_nombre)
                            elif opcion == "3":
                                consultas_por_productos(db, coleccion_nombre)
                        else:
                            print("⚠️  Opción no válida")
                    except ValueError:
                        print("⚠️  Número no válido")
                        
                elif opcion == "4":
                    consulta_personalizada(db)
                    
                else:
                    print("⚠️  Opción no válida")
                    
                input("\n⏎ Presiona Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
                
    finally:
        client.close()
        print("🔌 Conexión cerrada")

if __name__ == "__main__":
    main()