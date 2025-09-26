# 🚀 Cargador Optimizado de Facturas a MongoDB Atlas

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green.svg)](https://mongodb.com)

Sistema de carga masiva optimizado para procesar archivos ZIP con facturas JSON y cargarlos a MongoDB Atlas con máximo rendimiento.

## 📋 Descripción del Proyecto

Este proyecto implementa un cargador de facturas altamente optimizado que:

- 📦 **Procesa archivos ZIP directamente en memoria** (sin extracción a disco)
- ⚡ **Carga en lotes de 8,000 documentos** con `insert_many()`
- 🔧 **Configuración optimizada de MongoDB** (w=1, bypass_document_validation)
- 📊 **Creación de índices SOLO al final** del proceso
- 🛡️ **Manejo de errores sin interrumpir lotes** completos
- 🎨 **Interfaz con colores y barras de progreso**

## 🎯 Resultados Obtenidos

### ✅ Carga Exitosa Completada

| 📁 Colección | 📄 Documentos | ⏱️ Tiempo | 🚀 Velocidad |
|--------------|---------------|-----------|-------------|
| `despensa_central` | 19,663 | 16.6s | 1,186 docs/s |
| `faladeella` | 19,929 | 17.2s | 1,156 docs/s |
| `frutiexpress` | 18,716 | 18.4s | 1,018 docs/s |
| `supermercado_exitazo` | 19,902 | 12.1s | 1,648 docs/s |

### 📊 Total: 78,210 documentos cargados en 64.3s (1,217 docs/segundo)

## � Estadísticas de la Base de Datos

### 🗄️ Estado Actual de MongoDB Atlas

| 📊 Métrica | 💎 Valor |
|------------|----------|
| **Total Documentos** | 159,393 facturas |
| **Total Colecciones** | 4 tiendas |
| **Tamaño Total** | ~197 MB |
| **Índices Creados** | 24 (6 por colección) |
| **Período de Datos** | 2020-2025 (5+ años) |

### 📁 Distribución por Colección

| 🏪 Tienda | 📄 Docs | 💾 Tamaño | 📦 Productos/Factura |
|-----------|---------|-----------|---------------------|
| `despensa_central` | 42,299 | 52.59 MB | ~1 producto |
| `faladeella` | 39,858 | 48.67 MB | ~15 productos |
| `frutiexpress` | 37,432 | 45.97 MB | ~11 productos |
| `supermercado_exitazo` | 39,804 | 49.83 MB | ~9 productos |

### 🔍 Características de los Datos

- **✅ Estructura Consistente**: 12 campos por documento
- **📅 Rango Temporal**: Enero 2020 - Septiembre 2025
- **🎯 Campos Clave**: `factura_num`, `fecha_hora`, `productos`
- **📊 Índices Optimizados**: Para consultas rápidas por archivo, fecha y número de factura

## �🛠️ Instalación

### Prerrequisitos

- Python 3.7 o superior
- Cuenta en MongoDB Atlas
- Archivo ZIP con facturas JSON

### 1. Clonar el repositorio

```bash
git clone https://github.com/efrenbohorquez/efren_bohorquez_parcial1_2025_09_25_ucentral.git
cd efren_bohorquez_parcial1_2025_09_25_ucentral
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Conexión a MongoDB Atlas
MONGO_URI=mongodb+srv://usuario:password@cluster0.xxxxx.mongodb.net/

# Configuración del archivo ZIP
ZIP_PATH=D:\Facturas.zip

# Nombre de la base de datos
DATABASE_NAME=Facturas
```

## 🚀 Uso

### Ejecución Básica

```bash
python cargador_optimizado.py
```

### Herramientas de Análisis

```bash
# Ver estadísticas completas de la base de datos
python estadisticas_db.py

# Realizar consultas simples y rápidas
python consultas_simples.py

# Consultas interactivas avanzadas
python consultas_facturas.py

# Diagnóstico de conexión y rendimiento
python diagnostico_conexion.py
```

## 📁 Estructura del Proyecto

```
proyecto-facturas-mongo/
├── cargador_optimizado.py              # Cargador principal optimizado
├── estadisticas_db.py                  # Estadísticas completas de BD
├── consultas_simples.py                # Consultas básicas funcionales
├── consultas_facturas.py               # Consultas interactivas avanzadas
├── diagnostico_conexion.py             # Herramienta de diagnóstico
├── generar_pdf_simple.py               # Generador de PDF académico
├── INFORME_PARCIAL_BIG_DATA.md         # Informe técnico completo
├── INFORME_PARCIAL_BIG_DATA.pdf        # PDF para presentación académica
├── ANALISIS_TECNICO_BIG_DATA.md        # Análisis técnico detallado
├── GUIA_CONSULTAS_MONGODB.md           # Guía de uso de consultas
├── requirements.txt                    # Dependencias del proyecto
├── .env.example                        # Ejemplo de configuración
├── .gitignore                          # Archivos ignorados
└── README.md                           # Este archivo
```

## ⚙️ Configuraciones de Optimización

### MongoDB Atlas

```python
MongoClient(
    mongo_uri,
    w=1,                    # Solo confirmación del primario
    maxPoolSize=100,        # Pool grande de conexiones
    retryWrites=True,       # Reintentos automáticos
    socketTimeoutMS=0       # Sin timeout para operaciones largas
)
```

### Inserción Masiva

```python
collection.insert_many(
    batch_data,
    ordered=False,                    # Inserciones paralelas
    bypass_document_validation=True   # Sin validación de esquema
)
```

## 📊 Características Técnicas

### Optimizaciones Implementadas

| 🔧 Optimización | 📝 Descripción | 🎯 Impacto |
|----------------|-----------------|-----------|
| **Lotes de 8K** | `insert_many()` con 8,000 docs | Reduce llamadas a BD |
| **w=1** | Solo confirmación primario | Máxima velocidad escritura |
| **ordered=False** | Inserciones paralelas | Paralelización automática |
| **bypass_validation** | Sin validación esquema | Reduce overhead |
| **Índices diferidos** | Creación al final | No ralentiza escritura |
| **ZIP en memoria** | Sin extracción disco | Elimina I/O innecesario |

### Estructura de Datos

Cada documento incluye metadatos automáticos:

```json
{
  "_source_file": "Despensa_Central/factura_001.json",
  "_source_folder": "Despensa_Central",
  // ... datos originales de la factura
}
```

### Índices Creados

- `_source_file` - Para rastrear archivo origen
- `_source_folder` - Para rastrear carpeta origen
- `(_source_folder, _source_file)` - Índice compuesto
- `factura_num` - Si existe en los datos
- `fecha_hora` - Si existe en los datos

## 📈 Rendimiento

### Métricas de Rendimiento

- **Velocidad promedio**: 1,217 documentos/segundo
- **Pico máximo**: 1,648 documentos/segundo
- **Eficiencia**: 100% de documentos procesados exitosamente
- **Tiempo total**: 64.3 segundos para 78,210 documentos

## 🔍 Scripts Adicionales

### `estadisticas_db.py`

Genera estadísticas completas de la base de datos:

- Número de documentos por colección
- Tamaños de colección
- Índices creados
- Estadísticas de rendimiento

### `consultas_facturas.py`

Sistema interactivo de consultas:

- Consultas por rango de totales
- Búsqueda por cliente
- Filtros por fecha
- Búsqueda de texto libre

## 🐛 Solución de Problemas

### Error de Conexión a MongoDB

```bash
❌ Error de conexión: [Errno -3] Temporary failure in name resolution
```

**Solución**: Verificar MONGO_URI en el archivo `.env`

### Archivo ZIP no encontrado

```bash
❌ No se encontraron archivos JSON
```

**Solución**: Verificar la ruta ZIP_PATH en el archivo `.env`

## 👨‍💻 Autor

## Efren Bohorquez

- GitHub: [@efrenbohorquez](https://github.com/efrenbohorquez)
- Universidad Central - Parcial 1
- Fecha: 25 de septiembre de 2025

---

⭐ **¡Si este proyecto te fue útil, no olvides darle una estrella!** ⭐