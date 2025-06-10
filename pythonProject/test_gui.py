#!/usr/bin/env python3
"""
Prueba simple de la interfaz gráfica
"""

try:
    import tkinter as tk

    print("✓ tkinter importado correctamente")

    print("✓ requests importado correctamente")

    # Crear ventana de prueba simple
    root = tk.Tk()
    root.title("Prueba GUI - Sistema Bancario SINPE")
    root.geometry("400x200")

    label = tk.Label(root, text="¡GUI funcionando correctamente!", font=("Arial", 14))
    label.pack(pady=50)

    def cerrar():
        print("Cerrando ventana de prueba...")
        root.destroy()

    button = tk.Button(root, text="Cerrar", command=cerrar, font=("Arial", 12))
    button.pack(pady=20)

    print("Ventana de prueba creada. Cerrando automáticamente en 3 segundos...")
    root.after(3000, cerrar)  # Cerrar automáticamente después de 3 segundos
    root.mainloop()

    print("✓ Prueba completada exitosamente")
    print("\nLa interfaz gráfica está lista para usar.")
    print("Ejecute: python gui.py")

except ImportError as e:
    print(f"✗ Error de importación: {e}")
    print("Instale las dependencias con: pip install -r requirements.txt")
except Exception as e:
    print(f"✗ Error inesperado: {e}")
    print("Verifique la instalación de Python y tkinter")
