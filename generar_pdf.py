#!/usr/bin/env python3
"""
Convertidor de Markdown a PDF para el Informe del Parcial
========================================================

Este script convierte el informe técnico en markdown a un PDF profesional
usando reportlab y markdown2.

Autor: Efren Bohorquez
Fecha: 25 de septiembre de 2025
"""

import os
import sys
from datetime import datetime

def install_dependencies():
    """Instala las dependencias necesarias para la conversión a PDF."""
    packages = [
        'markdown',
        'reportlab', 
        'weasyprint'
    ]
    
    print("🔧 Instalando dependencias para conversión a PDF...")
    for package in packages:
        os.system(f'pip install {package}')
    print("✅ Dependencias instaladas correctamente")

def convert_to_pdf():
    """Convierte el archivo markdown a PDF usando weasyprint."""
    try:
        import markdown
        import weasyprint
        
        # Leer el archivo markdown
        with open('INFORME_PARCIAL_BIG_DATA.md', 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Convertir markdown a HTML
        html = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])
        
        # CSS para mejorar el formato
        css_styles = """
        <style>
        body {
            font-family: 'Times New Roman', serif;
            line-height: 1.6;
            margin: 40px;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 5px;
        }
        h3 {
            color: #2c3e50;
        }
        code {
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        pre {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
            overflow-x: auto;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        .page-break {
            page-break-before: always;
        }
        </style>
        """
        
        # HTML completo
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Informe Parcial Big Data - Efren Bohorquez</title>
            {css_styles}
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        # Convertir a PDF
        pdf_filename = f"INFORME_PARCIAL_BIG_DATA_Efren_Bohorquez_{datetime.now().strftime('%Y_%m_%d')}.pdf"
        weasyprint.HTML(string=full_html).write_pdf(pdf_filename)
        
        print(f"✅ PDF generado exitosamente: {pdf_filename}")
        return pdf_filename
        
    except ImportError as e:
        print(f"❌ Error: Falta instalar dependencias. Ejecuta install_dependencies() primero.")
        print(f"Error específico: {e}")
        return None
    except Exception as e:
        print(f"❌ Error al generar PDF: {e}")
        return None

def main():
    """Función principal del convertidor."""
    print("📄 GENERADOR DE PDF - INFORME PARCIAL BIG DATA")
    print("=" * 50)
    print(f"Estudiante: Efren Bohorquez")
    print(f"Universidad: Central")
    print(f"Materia: Big Data")
    print(f"Fecha: {datetime.now().strftime('%d de %B de %Y')}")
    print("=" * 50)
    
    # Verificar que existe el archivo markdown
    if not os.path.exists('INFORME_PARCIAL_BIG_DATA.md'):
        print("❌ Error: No se encuentra el archivo INFORME_PARCIAL_BIG_DATA.md")
        return
    
    # Instalar dependencias
    install_dependencies()
    
    # Convertir a PDF
    pdf_file = convert_to_pdf()
    
    if pdf_file:
        print(f"\n🎯 RESUMEN:")
        print(f"   📄 Archivo original: INFORME_PARCIAL_BIG_DATA.md")
        print(f"   📋 PDF generado: {pdf_file}")
        print(f"   📊 Listo para presentar al docente de Big Data")
        print(f"\n🚀 ¡El informe está listo para tu parcial!")
    else:
        print(f"\n❌ No se pudo generar el PDF. Revisa los errores anteriores.")

if __name__ == "__main__":
    main()