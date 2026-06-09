"""
FaceFrame Automator - app.py
============================
Herramienta de procesamiento de imágenes para superposición de marcos
institucionales sobre fotos de conductores.

Autor:   [Tu nombre / Equipo]
Versión: 1.1.0 (MVP - Fase 1 + Ajuste de posición)
Fecha:   2026

Arquitectura Modular:
    - Fase 1 (MVP): Procesamiento individual con Streamlit + Pillow.
                    Incluye ajuste manual de posición (offset X/Y) y zoom
                    para alinear el rostro con la ventana del marco.
    - Fase 2 (Roadmap): Procesamiento en lote, centrado de rostros con IA,
                        manipulación de fondos (ver placeholders al final del archivo).
"""

import io
import streamlit as st
from PIL import Image

# =============================================================================
# CONSTANTES Y CONFIGURACIÓN
# =============================================================================

APP_TITLE = "FaceFrame Automator"
APP_ICON = "🖼️"
OUTPUT_FORMAT = "PNG"
OUTPUT_FILENAME = "conductor_con_marco.png"

# Tamaño de salida estándar (puede volverse configurable en Fase 2)
DEFAULT_OUTPUT_SIZE = (800, 800)


# =============================================================================
# MÓDULO DE PROCESAMIENTO DE IMÁGENES (CORE)
# Estas funciones son el corazón del MVP y están diseñadas para ser
# reutilizadas y extendidas en Fase 2 sin romper la lógica existente.
# =============================================================================

def load_image(uploaded_file) -> Image.Image | None:
    """
    Carga un archivo subido por Streamlit y lo convierte en un objeto PIL Image.

    Args:
        uploaded_file: Objeto UploadedFile de Streamlit (BytesIO-like).

    Returns:
        PIL.Image.Image si la carga es exitosa, None en caso de error.
    """
    if uploaded_file is None:
        return None
    try:
        image = Image.open(uploaded_file)
        return image
    except Exception as e:
        st.error(f"Error al cargar la imagen: {e}")
        return None


def resize_to_fill(
    image: Image.Image,
    target_size: tuple[int, int],
    zoom: float = 1.0,
    offset_x: int = 0,
    offset_y: int = 0,
) -> Image.Image:
    """
    Redimensiona la imagen y la ubica en un lienzo (canvas) transparente.
    Permite mover la foto libremente, incluso fuera de los bordes.

    Estrategia "Canvas Libre":
        1. Escala la imagen para cubrir el target (cover) × zoom del usuario.
        2. Crea un lienzo RGBA transparente del tamaño `target_size`.
        3. Calcula la posición para centrar la imagen escalada en el lienzo.
        4. Suma `offset_x` y `offset_y` a esa posición para el desplazamiento libre.
        5. Pega la imagen en el lienzo.

    Args:
        image:       Imagen PIL a redimensionar.
        target_size: Tupla (ancho, alto) del tamaño objetivo.
        zoom:        Factor de zoom (1.0 = tamaño base).
        offset_x:    Píxeles de desplazamiento horizontal (sin límites).
        offset_y:    Píxeles de desplazamiento vertical (sin límites).

    Returns:
        PIL.Image.Image del tamaño target_size (modo RGBA).
    """
    target_w, target_h = target_size
    orig_w, orig_h = image.size

    # 1. Escala base (cover) × zoom del usuario
    base_scale = max(target_w / orig_w, target_h / orig_h)
    scale = base_scale * max(zoom, 1.0)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)

    resized = image.resize((new_w, new_h), Image.LANCZOS)
    if resized.mode != 'RGBA':
        resized = resized.convert('RGBA')

    # 2. Crear lienzo transparente
    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))

    # 3. Posición base (centrada)
    base_x = (target_w - new_w) // 2
    base_y = (target_h - new_h) // 2

    # 4. Sumar el desplazamiento manual del usuario
    final_x = base_x + offset_x
    final_y = base_y + offset_y

    # 5. Pegar la imagen en el lienzo (el canal alfa se respeta)
    canvas.paste(resized, (final_x, final_y), resized)

    return canvas


