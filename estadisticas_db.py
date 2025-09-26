#!/usr/bin/env python3
"""
Script para generar estadísticas completas de la base de datos de facturas
"""
import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from colorama import init, Fore, Style
import json
from collections import defaultdict, Counter

init(autoreset=True)

class EstadisticasFacturas:
    def __init__(self, mongo_uri: str, database_name: str):
        self.mongo_uri = mongo_uri
        self.database_name = database_name
        self.client = None
        self.db = None
    
    def conectar(self):
        """Conecta a MongoDB"""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.database_name]
            self.client.admin.command('ping')
            print(f"{Fore.GREEN}✅ Conectado a MongoDB Atlas{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error de conexión: {e}{Style.RESET_ALL}")
            return False
    
    def estadisticas_generales(self):
        """Estadísticas generales de todas las colecciones"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}📊 ESTADÍSTICAS GENERALES DE LA BASE DE DATOS")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        
        colecciones = self.db.list_collection_names()
        total_documentos = 0
        
        print(f"{Fore.YELLOW}🗄️  Base de datos: {self.database_name}")
        print(f"{Fore.YELLOW}📅 Fecha consulta: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.YELLOW}📁 Total colecciones: {len(colecciones)}{Style.RESET_ALL}\n")
        
        for coleccion_name in sorted(colecciones):
            coleccion = self.db[coleccion_name]
            count = coleccion.count_documents({})
            total_documentos += count
            
            # Obtener tamaño aproximado
            stats = self.db.command("collStats", coleccion_name)
            size_mb = stats.get('size', 0) / (1024 * 1024)
            
            print(f"{Fore.GREEN}📁 {coleccion_name.upper()}")
            print(f"   📄 Documentos: {count:,}")
            print(f"   💾 Tamaño: {size_mb:.2f} MB")
            print(f"   📊 Índices: {stats.get('nindexes', 0)}")
            print()
        
        print(f"{Fore.BLUE}{'='*50}")
        print(f"{Fore.BLUE}🎯 TOTAL DOCUMENTOS: {total_documentos:,}")
        print(f"{Fore.BLUE}{'='*50}{Style.RESET_ALL}")
    
    def analizar_estructura_facturas(self):
        """Analiza la estructura de las facturas"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}🔍 ANÁLISIS DE ESTRUCTURA DE FACTURAS")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        
        colecciones = self.db.list_collection_names()
        
        for coleccion_name in sorted(colecciones):
            coleccion = self.db[coleccion_name]
            
            print(f"\n{Fore.GREEN}📊 ANÁLISIS DE: {coleccion_name.upper()}{Style.RESET_ALL}")
            
            # Muestra de documentos
            muestra = list(coleccion.find().limit(100))
            if not muestra:
                print(f"{Fore.YELLOW}   ⚠️  No hay documentos{Style.RESET_ALL}")
                continue
            
            # Analizar campos
            campos_encontrados = set()
            tipos_campos = defaultdict(Counter)
            
            for doc in muestra:
                for campo, valor in doc.items():
                    campos_encontrados.add(campo)
                    tipo = type(valor).__name__
                    tipos_campos[campo][tipo] += 1
            
            print(f"   📋 Campos encontrados: {len(campos_encontrados)}")
            
            # Mostrar campos más comunes
            campos_comunes = ['factura_num', 'fecha_hora', 'total', 'cliente', 'productos', 'subtotal', 'impuestos']
            campos_presentes = [c for c in campos_comunes if c in campos_encontrados]
            
            if campos_presentes:
                print(f"   🎯 Campos de negocio: {', '.join(campos_presentes)}")
            
            # Estadísticas específicas
            if 'total' in campos_encontrados:
                pipeline = [
                    {"$match": {"total": {"$exists": True, "$type": "number"}}},
                    {"$group": {
                        "_id": None,
                        "total_min": {"$min": "$total"},
                        "total_max": {"$max": "$total"},
                        "total_avg": {"$avg": "$total"},
                        "total_sum": {"$sum": "$total"}
                    }}
                ]
                resultado = list(coleccion.aggregate(pipeline))
                if resultado:
                    stats = resultado[0]
                    print(f"   💰 Total mínimo: ${stats['total_min']:,.2f}")
                    print(f"   💰 Total máximo: ${stats['total_max']:,.2f}")
                    print(f"   💰 Total promedio: ${stats['total_avg']:,.2f}")
                    print(f"   💰 Suma total: ${stats['total_sum']:,.2f}")
    
    def top_productos_y_clientes(self):
        """Analiza productos y clientes más frecuentes"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}🏆 TOP PRODUCTOS Y CLIENTES")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        
        colecciones = self.db.list_collection_names()
        
        for coleccion_name in sorted(colecciones):
            coleccion = self.db[coleccion_name]
            
            print(f"\n{Fore.GREEN}🏪 {coleccion_name.upper()}{Style.RESET_ALL}")
            
            # Top clientes por frecuencia
            try:
                pipeline_clientes = [
                    {"$match": {"cliente": {"$exists": True}}},
                    {"$group": {"_id": "$cliente", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 5}
                ]
                
                top_clientes = list(coleccion.aggregate(pipeline_clientes))
                if top_clientes:
                    print(f"   👥 TOP 5 CLIENTES:")
                    for i, cliente in enumerate(top_clientes, 1):
                        print(f"      {i}. {cliente['_id']}: {cliente['count']} facturas")
            except:
                print(f"   👥 No se pudo analizar clientes")
            
            # Análisis de productos si existe el campo
            try:
                muestra = coleccion.find_one({"productos": {"$exists": True}})
                if muestra and 'productos' in muestra:
                    print(f"   📦 Campo productos encontrado")
                    if isinstance(muestra['productos'], list) and muestra['productos']:
                        print(f"   📦 Estructura de productos: lista con {len(muestra['productos'])} items")
                    else:
                        print(f"   📦 Estructura de productos: {type(muestra['productos']).__name__}")
            except:
                print(f"   📦 No se pudo analizar productos")
    
    def analisis_temporal(self):
        """Análisis temporal de las facturas"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}📅 ANÁLISIS TEMPORAL")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        
        colecciones = self.db.list_collection_names()
        
        for coleccion_name in sorted(colecciones):
            coleccion = self.db[coleccion_name]
            
            print(f"\n{Fore.GREEN}⏰ {coleccion_name.upper()}{Style.RESET_ALL}")
            
            # Buscar campos de fecha
            campos_fecha = ['fecha_hora', 'fecha', 'timestamp', 'date']
            campo_fecha_encontrado = None
            
            muestra = coleccion.find_one()
            if muestra:
                for campo in campos_fecha:
                    if campo in muestra:
                        campo_fecha_encontrado = campo
                        break
                
                if campo_fecha_encontrado:
                    print(f"   📅 Campo fecha: {campo_fecha_encontrado}")
                    
                    # Obtener rango de fechas
                    try:
                        pipeline = [
                            {"$match": {campo_fecha_encontrado: {"$exists": True}}},
                            {"$group": {
                                "_id": None,
                                "fecha_min": {"$min": f"${campo_fecha_encontrado}"},
                                "fecha_max": {"$max": f"${campo_fecha_encontrado}"}
                            }}
                        ]
                        
                        resultado = list(coleccion.aggregate(pipeline))
                        if resultado:
                            rango = resultado[0]
                            print(f"   📅 Fecha más antigua: {rango['fecha_min']}")
                            print(f"   📅 Fecha más reciente: {rango['fecha_max']}")
                    except:
                        print(f"   📅 No se pudo calcular rango de fechas")
                else:
                    print(f"   📅 No se encontró campo de fecha")
    
    def generar_reporte_completo(self):
        """Genera reporte completo"""
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}📋 REPORTE COMPLETO DE FACTURAS - BASE DE DATOS")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        
        if not self.conectar():
            return
        
        try:
            self.estadisticas_generales()
            self.analizar_estructura_facturas()
            self.top_productos_y_clientes()
            self.analisis_temporal()
            
            print(f"\n{Fore.GREEN}{'='*70}")
            print(f"{Fore.GREEN}✅ REPORTE COMPLETADO")
            print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️  Interrumpido por usuario{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        finally:
            if self.client:
                self.client.close()

def main():
    """Función principal"""
    load_dotenv()
    
    mongo_uri = os.getenv('MONGO_URI')
    database_name = os.getenv('DATABASE_NAME', 'Facturas')
    
    if not mongo_uri:
        print(f"{Fore.RED}❌ MONGO_URI no configurado en .env{Style.RESET_ALL}")
        return
    
    estadisticas = EstadisticasFacturas(mongo_uri, database_name)
    estadisticas.generar_reporte_completo()

if __name__ == "__main__":
    main()