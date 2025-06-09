# Interfaz Gráfica del Sistema Bancario SINPE

## Descripción

Esta interfaz gráfica permite usar todas las funcionalidades del sistema bancario SINPE de manera visual y sencilla, sin necesidad de usar comandos de terminal o hacer peticiones HTTP directamente.

## Características

### 🖥️ **Interfaz Simple y Funcional**
- Diseño sin estilos complejos, enfocado en funcionalidad
- Formularios simples para todas las operaciones
- Listas y tablas para visualizar datos
- Control integrado del servidor Flask

### 📋 **Funcionalidades Incluidas**

#### 1. **Control del Servidor**
- Iniciar/Detener el servidor Flask
- Verificar estado del servidor
- Monitoreo en tiempo real

#### 2. **Gestión de Usuarios**
- Crear nuevos usuarios
- Ver lista de usuarios existentes
- Eliminar usuarios
- Formularios con validación

#### 3. **Gestión de Cuentas Bancarias**
- Crear cuentas con diferentes monedas (CRC, USD, EUR)
- Ver todas las cuentas
- Actualizar saldos
- Vincular cuentas a usuarios

#### 4. **Enlaces Telefónicos SINPE Móvil**
- Crear enlaces entre números de teléfono y cuentas
- Ver enlaces existentes
- Eliminar enlaces
- Gestión completa de SINPE móvil

#### 5. **Transferencias**
- Transferencias tradicionales entre cuentas
- Validación de números telefónicos
- Ver contactos de bancos externos
- Health check del sistema

#### 6. **Historial de Transacciones**
- Ver todas las transacciones
- Filtrar por número de cuenta
- Detalles completos de cada transacción
- Ordenamiento por fecha

#### 7. **Autenticación**
- Iniciar sesión
- Verificar estado de autenticación
- Cerrar sesión
- Control de acceso

## Instalación y Uso

### Prerequisitos
```bash
# Instalar dependencias
pip install -r requirements.txt
```

### Ejecutar la Interfaz Gráfica

#### Opción 1: Script de inicio
```bash
python run_gui.py
```

#### Opción 2: Directo
```bash
python gui.py
```

### Uso Básico

1. **Iniciar el Servidor**
   - Haga clic en "Iniciar Servidor" en la parte superior
   - Espere a que aparezca "✓ Servidor en línea"

2. **Crear Usuarios**
   - Vaya a la pestaña "Usuarios"
   - Complete el formulario y haga clic en "Crear Usuario"

3. **Crear Cuentas**
   - Vaya a la pestaña "Cuentas" 
   - Complete los datos y vincule a un usuario si desea

4. **Enlaces Telefónicos**
   - Pestaña "Enlaces Telefónicos"
   - Asocie números de teléfono con cuentas

5. **Realizar Transferencias**
   - Pestaña "Transferencias SINPE"
   - Use las transferencias tradicionales entre cuentas

6. **Ver Historial**
   - Pestaña "Transacciones"
   - Filtre por cuenta o vea todas las transacciones

## Estructura de la Interfaz

### Pestañas Principales

| Pestaña | Funcionalidad |
|---------|---------------|
| **Usuarios** | Gestión completa de usuarios del sistema |
| **Cuentas** | Administración de cuentas bancarias |
| **Enlaces Telefónicos** | Configuración SINPE móvil |
| **Transferencias SINPE** | Operaciones de transferencia |
| **Transacciones** | Historial y consultas |
| **Autenticación** | Login y control de sesión |

### Panel de Control del Servidor

En la parte superior de la interfaz encontrará:
- **Estado del Servidor**: Indicador visual del estado
- **Iniciar Servidor**: Arrancar el backend Flask
- **Detener Servidor**: Parar el servidor
- **Verificar Estado**: Comprobar conectividad

## API Endpoints Utilizados

La interfaz gráfica utiliza todos los endpoints existentes del sistema:

### Usuarios
- `GET /api/users` - Listar usuarios
- `POST /api/users` - Crear usuario
- `DELETE /api/users/{id}` - Eliminar usuario

### Cuentas
- `GET /api/accounts` - Listar cuentas
- `POST /api/accounts` - Crear cuenta
- `PUT /api/accounts/{id}/balance` - Actualizar saldo

### Enlaces Telefónicos
- `GET /api/phone-links` - Listar enlaces
- `POST /api/phone-links` - Crear enlace
- `DELETE /api/phone-links/{id}` - Eliminar enlace

### Transferencias
- `POST /api/transactions` - Crear transferencia
- `GET /api/transactions` - Listar transacciones
- `GET /api/validate/{phone}` - Validar teléfono

### Utilidades
- `GET /health` - Health check
- `GET /api/bank-contacts` - Contactos de bancos

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/logout` - Cerrar sesión
- `GET /api/auth/check` - Verificar estado

## Características Técnicas

### Tecnologías Utilizadas
- **Python 3.x**
- **Tkinter** (interfaz gráfica nativa)
- **Requests** (comunicación HTTP)
- **Threading** (control del servidor)

### Ventajas del Diseño
- ✅ **Sin dependencias externas complejas**
- ✅ **Interfaz nativa del sistema operativo**
- ✅ **Integración completa con el backend existente**
- ✅ **Control total del servidor desde la GUI**
- ✅ **Formularios con validación**
- ✅ **Manejo de errores robusto**

### Manejo de Errores
- Validación de campos obligatorios
- Mensajes de error informativos
- Verificación de conectividad
- Timeout en peticiones HTTP
- Limpieza automática de formularios

## Limitaciones Conocidas

1. **Transferencias SINPE Móvil Externas**: Requieren integración con otros bancos
2. **Estilos Visuales**: Diseño funcional sin elementos decorativos
3. **Tiempo Real**: No hay actualización automática de listas

## Troubleshooting

### Problemas Comunes

#### El servidor no inicia
```
Solución:
1. Verificar que el puerto 5000 esté libre
2. Asegurar que todas las dependencias estén instaladas
3. Revisar permisos de archivos
```

#### Error de conexión
```
Solución:
1. Verificar que el servidor esté ejecutándose
2. Comprobar la URL (http://localhost:5000)
3. Revisar firewall y antivirus
```

#### Campos vacíos en formularios
```
Solución:
1. Todos los campos marcados son obligatorios
2. Verificar formato de números (ID, montos)
3. Usar formatos válidos (email, teléfono)
```

## Desarrollo Futuro

### Posibles Mejoras
- [ ] Actualización automática de listas
- [ ] Temas visuales opcionales
- [ ] Exportación de reportes
- [ ] Notificaciones en tiempo real
- [ ] Configuración avanzada
- [ ] Múltiples instancias de servidor

## Soporte

Para reportar problemas o sugerir mejoras, revise:
1. Los logs del servidor Flask
2. La consola de errores de Python
3. El estado de conectividad del sistema

---

**Nota**: Esta interfaz está diseñada para ser funcional y directa, sin elementos visuales complejos, enfocándose en la usabilidad y las funcionalidades del sistema bancario SINPE.
