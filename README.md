# Información general

## DescarGato:

Este es mi primer proyecto, creado especialmente con amor para mi novia **Suidelame ♥**

**DescarGato** es un software sencillo pero eficiente para **Windows** que permite descargar videos de múltiples plataformas como YouTube, Instagram, Facebook, TikTok, etc.
Funciona principalmente como una interfaz gráfica para **yt-dlp**, integrando varios complementos adicionales.

Sólo debes instalar Python para poder abrir el archivo `main.py`; el programa se encarga automáticamente de conseguir los complementos que necesita para funcionar.

------------------------------------------------------------------------

### 📦 Versión Portable 📦

*Nota: La primera vez que abras el programa se descargarán los complementos necesarios.*

### ⚠️ Importante ⚠️

En caso de que uses el ejecutable `.exe` y al abrir te aparezca la ventana de **"Windows protegió su PC"**, haz clic en **"Más información"** y luego en **"Ejecutar de todas formas"**.

<img width="1068" height="500" alt="1_2" src="https://github.com/user-attachments/assets/87f7d672-f3b3-42c1-969d-8fc3becaf1ea" />

------------------------------------------------------------------------

## 🖥️ Instrucciones para su uso 🖥️

La interfaz de DescarGato es muy intuitiva y está compuesta por los siguientes elementos:

<img width="874" height="862" alt="DescarGato_c2" src="https://github.com/user-attachments/assets/84b3fe13-445a-4a1f-b3e7-f1dc747ac0d7" />

| **Elemento de la Interfaz** | **Función Principal** |
| :--- | :--- |
| **Barra de URL** | Pegar el enlace del video que deseas descargar (YouTube, TikTok, Instagram y más). |
| **Seleccionar Carpeta** | Elegir la ubicación exacta y personalizada en tu PC donde se guardarán los archivos (la ruta se muestra debajo). |
| **Opciones de Descarga** | Seleccionar la calidad visual (por defecto "Mejor Calidad"), formato de solo audio, Multi-Lenguaje o el Modo Compatibilidad. |
| **Botón Descargar** | Iniciar el proceso de descarga según la calidad y parámetros elegidos. |
| **Limpiar / Cancelar** | Restablecer toda la interfaz, borrar el enlace ingresado, limpiar la consola o detener forzosamente un proceso activo. |
| **Actualizador** | Verificar y descargar la última versión del software (si la hay) o renovar los complementos internos. |
| **Consola de Detalles** | Visualizar el progreso, estado y posibles advertencias en tiempo real. |
| **Estado General** | Ubicado al pie de la ventana, muestra el estado actual (esperando, descargando, completado o error). |

### 📌 Notas sobre las Opciones de Descarga 📌

* **Opción "Multi-Lenguaje":** Esta función descarga el video en un contenedor `.mkv` que incluye el audio original y la mejor pista de audio en Español (si está disponible), además de los subtítulos incrustados. Esto permite cambiar de idioma y activar/desactivar subtítulos directamente desde el reproductor de video.
* **Calidades específicas:** Si eliges una opción como **"1080p"** y esta no está disponible en el video, el programa buscará automáticamente **la siguiente calidad inferior más cercana** (ej. 720p) para garantizar la descarga. Si no existe ninguna opción válida, te mostrará una lista de las calidades que sí están disponibles.
* **Modo Compatibilidad:** En caso de que el archivo descargado muestre incompatibilidad, elige esta opción. Buscará un formato compatible, y en caso de que no lo haya, iniciará un **proceso de conversión forzada**.

### 🛑 ¡Advertencia Crítica sobre las actualizaciones del software! 🛑

Al momento de actualizar el software, se abrirá **la consola de actualización**.

<img width="1099" height="637" alt="Console" src="https://github.com/user-attachments/assets/8deb439e-45ed-4ff0-bc59-96b793aebcbb" />

**Bajo ningún concepto debes cerrarla**. Hacerlo dejará el programa completamente inutilizado. Aunque he bloqueado el botón de cerrar (X) por seguridad, si el proceso llegara a interrumpirse por cualquier otro motivo (como un cierre forzado del sistema), será necesario **descargar el software nuevamente** desde este repositorio.

------------------------------------------------------------------------

## ⚖️ Políticas de Uso y Descargo de Responsabilidad

**DescarGato** ha sido desarrollado con fines estrictamente educativos y para facilitar el acceso a contenido de libre distribución o para uso personal y privado. 

Al descargar y utilizar este software, el usuario acepta las siguientes políticas:
1. **Responsabilidad del Usuario:** El desarrollador (Oxadison) no fomenta, apoya ni se hace responsable de la descarga, distribución o piratería de material protegido por derechos de autor, así como tampoco de la obtención, almacenamiento o distribución de cualquier tipo de material ilegal, ilícito o prohibido por las leyes vigentes. Toda la responsabilidad legal, penal y civil recae única y exclusivamente en el usuario final.
2. **Respeto a las Plataformas:** El usuario debe asegurarse de tener los derechos, permisos o consentimientos legales necesarios antes de descargar medios desde cualquier plataforma, respetando siempre sus respectivos Términos de Servicio (ToS).
3. **Uso del Software:** Este programa se proporciona "tal cual", sin garantías de ningún tipo. El desarrollador no se hace responsable de daños, pérdida de datos o bloqueos de IP derivados del uso de esta herramienta.

------------------------------------------------------------------------

## 🤝 Créditos y Dependencias de Terceros 🤝

Este proyecto funciona como una interfaz gráfica y orquestador. El trabajo pesado de descarga y procesamiento es realizado gracias a los siguientes proyectos de código abierto, los cuales son descargados dinámicamente por la aplicación:

* **[yt-dlp](https://github.com/yt-dlp/yt-dlp):** El motor principal utilizado para la extracción y descarga de medios.
* **[FFmpeg](https://ffmpeg.org/) (vía [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)):** Fundamental para la conversión de formatos y la fusión de pistas de audio y video en calidades altas.
* **[Deno](https://deno.com/):** Entorno de ejecución de JavaScript utilizado en segundo plano para procesar scripts de resolución de desafíos de red (`solver.js`).
* **[curl_cffi](https://github.com/lexiforest/curl_cffi):** Librería de Python utilizada para suplantar huellas TLS y asegurar conexiones estables.
* **Python Embebido:** El núcleo portátil que permite que DescarGato funcione en cualquier sistema Windows sin instalaciones previas.
* **Tkinter:** El framework nativo de Python utilizado para construir esta interfaz gráfica.

------------------------------------------------------------------------

**© 2025 Oxadison. Todos los derechos reservados.**
