#!/usr/bin/env python3
"""
Lanzador Universal - Sistema Bancario SINPE
Detecta automáticamente la mejor interfaz disponible
"""

import sys
import os
import subprocess

def check_tkinter():
    """Verificar si tkinter está disponible"""
    try:
        import tkinter
        return True
    except ImportError:
        return False

def check_flask():
    """Verificar si Flask está disponible"""
    try:
        import flask
        return True
    except ImportError:
        return False

def check_requests():
    """Verificar si requests está disponible"""
    try:
        import requests
        return True
    except ImportError:
        return False

def print_banner():
    """Mostrar banner"""
    print("=" * 60)
    print("🏦 SISTEMA BANCARIO SINPE - LANZADOR UNIVERSAL")
    print("=" * 60)
    print()

def print_status():
    """Mostrar estado de dependencias"""
    print("🔍 Detectando interfaces disponibles...")
    print()
    
    tkinter_available = check_tkinter()
    flask_available = check_flask()
    requests_available = check_requests()
    
    print(f"{'✅' if tkinter_available else '❌'} Tkinter (GUI): {'Disponible' if tkinter_available else 'No disponible'}")
    print(f"{'✅' if flask_available else '❌'} Flask (Web): {'Disponible' if flask_available else 'No disponible'}")
    print(f"{'✅' if requests_available else '❌'} Requests (HTTP): {'Disponible' if requests_available else 'No disponible'}")
    print(f"✅ CLI Simple: Siempre disponible")
    print()
    
    return {
        'tkinter': tkinter_available,
        'flask': flask_available, 
        'requests': requests_available
    }

def show_menu(available):
    """Mostrar menú de opciones"""
    print("📋 INTERFACES DISPONIBLES:")
    print("-" * 40)
    
    options = []
    
    # CLI Simple (siempre disponible)
    print("1. 🌟 CLI Simple (Recomendada)")
    print("   - Sin dependencias externas")
    print("   - Funciona en cualquier sistema")
    print("   - Archivo: cli_simple.py")
    options.append(('cli_simple.py', "CLI Simple"))
    print()
    
    # Terminal Rico (si rich está disponible)
    print("2. 💻 Terminal Rico (Original)")
    print("   - Interfaz colorida y avanzada")
    print("   - Requiere dependencias instaladas")
    print("   - Archivo: main.py")
    options.append(('main.py', "Terminal Rico"))
    print()
    
    # GUI Tkinter
    if available['tkinter']:
        print("3. 🖥️ GUI Simple (Tkinter)")
        print("   - Interfaz gráfica básica")
        print("   - Ventanas y formularios")
        print("   - Archivo: simple_gui.py")
        options.append(('simple_gui.py', "GUI Simple"))
        print()
        
        if available['requests']:
            print("4. 🎨 GUI Completa (Tkinter + Requests)")
            print("   - Interfaz gráfica completa")
            print("   - Todas las funcionalidades")
            print("   - Archivo: gui.py")
            options.append(('gui.py', "GUI Completa"))
            print()
    else:
        print("3. ❌ GUI (No disponible - tkinter no instalado)")
        print()
    
    # Interfaz Web
    if available['flask']:
        print(f"{'5' if available['tkinter'] and available['requests'] else '3'}. 🌐 Interfaz Web (Flask)")
        print("   - Acceso desde navegador")
        print("   - Puerto 5001")
        print("   - Archivo: web_gui.py")
        options.append(('web_gui.py', "Interfaz Web"))
        print()
    else:
        print(f"{'5' if available['tkinter'] else '3'}. ❌ Interfaz Web (No disponible - Flask no instalado)")
        print()
    
    print("0. Salir")
    print()
    
    return options

def install_dependencies():
    """Instalar dependencias"""
    print("📦 ¿Desea instalar las dependencias faltantes?")
    print("Esto instalará: Flask, requests, rich y otras dependencias")
    response = input("(s/n): ").strip().lower()
    
    if response in ['s', 'y', 'yes', 'si', 'sí']:
        print("\n⏳ Instalando dependencias...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True)
            print("✅ Dependencias instaladas correctamente")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error al instalar dependencias")
            return False
    else:
        print("ℹ️ Puede instalar manualmente con: pip install -r requirements.txt")
        return False

def launch_interface(script_name):
    """Lanzar interfaz seleccionada"""
    print(f"\n🚀 Iniciando {script_name}...")
    print("=" * 40)
    
    try:
        # Cambiar al directorio del script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # Ejecutar el script
        subprocess.run([sys.executable, script_name])
        
    except KeyboardInterrupt:
        print("\n👋 Interfaz cerrada por el usuario")
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {script_name}")
    except Exception as e:
        print(f"❌ Error al ejecutar {script_name}: {e}")

def main():
    """Función principal"""
    print_banner()
    
    # Verificar dependencias
    available = print_status()
    
    # Instalar dependencias si faltan
    missing_deps = not (available['flask'] and available['requests'])
    if missing_deps:
        print("⚠️ Algunas dependencias no están instaladas.")
        if install_dependencies():
            # Re-verificar después de la instalación
            available = print_status()
    
    while True:
        # Mostrar menú
        options = show_menu(available)
        
        try:
            choice = input("Seleccione una interfaz (número): ").strip()
            
            if choice == "0":
                print("\n👋 ¡Gracias por usar el Sistema Bancario SINPE!")
                break
                
            choice_num = int(choice) - 1
            
            if 0 <= choice_num < len(options):
                script_name, interface_name = options[choice_num]
                print(f"\n🎯 Ha seleccionado: {interface_name}")
                
                confirm = input("¿Continuar? (s/n): ").strip().lower()
                if confirm in ['s', 'y', 'yes', 'si', 'sí', '']:
                    launch_interface(script_name)
                    break
                else:
                    print("ℹ️ Selección cancelada\n")
                    continue
            else:
                print("❌ Opción inválida\n")
                
        except ValueError:
            print("❌ Por favor ingrese un número válido\n")
        except KeyboardInterrupt:
            print("\n\n👋 Aplicación terminada por el usuario")
            break

if __name__ == "__main__":
    main()
