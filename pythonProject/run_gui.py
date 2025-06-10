#!/usr/bin/env python3
"""
Script de inicio para la Interfaz Gráfica del Sistema Bancario SINPE
"""

import sys
import os

# Añadir el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from gui import main

    main()
except ImportError as e:
    print(f"Error al importar módulos: {e}")
    print("Asegúrese de que todas las dependencias estén instaladas:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"Error al ejecutar la aplicación: {e}")
    sys.exit(1)
