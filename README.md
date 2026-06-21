# Información general

## DescarGato:

Este es mi primer proyecto, creado especialmente con amor para mi novia Suidelame ♥. Es un software sencillo pero eficiente para Windows que permite descargar videos de múltiples plataformas (YouTube, Instagram, Facebook, TikTok, etc.).

Funciona como una interfaz gráfica para yt-dlp, integrando automáticamente complementos como ffmpeg, solver, deno, curl-cffi y aria2c.

Sólo debes instalar Python para poder abrir el archivo `main.py`; el programa se encarga automáticamente de conseguir los complementos que necesita para funcionar.

------------------------------------------------------------------------

### 📦 Versión Portable

*Nota: La primera vez que abras el programa se descargarán los complementos necesarios.*

### ⚠️ Importante ⚠️

En caso de que uses el ejecutable `.exe` y al abrir te aparezca la ventana de **"Windows protegió su PC"**, haz clic en **"Más información"** y luego en **"Ejecutar de todas formas"**.

<img width="401" height="375" alt="01" src="https://github.com/user-attachments/assets/5ff53100-2615-41a9-855b-2eae707102d6" />   <img width="401" height="375" alt="03" src="https://github.com/user-attachments/assets/be88fc7c-cfab-4e9c-8e66-46c546111cae" />

------------------------------------------------------------------------

## 🖥️ Instrucciones para su uso 🖥️

La interfaz de DescarGato es muy intuitiva y está compuesta por los siguientes elementos:

<img width="874" height="862" alt="DesgarGato" src="https://github.com/user-attachments/assets/483a75ee-dd61-42b5-9c5d-5a4921152cd9" />

| Elemento de la Interfaz | Función Principal |
| :--- | :--- |
| **Barra de URL** | Pegar el enlace del video que deseas descargar (YouTube, TikTok, Instagram y más). |
| **Seleccionar Carpeta** | Elegir la ubicación exacta y personalizada en tu PC donde se guardarán los archivos (la ruta se muestra debajo). |
| **Opciones de Descarga** | Seleccionar la calidad visual (por defecto "Mejor Calidad"), formato de solo audio, Multi-Lenguaje o el Modo Compatibilidad. |
| **Botón Descargar** | Iniciar el proceso de descarga según la calidad y parámetros elegidos. |
| **Limpiar / Cancelar** | Restablecer toda la interfaz, borrar el enlace ingresado, limpiar la consola o detener forzosamente un proceso activo. |
| **Actualizar** | Verificar y descargar la última versión del software (si la hay) o renovar los complementos internos. |
| **Consola de Detalles** | Visualizar el progreso, estado y posibles advertencias en tiempo real. |
| **Estado General** | Ubicado al pie de la ventana, muestra el estado actual (esperando, descargando, completado o error). |

### 📌 Notas sobre las Opciones de Descarga

* **Opción "Multi-Lenguaje":** Esta función descarga el video en un contenedor `.mkv` que incluye el audio original y la mejor pista de audio en Español (si está disponible), además de los subtítulos incrustados. Esto permite cambiar de idioma y activar/desactivar subtítulos directamente desde el reproductor de video.
* **Calidades específicas:** Si eliges una opción como **"1080p"** y esta no está disponible en el video, el programa buscará automáticamente **la siguiente calidad inferior más cercana** (ej. 720p) para garantizar la descarga. Si no existe ninguna opción válida, te mostrará una lista de las calidades que sí están disponibles.
* **Modo Compatibilidad:** En caso de que el archivo descargado muestre incompatibilidad, elige esta opción. Buscará un formato compatible, y en caso de que no lo haya, iniciará un **proceso de conversión forzada**.
