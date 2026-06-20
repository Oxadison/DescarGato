📘 Información general 📘

DescarGato:

Este es mi primer proyecto, un software que he creado especialmente para mi novia Suidelame ♥ 
sencillo pero eficiente para descargar videos de múltiples 
plataformas como Youtube, Instagram, Facebook, Tiktok, etc.

Sólo deben instalarse python para poder abrir el archivo main.py, el solo se encarga de conseguir los complementos que necesita para funcionar,
si lo quieren como un ejecutable .exe totalmente independiente en el sistema ejecuten este comando: (requiere tener pyinstaller instalado)

pyinstaller --noconfirm --onedir --windowed --clean --name "DescarGato" --icon "icon.ico" --add-data "icon.ico;." main.py

------------------------------------------------------------------------

Les dejo por si desean, la versión ya convertida en un ejecutable .exe para que
puedan abrirlo directamente sin tener que instalar nada:

https://drive.google.com/file/d/1X0-u4GUS3p24lIp7QD-jok7QG-4lX5xE/view?usp=sharing

Nota: La primera vez que abran el programa se descargarán los complementos que aproximadamente son 444Mb

⚠️ Importante ⚠️

En caso de que uses el ejecutable .exe y al abrir te aparece la ventana de 
"Windows protegió su PC", da click en "Más información" y "Ejecutar de todas formas"

<img width="401" height="375" alt="01" src="https://github.com/user-attachments/assets/5ff53100-2615-41a9-855b-2eae707102d6" />   <img width="401" height="375" alt="03" src="https://github.com/user-attachments/assets/be88fc7c-cfab-4e9c-8e66-46c546111cae" />

------------------------------------------------------------------------

🖥️ Instrucciones para su uso 🖥️

La interfaz de DescarGato es muy intuitiva y está compuesta por los
siguientes elementos:

<img width="874" height="862" alt="DesgarGato" src="https://github.com/user-attachments/assets/483a75ee-dd61-42b5-9c5d-5a4921152cd9" />

-   Barra de URL: aquí debes pegar el enlace del video que quieras
    descargar (YouTube, TikTok, Instagram y más).

-   Botón "Seleccionar Carpeta de Descarga": te permite elegir una
    ubicación personalizada donde se guardarán tus videos.

-   Etiqueta de Carpeta Seleccionada: justo debajo se muestra la ruta de
    la carpeta activa para que sepas dónde se guardarán los archivos.

-   Opciones de Descarga: permite elegir entre varias opciones
    (Mejor Calidad, Multi-Lenguaje, Modo Compatibilidad, 1080p, 720p, 480p, 360p o Solo Audio).

    Por defecto siempre está seleccionada la opción "Mejor Calidad".

    Opción "Multi-Lenguaje": Esta función descarga el video en un 
    contenedor .mkv que incluye el audio original y la mejor 
    pista de audio en Español (si está disponible), además de los subtítulos incrustados. 
    Esto permite cambiar de idioma y activar/desactivar subtítulos desde el 
    reproductor de video.
    
    Nota sobre calidades específicas: Si eliges una opción como "1080p" y 
    esta no está disponible en el video, el programa buscará automáticamente 
    la siguiente calidad inferior más cercana (ej. 720p) para garantizar 
    la descarga. Si no existe ninguna opción válida, te mostrará una lista 
    de las calidades que sí están disponibles.

    En caso de que el archivo descargado muestre incompatibilidad, 
    elegir la opción "Modo Compatibilidad" esta opción buscará un formato
    compatible, y en caso de que no lo haya, iniciará un proceso de conversión
    forzada, lo que puede tardar más tiempo y consumir recursos de la computadora,
    se recomienda no usarla en videos largos con calidades altas, y en
    computadoras de bajos recursos.

-   Botón "Descargar": inicia la descarga del video según la calidad
    seleccionada.

-   Botón "Limpiar / Cancelar": restablece la interfaz, borra el enlace
    ingresado, limpia la consola y cancela cualquier proceso activo.

-   Botón "Actualizar": verifica y descarga automáticamente las últimas
    versiones de sus complementos que son importantes para que el software funcione,
	para mantener el programa al día.

-   Consola de Detalles: muestra en tiempo real lo que hace el programa
    (estado de la descarga, progreso, errores si ocurren, etc.).

-   Estado General: al pie de la ventana justo abajo de la consola,
    se muestra el estado actual (esperando, descargando, completado o error).

------------------------------------------------------------------------

© 2025 Oxadison. Todos los derechos reservados.

Este software es propiedad intelectual de Oxadison. 
Queda prohibida su distribución, modificación o uso comercial sin 
autorización previa y por escrito del autor.
