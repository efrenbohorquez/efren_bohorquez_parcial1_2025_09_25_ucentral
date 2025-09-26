#!/usr/bin/env python3
"""
Script para realizar consultas específicas sobre las facturas cargadas
"""
import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
from colorama import init, Fore, Style
import json
from typing import List, Dict, Any

init(autoreset=True)

class ConsultasFacturas:
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
            print(f"{Fore.GREEN}✅ Conectado a {self.database_name}{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error de conexión: {e}{Style.RESET_ALL}")
            return False
    
    def listar_colecciones(self):
        """Lista todas las colecciones disponibles"""
        print(f"\n{Fore.CYAN}📁 COLECCIONES DISPONIBLES:{Style.RESET_ALL}")
        colecciones = self.db.list_collection_names()
        
        for i, coleccion in enumerate(sorted(colecciones), 1):
            count = self.db[coleccion].count_documents({})
            print(f"   {i}. {Fore.YELLOW}{coleccion}{Style.RESET_ALL} ({count:,} documentos)")
        
        return colecciones
    
    def consulta_por_total(self, coleccion_name: str, total_min: float = None, total_max: float = None):
        """Consulta facturas por rango de total"""
        print(f"\n{Fore.GREEN}💰 CONSULTA POR TOTAL - {coleccion_name.upper()}{Style.RESET_ALL}")
        
        coleccion = self.db[coleccion_name]
        filtro = {}
        
        if total_min is not None or total_max is not None:
            filtro['total'] = {}
            if total_min is not None:
                filtro['total']['$gte'] = total_min
            if total_max is not None:
                filtro['total']['$lte'] = total_max
        
        try:
            # Contar documentos
            count = coleccion.count_documents(filtro)
            print(f"   📊 Facturas encontradas: {count:,}")
            
            if count > 0:
                # Estadísticas
                pipeline = [
                    {"$match": filtro},
                    {"$group": {
                        "_id": None,
                        "total_min": {"$min": "$total"},
                        "total_max": {"$max": "$total"},
                        "total_avg": {"$avg": "$total"},
                        "total_sum": {"$sum": "$total"}
                    }}
                ]
                
                stats = list(coleccion.aggregate(pipeline))
                if stats:
                    s = stats[0]
                    print(f"   💰 Total mínimo: ${s['total_min']:,.2f}")
                    print(f"   💰 Total máximo: ${s['total_max']:,.2f}")
                    print(f"   💰 Total promedio: ${s['total_avg']:,.2f}")
                    print(f"   💰 Suma total: ${s['total_sum']:,.2f}")
                
                # Mostrar algunos ejemplos
                ejemplos = list(coleccion.find(filtro).limit(3))
                print(f"\n   🔍 EJEMPLOS:")
                for i, factura in enumerate(ejemplos, 1):
                    print(f"      {i}. Factura: {factura.get('factura_num', 'N/A')} - Total: ${factura.get('total', 0):.2f}")
        
        except Exception as e:
            print(f"   ❌ Error en consulta: {e}")
    
    def consulta_por_cliente(self, coleccion_name: str, cliente_buscar: str = None):
        """Consulta facturas por cliente"""
        print(f"\n{Fore.GREEN}👥 CONSULTA POR CLIENTE - {coleccion_name.upper()}{Style.RESET_ALL}")
        
        coleccion = self.db[coleccion_name]
        
        try:
            if cliente_buscar:
                # Buscar cliente específico (case insensitive)
                filtro = {"cliente": {"$regex": cliente_buscar, "$options": "i"}}
                facturas = list(coleccion.find(filtro).limit(10))
                
                print(f"   🔍 Buscando: '{cliente_buscar}'")
                print(f"   📊 Facturas encontradas: {len(facturas)}")
                
                for factura in facturas:
                    print(f"      • {factura.get('cliente', 'N/A')} - ${factura.get('total', 0):.2f}")
            else:
                # Top 10 clientes más frecuentes
                pipeline = [
                    {"$match": {"cliente": {"$exists": True}}},
                    {"$group": {
                        "_id": "$cliente", 
                        "total_facturas": {"$sum": 1},
                        "total_monto": {"$sum": "$total"}
                    }},
                    {"$sort": {"total_facturas": -1}},
                    {"$limit": 10}
                ]
                
                top_clientes = list(coleccion.aggregate(pipeline))
                print(f"   🏆 TOP 10 CLIENTES:")
                
                for i, cliente in enumerate(top_clientes, 1):
                    print(f"      {i}. {cliente['_id']}: {cliente['total_facturas']} facturas, ${cliente.get('total_monto', 0):,.2f}")
        
        except Exception as e:
            print(f"   ❌ Error en consulta: {e}")
    
    def consulta_por_fecha(self, coleccion_name: str, fecha_inicio: str = None, fecha_fin: str = None):
        """Consulta facturas por rango de fechas"""
        print(f"\n{Fore.GREEN}📅 CONSULTA POR FECHA - {coleccion_name.upper()}{Style.RESET_ALL}")
        
        coleccion = self.db[coleccion_name]
        
        try:
            # Detectar campo de fecha
            muestra = coleccion.find_one()
            campos_fecha = ['fecha_hora', 'fecha', 'timestamp', 'date']
            campo_fecha = None
            
            for campo in campos_fecha:
                if muestra and campo in muestra:
                    campo_fecha = campo
                    break
            
            if not campo_fecha:
                print(f"   ⚠️  No se encontró campo de fecha")
                return
            
            print(f"   📅 Campo fecha usado: {campo_fecha}")
            
            # Construir filtro
            filtro = {}
            if fecha_inicio or fecha_fin:
                filtro[campo_fecha] = {}
                if fecha_inicio:
                    filtro[campo_fecha]['$gte'] = fecha_inicio
                if fecha_fin:
                    filtro[campo_fecha]['$lte'] = fecha_fin
            
            count = coleccion.count_documents(filtro)
            print(f"   📊 Facturas encontradas: {count:,}")
            
            if count > 0:
                # Mostrar ejemplos
                ejemplos = list(coleccion.find(filtro).limit(5))
                print(f"\n   🔍 EJEMPLOS:")
                for i, factura in enumerate(ejemplos, 1):
                    fecha = factura.get(campo_fecha, 'N/A')
                    total = factura.get('total', 0)
                    print(f"      {i}. {fecha} - ${total:.2f}")
        
        except Exception as e:
            print(f"   ❌ Error en consulta: {e}")
    
    def buscar_facturas_texto(self, coleccion_name: str, texto_buscar: str):
        """Búsqueda de texto en facturas"""
        print(f"\n{Fore.GREEN}🔍 BÚSQUEDA DE TEXTO - {coleccion_name.upper()}{Style.RESET_ALL}")
        
        coleccion = self.db[coleccion_name]
        
        try:
            # Buscar en campos de texto comunes
            filtro = {
                "$or": [
                    {"cliente": {"$regex": texto_buscar, "$options": "i"}},
                    {"factura_num": {"$regex": texto_buscar, "$options": "i"}},
                    {"descripcion": {"$regex": texto_buscar, "$options": "i"}},
                    {"comentarios": {"$regex": texto_buscar, "$options": "i"}}
                ]
            }
            
            facturas = list(coleccion.find(filtro).limit(10))
            print(f"   🔍 Buscando: '{texto_buscar}'")
            print(f"   📊 Facturas encontradas: {len(facturas)}")
            
            for i, factura in enumerate(facturas, 1):
                cliente = factura.get('cliente', 'N/A')
                factura_num = factura.get('factura_num', 'N/A')
                total = factura.get('total', 0)
                print(f"      {i}. {factura_num} - {cliente} - ${total:.2f}")
        
        except Exception as e:
            print(f"   ❌ Error en búsqueda: {e}")
    
    def resumen_por_coleccion(self, coleccion_name: str):
        """Resumen completo de una colección"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}📊 RESUMEN COMPLETO - {coleccion_name.upper()}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        coleccion = self.db[coleccion_name]
        
        try:
            # Estadísticas básicas
            total_docs = coleccion.count_documents({})
            print(f"{Fore.YELLOW}📄 Total documentos: {total_docs:,}{Style.RESET_ALL}")
            
            if total_docs == 0:
                print(f"{Fore.YELLOW}   ⚠️  Colección vacía{Style.RESET_ALL}")
                return
            
            # Muestra de documento
            muestra = coleccion.find_one()
            campos = list(muestra.keys()) if muestra else []
            print(f"{Fore.YELLOW}📋 Campos disponibles: {len(campos)}{Style.RESET_ALL}")
            print(f"   {', '.join(campos[:10])}{'...' if len(campos) > 10 else ''}")
            
            # Estadísticas de totales si existe el campo
            if 'total' in campos:
                pipeline = [
                    {"$match": {"total": {"$exists": True, "$type": "number"}}},
                    {"$group": {
                        "_id": None,
                        "total_min": {"$min": "$total"},
                        "total_max": {"$max": "$total"},
                        "total_avg": {"$avg": "$total"},
                        "total_sum": {"$sum": "$total"},
                        "count": {"$sum": 1}
                    }}
                ]
                
                stats = list(coleccion.aggregate(pipeline))
                if stats:
                    s = stats[0]
                    print(f"\n{Fore.GREEN}💰 ESTADÍSTICAS DE MONTOS:")
                    print(f"   📊 Facturas con monto: {s['count']:,}")
                    print(f"   💰 Monto mínimo: ${s['total_min']:,.2f}")
                    print(f"   💰 Monto máximo: ${s['total_max']:,.2f}")
                    print(f"   💰 Monto promedio: ${s['total_avg']:,.2f}")
                    print(f"   💰 Suma total: ${s['total_sum']:,.2f}{Style.RESET_ALL}")
            
            # Top clientes si existe el campo
            if 'cliente' in campos:
                pipeline = [
                    {"$match": {"cliente": {"$exists": True}}},
                    {"$group": {"_id": "$cliente", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 5}
                ]
                
                top_clientes = list(coleccion.aggregate(pipeline))
                if top_clientes:
                    print(f"\n{Fore.GREEN}👥 TOP 5 CLIENTES:")
                    for i, cliente in enumerate(top_clientes, 1):
                        print(f"   {i}. {cliente['_id']}: {cliente['count']} facturas{Style.RESET_ALL}")
        
        except Exception as e:
            print(f"   ❌ Error en resumen: {e}")
    
    def menu_interactivo(self):
        """Menú interactivo de consultas"""
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}🔍 CONSULTAS INTERACTIVAS DE FACTURAS")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        
        if not self.conectar():
            return
        
        colecciones = self.listar_colecciones()
        if not colecciones:
            print(f"{Fore.RED}❌ No hay colecciones disponibles{Style.RESET_ALL}")
            return
        
        while True:
            print(f"\n{Fore.CYAN}{'='*50}")
            print(f"{Fore.CYAN}🔧 OPCIONES DE CONSULTA")
            print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Resumen completo por colección")
            print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Consulta por rango de totales")
            print(f"{Fore.YELLOW}3.{Style.RESET_ALL} Consulta por cliente")
            print(f"{Fore.YELLOW}4.{Style.RESET_ALL} Consulta por fecha")
            print(f"{Fore.YELLOW}5.{Style.RESET_ALL} Búsqueda de texto")
            print(f"{Fore.YELLOW}6.{Style.RESET_ALL} Resumen de todas las colecciones")
            print(f"{Fore.YELLOW}0.{Style.RESET_ALL} Salir")
            
            try:
                opcion = input(f"\n{Fore.GREEN}Selecciona una opción (0-6): {Style.RESET_ALL}").strip()
                
                if opcion == '0':
                    print(f"{Fore.GREEN}👋 ¡Hasta luego!{Style.RESET_ALL}")
                    break
                
                elif opcion == '1':
                    print(f"\n{Fore.CYAN}Colecciones disponibles:{Style.RESET_ALL}")
                    for i, col in enumerate(sorted(colecciones), 1):
                        print(f"   {i}. {col}")
                    
                    col_num = input(f"{Fore.GREEN}Número de colección: {Style.RESET_ALL}").strip()
                    try:
                        col_idx = int(col_num) - 1
                        coleccion_elegida = sorted(colecciones)[col_idx]
                        self.resumen_por_coleccion(coleccion_elegida)
                    except (ValueError, IndexError):
                        print(f"{Fore.RED}❌ Opción inválida{Style.RESET_ALL}")
                
                elif opcion == '2':
                    print(f"\n{Fore.CYAN}Colecciones disponibles:{Style.RESET_ALL}")
                    for i, col in enumerate(sorted(colecciones), 1):
                        print(f"   {i}. {col}")
                    
                    col_num = input(f"{Fore.GREEN}Número de colección: {Style.RESET_ALL}").strip()
                    try:
                        col_idx = int(col_num) - 1
                        coleccion_elegida = sorted(colecciones)[col_idx]
                        
                        total_min = input(f"{Fore.GREEN}Total mínimo (Enter para omitir): ${Style.RESET_ALL}").strip()
                        total_max = input(f"{Fore.GREEN}Total máximo (Enter para omitir): ${Style.RESET_ALL}").strip()
                        
                        min_val = float(total_min) if total_min else None
                        max_val = float(total_max) if total_max else None
                        
                        self.consulta_por_total(coleccion_elegida, min_val, max_val)
                    except (ValueError, IndexError):
                        print(f"{Fore.RED}❌ Entrada inválida{Style.RESET_ALL}")
                
                elif opcion == '3':
                    print(f"\n{Fore.CYAN}Colecciones disponibles:{Style.RESET_ALL}")
                    for i, col in enumerate(sorted(colecciones), 1):
                        print(f"   {i}. {col}")
                    
                    col_num = input(f"{Fore.GREEN}Número de colección: {Style.RESET_ALL}").strip()
                    try:
                        col_idx = int(col_num) - 1
                        coleccion_elegida = sorted(colecciones)[col_idx]
                        
                        cliente = input(f"{Fore.GREEN}Nombre del cliente (Enter para top clientes): {Style.RESET_ALL}").strip()
                        cliente = cliente if cliente else None
                        
                        self.consulta_por_cliente(coleccion_elegida, cliente)
                    except (ValueError, IndexError):
                        print(f"{Fore.RED}❌ Opción inválida{Style.RESET_ALL}")
                
                elif opcion == '4':
                    print(f"\n{Fore.CYAN}Colecciones disponibles:{Style.RESET_ALL}")
                    for i, col in enumerate(sorted(colecciones), 1):
                        print(f"   {i}. {col}")
                    
                    col_num = input(f"{Fore.GREEN}Número de colección: {Style.RESET_ALL}").strip()
                    try:
                        col_idx = int(col_num) - 1
                        coleccion_elegida = sorted(colecciones)[col_idx]
                        
                        fecha_inicio = input(f"{Fore.GREEN}Fecha inicio (YYYY-MM-DD, Enter para omitir): {Style.RESET_ALL}").strip()
                        fecha_fin = input(f"{Fore.GREEN}Fecha fin (YYYY-MM-DD, Enter para omitir): {Style.RESET_ALL}").strip()
                        
                        fecha_inicio = fecha_inicio if fecha_inicio else None
                        fecha_fin = fecha_fin if fecha_fin else None
                        
                        self.consulta_por_fecha(coleccion_elegida, fecha_inicio, fecha_fin)
                    except (ValueError, IndexError):
                        print(f"{Fore.RED}❌ Opción inválida{Style.RESET_ALL}")
                
                elif opcion == '5':
                    print(f"\n{Fore.CYAN}Colecciones disponibles:{Style.RESET_ALL}")
                    for i, col in enumerate(sorted(colecciones), 1):
                        print(f"   {i}. {col}")
                    
                    col_num = input(f"{Fore.GREEN}Número de colección: {Style.RESET_ALL}").strip()
                    try:
                        col_idx = int(col_num) - 1
                        coleccion_elegida = sorted(colecciones)[col_idx]
                        
                        texto = input(f"{Fore.GREEN}Texto a buscar: {Style.RESET_ALL}").strip()
                        if texto:
                            self.buscar_facturas_texto(coleccion_elegida, texto)
                        else:
                            print(f"{Fore.RED}❌ Debes ingresar un texto{Style.RESET_ALL}")
                    except (ValueError, IndexError):
                        print(f"{Fore.RED}❌ Opción inválida{Style.RESET_ALL}")
                
                elif opcion == '6':
                    for coleccion in sorted(colecciones):
                        self.resumen_por_coleccion(coleccion)
                
                else:
                    print(f"{Fore.RED}❌ Opción inválida{Style.RESET_ALL}")
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}👋 ¡Hasta luego!{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        
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
    
    consultas = ConsultasFacturas(mongo_uri, database_name)
    consultas.menu_interactivo()

if __name__ == "__main__":
    main()