def overlay_frame(
    driver_photo: Image.Image,
    frame: Image.Image,
    output_size: tuple[int, int] = DEFAULT_OUTPUT_SIZE,
    zoom: float = 1.0,
    offset_x: int = 0,
    offset_y: int = 0,
) -> Image.Image:
    """
    Composición principal: superpone el marco institucional (Capa 1 - Superior)
    sobre la foto del conductor (Capa 2 - Inferior).

    Proceso:
        1. Convierte la foto del conductor a RGBA para operaciones de composición.
        2. Redimensiona la foto con zoom y offset para alinear el rostro
           con la ventana transparente del marco.
        3. Redimensiona el marco para que coincida exactamente con el canvas.
        4. Aplana las capas usando `alpha_composite`.

    Args:
        driver_photo: Imagen PIL del conductor (JPG o PNG).
        frame:        Imagen PIL del marco con canal alfa (PNG con transparencia).
        output_size:  Tupla (ancho, alto) del resultado final.
        zoom:         Factor de zoom sobre la foto del conductor (>= 1.0).
        offset_x:     Desplazamiento horizontal de la foto en píxeles.
        offset_y:     Desplazamiento vertical de la foto en píxeles.

    Returns:
        PIL.Image.Image con la composición final en modo RGBA.

    # FASE 2 - INVERSIÓN/CAMBIO DE FONDO:
    # Antes de llamar a esta función, pasar `driver_photo` por
    # `replace_blue_background(driver_photo, new_bg_color)` para manipular
    # el fondo azul institucional.
    """
    # --- Paso 1: Preparar el canvas base con la foto del conductor ---
    driver_rgba = driver_photo.convert("RGBA")
    base = resize_to_fill(driver_rgba, output_size, zoom=zoom,
                          offset_x=offset_x, offset_y=offset_y)

    # --- Paso 2: Preparar el marco ---
    # El marco DEBE tener canal alfa. Si viene como RGB, se asume opaco.
    frame_rgba = frame.convert("RGBA")
    frame_resized = frame_rgba.resize(output_size, Image.LANCZOS)

    # --- Paso 3: Composición (Marco sobre Foto) ---
    # alpha_composite respeta el canal alfa del marco para la transparencia.
    result = Image.alpha_composite(base, frame_resized)

    return result


def export_image_to_bytes(image: Image.Image, fmt: str = OUTPUT_FORMAT) -> bytes:
    """
    Convierte un objeto PIL Image a bytes listos para descarga.

    Args:
        image: PIL.Image.Image a serializar.
        fmt:   Formato de exportación ('PNG', 'JPEG', etc.).

    Returns:
        bytes del archivo de imagen serializado.
    """
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    buffer.seek(0)
    return buffer.getvalue()


# =============================================================================
# INTERFAZ DE USUARIO - STREAMLIT
# =============================================================================

