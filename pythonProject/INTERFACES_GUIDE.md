# 🖥️ Interfaces Gráficas - Sistema Bancario SINPE

## Resumen

Se han implementado **múltiples interfaces** para usar el Sistema Bancario SINPE, adaptándose a diferentes entornos y preferencias:

| Interfaz | Archivo | Dependencias | Estado | Recomendación |
|----------|---------|--------------|---------|---------------|
| **CLI Simple** | `cli_simple.py` | ✅ Solo Python estándar | ✅ **FUNCIONAL** | 🌟 **RECOMENDADA** |
| **GUI Tkinter** | `simple_gui.py` | ⚠️ tkinter (incluido en Python) | ⚠️ Requiere tkinter | Para sistemas con GUI |
| **GUI Completa** | `gui.py` | ⚠️ tkinter + requests | ⚠️ Requiere tkinter | Funcionalidad completa |
| **Interfaz Web** | `web_gui.py` | 🔧 Flask + requests | 🔧 En desarrollo | Navegador web |
| **Terminal Rico** | `main.py` | 🔧 rich + dependencias | ✅ **FUNCIONAL** | Interfaz original |

## 🌟 Interfaz Recomendada: CLI Simple

### Ejecutar
```bash
python cli_simple.py
```

### Características
- ✅ **Sin dependencias externas** - Solo Python estándar
- ✅ **Funciona en cualquier sistema** - Windows, Linux, macOS
- ✅ **Control integrado del servidor** - Inicia/detiene el backend automáticamente
- ✅ **Todas las funcionalidades principales**:
  - Gestión de usuarios (crear, listar)
  - Gestión de cuentas (crear, listar)  
  - Transferencias entre cuentas
  - Historial de transacciones
  - Verificación del estado del servidor

### Uso
1. **Ejecutar la interfaz**: `python cli_simple.py`
2. **Iniciar servidor**: Opción 1 del menú principal
3. **Esperar confirmación**: El sistema verifica que el servidor esté en línea
4. **Usar las funcionalidades**: Navegar por los menús para gestionar usuarios, cuentas y transferencias

## 🖥️ Interfaces Gráficas (Opcionales)

### GUI Simple (tkinter)
Si tkinter está disponible en su sistema:

```bash
python simple_gui.py
```

**Características**:
- Interfaz gráfica básica con ventanas y formularios
- Control del servidor integrado
- Pestañas para usuarios, cuentas y transferencias
- Funciona sin conexión a internet

### GUI Completa (tkinter)
Para funcionalidad completa con tkinter:

```bash
python gui.py
```

**Características**:
- Interfaz gráfica completa con todas las funcionalidades
- Múltiples pestañas organizadas
- Formularios con validación
- Listas interactivas
- Control avanzado del servidor

### Interfaz Web (Flask)
Para usar en navegador web:

```bash
python web_gui.py
```

Luego abrir: `http://localhost:5001`

**Características**:
- Interfaz web responsiva
- Funciona desde cualquier navegador
- API integrada
- Estilos CSS simples

## 🚀 Scripts de Inicio Rápido

### Windows
```batch
# Ejecutar con batch file
start_gui.bat

# O directamente
python run_gui.py
```

### Linux/macOS  
```bash
# Hacer ejecutable y correr
chmod +x run_gui.py
./run_gui.py

# O directamente
python3 cli_simple.py
```

## 🔧 Solución de Problemas

### Problema: "tkinter no está disponible"
**Solución**: Use la interfaz CLI simple
```bash
python cli_simple.py
```

### Problema: "requests no está disponible"  
**Solución**: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Problema: "No se puede conectar al servidor"
**Soluciones**:
1. Use la opción "Iniciar servidor" en cualquier interfaz
2. Verifique que el puerto 5000 esté libre
3. Use la opción "Estado del servidor" para diagnóstico

### Problema: Error de Python version
**Solución**: Use Python 3.7 o superior
```bash
python --version
```

## 📋 Funcionalidades Disponibles

### 👥 Gestión de Usuarios
- ✅ Crear usuarios con nombre, email, teléfono, contraseña
- ✅ Listar usuarios existentes
- ✅ Ver detalles completos de cada usuario

### 🏦 Gestión de Cuentas  
- ✅ Crear cuentas bancarias
- ✅ Asignar saldo inicial
- ✅ Vincular cuentas a usuarios
- ✅ Listar todas las cuentas con saldos

### 💸 Transferencias
- ✅ Transferencias entre cuentas internas
- ✅ Validación de saldos suficientes
- ✅ Registro completo de transacciones
- ✅ Descripciones personalizadas

### 📊 Transacciones
- ✅ Historial completo de transacciones
- ✅ Filtrado por cuentas
- ✅ Estados de transacciones
- ✅ Información detallada

### 🔧 Control del Sistema
- ✅ Iniciar/detener servidor Flask
- ✅ Verificar estado del servidor
- ✅ Health check del sistema
- ✅ Monitoreo en tiempo real

## 🎯 Casos de Uso

### Desarrollo y Pruebas
```bash
# Iniciar interfaz simple
python cli_simple.py

# 1. Iniciar servidor
# 2. Crear usuarios de prueba  
# 3. Crear cuentas con saldo
# 4. Realizar transferencias
# 5. Verificar transacciones
```

### Administración del Sistema
```bash
# Usar interfaz completa
python gui.py

# Gestión avanzada con formularios
# Control detallado del servidor
# Monitoreo en tiempo real
```

### Acceso Remoto
```bash
# Interfaz web
python web_gui.py

# Acceder desde navegador
# Funciona en red local
# Compatible con móviles
```

## 📝 Notas Técnicas

### Arquitectura
- **Frontend**: Interfaces diversas (CLI, GUI, Web)
- **Backend**: Flask API (puerto 5000)
- **Base de datos**: SQLite con SQLAlchemy
- **Comunicación**: HTTP REST API

### Seguridad
- Autenticación de usuarios
- Validación de datos
- HMAC para transferencias SINPE
- Sesiones seguras

### Escalabilidad
- API REST estándar
- Base de datos relacional
- Separación frontend/backend
- Compatible con otros bancos

## 🔮 Desarrollo Futuro

### Mejoras Planeadas
- [ ] Interfaz web mejorada con Bootstrap
- [ ] Aplicación móvil nativa
- [ ] Dashboard en tiempo real
- [ ] Reportes y estadísticas
- [ ] Integración con otros bancos
- [ ] Notificaciones push

### Contribuciones
Las interfaces están diseñadas para ser:
- ✅ **Modulares** - Fácil agregar nuevas funcionalidades
- ✅ **Extensibles** - Compatible con nuevos endpoints
- ✅ **Mantenibles** - Código limpio y documentado
- ✅ **Portables** - Funciona en diferentes sistemas

---

## 🎉 Conclusión

El Sistema Bancario SINPE ahora cuenta con **múltiples interfaces** que se adaptan a diferentes necesidades:

- **🌟 CLI Simple**: Para desarrollo rápido y sistemas sin GUI
- **🖥️ GUI Tkinter**: Para usuarios que prefieren interfaces gráficas
- **🌐 Web**: Para acceso remoto y colaboración
- **💻 Terminal Rico**: Para administradores avanzados

**Recomendación**: Comience con `python cli_simple.py` para pruebas rápidas y `python gui.py` para uso completo.

Todas las interfaces usan la **misma API backend**, garantizando consistencia y compatibilidad entre diferentes formas de acceso al sistema.
