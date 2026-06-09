# 🖼️ FaceFrame Automator

> **Herramienta interna de procesamiento de imágenes** para la generación automatizada de fotos de perfil institucionales.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Pillow](https://img.shields.io/badge/Pillow-10.3%2B-green)](https://python-pillow.org)
[![License: MIT](https://img.shields.io/badge/Licencia-MIT-yellow)](LICENSE)
[![Status](https://img.shields.io/badge/Estado-MVP%20Fase%201-orange)]()

---

## 📋 ¿Qué es FaceFrame Automator?

**FaceFrame Automator** es una herramienta de escritorio local que ejecuta una interfaz web mediante **Streamlit** para automatizar la creación de fotos de perfil institucionales. Superpone un **marco institucional** (PNG con transparencia) sobre la **foto de un conductor** (JPG/PNG), genera una previsualización en tiempo real y permite descargar el resultado con un solo clic.

El objetivo a largo plazo es procesar hasta **3,000 fotos de conductores** de forma automatizada, con detección de rostros por IA y manipulación de fondos.

---

## ✨ Características del MVP (Fase 1)

| Función | Estado |
|---|---|
| Carga de marco institucional (PNG con alfa) | ✅ Implementado |
| Carga de foto del conductor (JPG/PNG) | ✅ Implementado |
| Redimensionado automático con recorte centrado | ✅ Implementado |
| Superposición de capas con preservación de alfa | ✅ Implementado |
| Previsualización en tiempo real | ✅ Implementado |
| Exportación y descarga en PNG | ✅ Implementado |
| Configuración de resolución de salida | ✅ Implementado |

---

## 🗺️ Roadmap (Próximas Fases)

### Fase 2 — Procesamiento Avanzado
- [ ] **Procesamiento en lote** (Bulk): Procesar carpetas completas de fotos automáticamente.
- [ ] **Centrado de rostros con IA**: Uso de OpenCV o MediaPipe para detectar el rostro y centrarlo antes del recorte.
- [ ] **Manipulación de fondos**: Detección y reemplazo del fondo azul institucional (inversión de color o cambio por imagen personalizada).

> 💡 El código del MVP ya incluye los **stubs documentados** para estas funciones. La arquitectura modular garantiza que la Fase 2 no rompa el MVP actual.

---

## 🗂️ Estructura del Proyecto

```
FaceFrame-Automator/
│
├── app.py              # Aplicación principal (Streamlit + Pillow)
├── requirements.txt    # Dependencias de Python
└── README.md           # Este archivo
```

---

## ⚙️ Requisitos del Sistema

- **Python**: 3.11 o superior
- **Sistema Operativo**: Windows 10/11 o Linux Ubuntu 22.04+
- **Conexión a internet**: Solo para la instalación inicial de dependencias

---

## 🚀 Instalación y Ejecución

### Opción A — Linux (Ubuntu / Debian)

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/FaceFrame-Automator.git
cd FaceFrame-Automator

# 2. Crear y activar el entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
streamlit run app.py
```

### Opción B — Windows (PowerShell o CMD)

```powershell
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/FaceFrame-Automator.git
cd FaceFrame-Automator

# 2. Crear y activar el entorno virtual
python -m venv .venv
.venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
streamlit run app.py
```

> ℹ️ Streamlit abrirá automáticamente tu navegador en `http://localhost:8501`.  
> Si no se abre, cópialo y pégalo manualmente en la barra de direcciones.

---

## 🖥️ Cómo Usar la Aplicación

1. **Cargar el Marco**: Sube el archivo PNG institucional con transparencia (canal alfa).
2. **Cargar la Foto**: Sube la foto JPG o PNG del conductor.
3. *(Opcional)* Ajusta la **resolución de salida** en el panel de configuración.
4. Haz clic en **"⚡ Procesar Imagen"**.
5. Revisa la **previsualización** del resultado.
6. Haz clic en **"⬇️ Descargar Imagen"** para guardar el archivo PNG.

---

## 📦 Dependencias

| Paquete | Versión mínima | Uso |
|---|---|---|
| `streamlit` | 1.35.0 | Interfaz de usuario web local |
| `Pillow` | 10.3.0 | Procesamiento y composición de imágenes |

> Las dependencias de Fase 2 (OpenCV, MediaPipe, rembg) están documentadas en `requirements.txt` como comentarios opcionales.

---

## 🔧 Solución de Problemas Comunes

### `ModuleNotFoundError: No module named 'streamlit'`
El entorno virtual no está activado. Ejecuta:
- Linux: `source .venv/bin/activate`
- Windows: `.venv\Scripts\activate`

### El navegador no se abre automáticamente
Abre manualmente `http://localhost:8501` en tu navegador.

### Error al procesar la imagen: "Modo RGBA"
Asegúrate de que el **marco sea un PNG con canal alfa** (transparencia). Un PNG sin transparencia no generará el efecto de superposición correcto.

### Puerto 8501 ocupado
```bash
# Cambiar el puerto de ejecución
streamlit run app.py --server.port 8502
```

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un **Issue** primero para discutir los cambios propuestos antes de crear un Pull Request.

---

## 📄 Licencia

Distribuido bajo la licencia **MIT**. Consulta el archivo `LICENSE` para más información.

---

<p align="center">
  Hecho con ❤️ usando <a href="https://streamlit.io">Streamlit</a> y <a href="https://python-pillow.org">Pillow</a>
</p>