def configure_page():
    """Configura los metadatos y el estilo global de la página Streamlit."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def render_header():
    """Renderiza el encabezado principal de la aplicación."""
    st.title(f"{APP_ICON} {APP_TITLE}")
    st.markdown(
        "**Superposición automática de marcos institucionales** sobre fotos de conductores. "
        "Carga las imágenes, previsualiza y descarga el resultado."
    )
    st.divider()


def render_upload_section() -> tuple:
    """
    Renderiza la sección de carga de archivos con dos columnas:
    - Columna izquierda: Marco institucional (PNG con transparencia).
    - Columna derecha:   Foto del conductor (JPG/PNG).

    Returns:
        Tupla (frame_file, photo_file) con los objetos UploadedFile de Streamlit.
        Cualquiera puede ser None si el usuario aún no ha subido el archivo.
    """
    st.subheader("📂 Paso 1: Cargar Imágenes")

    col_frame, col_photo = st.columns(2)

    with col_frame:
        st.markdown("**🖼️ Marco Institucional** *(Capa Superior)*")
        st.caption("Formato requerido: PNG con transparencia (canal alfa)")
        frame_file = st.file_uploader(
            label="Seleccionar Marco",
            type=["png"],
            key="frame_uploader",
            help="El marco debe ser un PNG con fondo transparente para que la superposición sea correcta.",
        )
        if frame_file:
            st.image(frame_file, caption="Marco cargado", use_container_width=True)

    with col_photo:
        st.markdown("**👤 Foto del Conductor** *(Capa Base)*)")
        st.caption("Formatos aceptados: JPG, JPEG, PNG")
        photo_file = st.file_uploader(
            label="Seleccionar Foto",
            type=["jpg", "jpeg", "png"],
            key="photo_uploader",
            help="La foto se escalará automáticamente para cubrir el canvas de salida.",
        )
        if photo_file:
            st.image(photo_file, caption="Foto cargada", use_container_width=True)

    return frame_file, photo_file


def render_settings_section() -> dict:
    """
    Renderiza los ajustes de procesamiento:
      - Resolución de salida (ancho x alto).
      - Ajuste de posición de la foto (offset X/Y y zoom) para alinear
        el rostro del conductor con la ventana transparente del marco.

    Returns:
        Diccionario con las claves:
            'output_size' : tuple[int, int]  — (ancho, alto) del canvas.
            'zoom'        : float            — factor de zoom (>= 1.0).
            'offset_x'    : int              — desplazamiento horizontal (px).
            'offset_y'    : int              — desplazamiento vertical (px).

    # FASE 2 - CONFIGURACIÓN DE LOTE:
    # Agregar aquí un st.expander con opciones avanzadas de batch processing:
    #   - Selector de carpeta de entrada.
    #   - Selector de carpeta de salida.
    #   - Opción de prefijo para nombres de archivo.
    """
    st.subheader("⚙️ Paso 2: Configuración")

    # --- Panel 1: Resolución de salida ---
    with st.expander("📐 Resolución de salida", expanded=False):
        col_w, col_h = st.columns(2)
        with col_w:
            output_w = st.number_input(
                "Ancho (px)", min_value=100, max_value=4096,
                value=DEFAULT_OUTPUT_SIZE[0], step=50
            )
        with col_h:
            output_h = st.number_input(
                "Alto (px)", min_value=100, max_value=4096,
                value=DEFAULT_OUTPUT_SIZE[1], step=50
            )

    # --- Panel 2: Ajuste de posición de la foto ---
    # Permite alinear el rostro con la ventana/recuadro transparente del marco
    # sin necesidad de IA. En Fase 2 este panel puede reemplazarse por
    # detección automática de rostros.
    with st.expander("🎯 Ajuste de posición de la foto", expanded=True):
        st.caption(
            "Mueve la foto libremente en cualquier dirección. "
            "Si te sales del marco, verás el fondo transparente."
        )
        col_zoom, col_empty = st.columns([1, 1])
        with col_zoom:
            zoom = st.slider(
                "🔍 Zoom de la foto",
                min_value=0.5, max_value=3.0, value=1.0, step=0.05,
                help="Puedes alejar (<1.0) o acercar (>1.0) la foto.",
            )

        col_ox, col_oy = st.columns(2)
        # Permitimos mover la foto una distancia igual al tamaño del canvas
        max_pan = int(max(output_w, output_h))
        with col_ox:
            offset_x = st.slider(
                "↔️ Posición horizontal",
                min_value=-max_pan, max_value=max_pan, value=0, step=5,
                help="Mueve la foto hacia la izquierda o derecha libremente.",
            )
        with col_oy:
            offset_y = st.slider(
                "↕️ Posición vertical",
                min_value=-max_pan, max_value=max_pan, value=0, step=5,
                help="Mueve la foto hacia arriba o abajo libremente.",
            )

    return {
        "output_size": (int(output_w), int(output_h)),
        "zoom":        zoom,
        "offset_x":    offset_x,
        "offset_y":    offset_y,
    }


def render_process_section(frame_file, photo_file, settings: dict):
    """
    Renderiza la sección de procesamiento en TIEMPO REAL y descarga.

    v1.3 — Preview automático:
        Cuando ambas imágenes están cargadas, la composición se genera
        automáticamente en cada interacción (cada vez que el usuario mueve
        un slider o cambia un ajuste). No requiere botón "Previsualizar".

        Estrategia de cache por settings-key:
        - Se calcula una clave con los settings actuales.
        - Si la clave coincide con la última procesada, se reutiliza el resultado
          de session_state sin re-procesar (evita trabajo redundante).
        - Si la clave cambia (usuario movió un slider), se re-procesa.

        Esto garantiza que:
        1. El preview siempre refleja los ajustes actuales.
        2. El botón de descarga siempre corresponde al resultado visible.
        3. No se re-procesa si nada cambió.

    Args:
        frame_file: UploadedFile del marco (puede ser None).
        photo_file: UploadedFile de la foto (puede ser None).
        settings:   Diccionario con output_size, zoom, offset_x, offset_y.
    """
    output_size = settings["output_size"]
    zoom        = settings["zoom"]
    offset_x    = settings["offset_x"]
    offset_y    = settings["offset_y"]

    st.subheader("🚀 Paso 3: Preview en tiempo real y Exportar")

    files_ready = frame_file is not None and photo_file is not None

    # Botón de reset (única acción manual que queda)
    if st.button(
        "🔄 Limpiar resultado",
        disabled="result_image" not in st.session_state,
        help="Borra el resultado actual.",
    ):
        st.session_state.pop("result_image", None)
        st.session_state.pop("result_bytes", None)
        st.session_state.pop("result_settings", None)
        st.rerun()

    if not files_ready:
        st.info("📂 Carga el marco y la foto del conductor para ver el preview en tiempo real.")
        return

    # --- Cache por settings-key: solo re-procesa si algo cambió ---
    current_key = (output_size, zoom, offset_x, offset_y)
    cached_key  = st.session_state.get("result_settings")

    if cached_key != current_key:
        # Los ajustes cambiaron (o es la primera vez): procesar
        frame_img = load_image(frame_file)
        photo_img = load_image(photo_file)

        if frame_img is None or photo_img is None:
            st.error("❌ No se pudieron cargar las imágenes. Verifica los archivos.")
            return

        result_image = overlay_frame(
            photo_img, frame_img,
            output_size=output_size,
            zoom=zoom,
            offset_x=offset_x,
            offset_y=offset_y,
        )

        img_bytes = export_image_to_bytes(result_image, fmt=OUTPUT_FORMAT)
        st.session_state["result_image"]    = result_image
        st.session_state["result_bytes"]    = img_bytes
        st.session_state["result_settings"] = current_key

    # --- Preview y Descarga ---
    if "result_image" in st.session_state:
        st.divider()
        render_preview_and_download(
            st.session_state["result_image"],
            st.session_state["result_bytes"],
        )


def render_preview_and_download(result_image: Image.Image, img_bytes: bytes):
    """
    Renderiza el área de previsualización y el botón de descarga.

    FIX v1.2: Los bytes se reciben como parámetro (pre-calculados y guardados
    en session_state) en lugar de calcularse aquí. Esto garantiza que el
    st.download_button siempre recibe exactamente los mismos bytes sin importar
    cuántas veces Streamlit re-renderice la página al hacer clic en el botón.

    Args:
        result_image: PIL.Image.Image con la composición final.
        img_bytes:    bytes pre-serializados listos para descarga.
    """
    st.subheader("🔍 Previsualización del Resultado")

    col_preview, col_info = st.columns([2, 1])

    with col_preview:
        st.image(
            result_image,
            caption="Resultado final (Marco + Foto)",
            use_container_width=True,
        )

    with col_info:
        w, h = result_image.size
        st.metric("Ancho de salida", f"{w} px")
        st.metric("Alto de salida", f"{h} px")
        st.metric("Modo de color", result_image.mode)
        st.info(
            "La imagen exportada será un **PNG** de alta calidad "
            "con canal alfa preservado."
        )

        # Los bytes ya están pre-calculados: el botón es estable entre re-renders
        st.download_button(
            label="⬇️ Descargar Imagen",
            data=img_bytes,
            file_name=OUTPUT_FILENAME,
            mime="image/png",
            type="primary",
            use_container_width=True,
        )


def render_footer():
    """Renderiza el pie de página con información del proyecto."""
    st.divider()
    st.caption(
        f"**{APP_TITLE}** · MVP Fase 1 · "
        "Herramienta interna de procesamiento de imágenes · "
        "Desarrollado con [Streamlit](https://streamlit.io) y [Pillow](https://python-pillow.org)"
    )


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """
    Función principal que orquesta el flujo de la aplicación Streamlit.

    Orden de renderizado:
        1. Configuración de página.
        2. Encabezado.
        3. Sección de carga de archivos.
        4. Sección de ajustes.
        5. Sección de procesamiento / previsualización / descarga.
        6. Pie de página.
    """
    configure_page()
    render_header()
    frame_file, photo_file = render_upload_section()
    settings = render_settings_section()
    st.divider()
    render_process_section(frame_file, photo_file, settings)
    render_footer()


if __name__ == "__main__":
    main()


# =============================================================================
# ════════════════════════════════════════════════════════════════════════════
# PLACEHOLDERS FASE 2 - NO ELIMINAR
# Estos stubs documentan las funciones planeadas para la siguiente fase.
# Implementar aquí sin modificar las funciones del MVP arriba.
# ════════════════════════════════════════════════════════════════════════════
# =============================================================================

# --- FASE 2A: Procesamiento en Lote (Bulk Processing) ---
#
# def process_bulk(
#     photo_folder: str,
#     frame_path: str,
#     output_folder: str,
#     output_size: tuple = DEFAULT_OUTPUT_SIZE,
#     progress_callback=None
# ) -> list[str]:
#     """
#     Procesa una carpeta completa de fotos de conductores en lote.
#
#     Args:
#         photo_folder:      Ruta a la carpeta con las fotos individuales.
#         frame_path:        Ruta al marco PNG.
#         output_folder:     Ruta donde se guardarán las imágenes resultantes.
#         output_size:       Dimensiones del canvas de salida.
#         progress_callback: Función llamada con (current, total) para actualizar
#                            una barra de progreso de Streamlit.
#
#     Returns:
#         Lista de rutas absolutas de los archivos generados.
#     """
#     pass


# --- FASE 2B: Centrado Automático de Rostros (IA / Visión Artificial) ---
#
# def detect_face_center(image: Image.Image) -> tuple[int, int]:
#     """
#     Detecta el centro del rostro principal en una imagen usando OpenCV o MediaPipe.
#
#     Librerías candidatas:
#         - opencv-python: cv2.CascadeClassifier (Haar Cascades) - rápido, sin GPU.
#         - mediapipe: mp.solutions.face_detection - más preciso, basado en ML.
#
#     Args:
#         image: PIL.Image.Image de la foto del conductor.
#
#     Returns:
#         Tupla (x, y) con las coordenadas del centro del rostro detectado.
#         Retorna el centro geométrico de la imagen si no se detecta ningún rostro.
#
#     Integración con el MVP:
#         Llamar esta función dentro de `resize_to_fill()` justo antes del crop
#         para usar las coordenadas como punto focal del recorte.
#     """
#     pass


# --- FASE 2C: Manipulación de Fondos (Inversión / Cambio de Fondo Azul) ---
#
# def replace_blue_background(
#     image: Image.Image,
#     new_background: Image.Image | tuple,
#     tolerance: int = 30
# ) -> Image.Image:
#     """
#     Detecta y reemplaza el fondo azul institucional de una foto de conductor.
#
#     Estrategia:
#         1. Convertir la imagen a espacio de color HSV para detección robusta del azul.
#         2. Generar una máscara binaria del área de fondo.
#         3. Aplicar la máscara para componer el nuevo fondo.
#
#     Librerías:
#         - OpenCV (cv2.inRange) para segmentación de color en HSV.
#         - rembg como alternativa para remoción de fondo con IA.
#
#     Args:
#         image:          PIL.Image.Image con fondo azul.
#         new_background: Nuevo fondo. Puede ser una imagen PIL o una tupla RGB
#                         de color sólido (ej. (255, 255, 255) para blanco).
#         tolerance:      Rango de tolerancia HSV para la detección del azul.
#
#     Returns:
#         PIL.Image.Image con el fondo reemplazado.
#
#     Integración con el MVP:
#         Llamar esta función sobre `driver_photo` dentro de `overlay_frame()`
#         antes de la composición de capas.
#     """
#     pass
