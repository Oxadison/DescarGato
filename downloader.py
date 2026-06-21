# Código creado por Oxadison con amor para Suidelame ♥

import os
import sys
import re
import io
import json
import zipfile
import shutil
import threading
import subprocess
import urllib.request
import tempfile
import ssl
from pathlib import Path

APP_VERSION = "1.0.3"
GITHUB_REPO = "Oxadison/DescarGato"

APP_DIR = Path(getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))))
BIN_DIR = APP_DIR / "bin"
PY_EMBED_DIR = BIN_DIR / "python"
SITE_PACKAGES = BIN_DIR / "site-packages"
YTDLP_DIR = SITE_PACKAGES / "yt_dlp"

FFMPEG_EXE = BIN_DIR / "ffmpeg.exe"
FFPROBE_EXE = BIN_DIR / "ffprobe.exe"
ARIA2C_EXE = BIN_DIR / "aria2c.exe"
PYTHON_EXE = PY_EMBED_DIR / "python.exe"
DENO_EXE = BIN_DIR / "deno.exe"
SOLVER_JS = BIN_DIR / "yt.solver.lib.min.js"
CURL_CFFI_MARKER = SITE_PACKAGES / "curl_cffi"

CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
USER_AGENT = "DescarGato-Updater"
TIMEOUT = 30

_active_processes_lock = threading.Lock()
_active_processes = [] 
cancel_event = threading.Event()

def _req(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    return urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx)

def _http_json(url):
    with _req(url) as r:
        return json.loads(r.read().decode("utf-8", errors="ignore"))

def _http_text(url):
    with _req(url) as r:
        return r.read().decode("utf-8", errors="ignore").strip()

def _http_bytes(url):
    with _req(url) as r:
        return r.read()

def _ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def _copytree(src: Path, dst: Path):
    _ensure_dir(dst)
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        target = dst / (rel if rel != "." else "")
        _ensure_dir(target)
        for f in files:
            shutil.copy2(os.path.join(root, f), target / f)

def _add_active_process(p: subprocess.Popen):
    with _active_processes_lock:
        _active_processes.append(p)

def _pop_active_process(p: subprocess.Popen):
    with _active_processes_lock:
        if p in _active_processes:
            _active_processes.remove(p)

def _kill_tree(p: subprocess.Popen):
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(p.pid)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW
            )
        else:
            p.terminate()
    except Exception:
        pass

def _run_ver(exe, args):
    try:
        out = subprocess.run([str(exe)] + list(args),
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, encoding="utf-8", errors="ignore", timeout=15, creationflags=CREATE_NO_WINDOW)
        return (out.stdout or "").strip()
    except Exception as e:
        return f"ERROR: {e}"

def _ff_ver_line(txt):
    first = (txt or "").splitlines()[0] if txt else ""
    m = re.search(r"ffmpeg version ([^\s]+)", first)
    return m.group(1) if m else first

def _aria_ver_line(txt):
    m = re.search(r"aria2 version ([^\s]+)", txt or "")
    return m.group(1) if m else ""

def _cache_path():
    p = APP_DIR / "gatoupdate"
    _ensure_dir(p)
    return p

def _get_pypi_download_url(package, match_fn):
    try:
        data = _http_json(f"https://pypi.org/pypi/{package}/json")
        version = data["info"]["version"]
        selected_url = None
        for file_obj in data["urls"]:
            if match_fn(file_obj["filename"]):
                selected_url = file_obj["url"]
                break
        return version, selected_url
    except Exception:
        return None, None

def _latest_python_embed_info():
    index = "https://www.python.org/ftp/python/"
    try:
        txt = _http_text(index)
        vers = re.findall(r'href=["\']?(3\.\d+\.\d+)/?["\']?', txt)
        if not vers:
            raise Exception("Regex no encontró versiones")
        vers = list(set(vers))
        vers.sort(key=lambda v: tuple(map(int, v.split("."))), reverse=True)
        for ver in vers:
            filename = f"python-{ver}-embed-amd64.zip"
            url = f"{index}{ver}/{filename}"
            try:
                req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=10) as r:
                    if r.status == 200:
                        return ver, url, filename
            except Exception:
                continue
    except Exception as e:
        pass
    return "3.11.5", f"{index}3.11.5/python-3.11.5-embed-amd64.zip", "python-3.11.5-embed-amd64.zip"

def _install_embedded_python(cache, log):
    ver, url, filename = _latest_python_embed_info()
    log(f"Descargando Python {ver}…")
    data = _http_bytes(url)
    ext = cache / "py_embed"
    shutil.rmtree(ext, ignore_errors=True)
    _ensure_dir(ext)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        z.extractall(ext)
    shutil.rmtree(PY_EMBED_DIR, ignore_errors=True)
    _ensure_dir(BIN_DIR)
    shutil.copytree(ext, PY_EMBED_DIR)
    log("Python instalado.")
    pth = None
    for item in PY_EMBED_DIR.glob("python*.pth"): continue
    for item in PY_EMBED_DIR.glob("python*._pth"):
        pth = item
        break
    if pth is None:
        major_minor = ""
        for dll in PY_EMBED_DIR.glob("python3*.dll"):
            m = re.search(r"python(3\d)", dll.name)
            if m:
                major_minor = m.group(1)
                break
        pth = PY_EMBED_DIR / f"python{major_minor}._pth"
    content = ""
    if pth.exists():
        content = pth.read_text(encoding="utf-8", errors="ignore")
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    if str(SITE_PACKAGES) not in lines:
        rel = os.path.relpath(SITE_PACKAGES, PY_EMBED_DIR)
        lines.append(rel.replace("\\", "/"))
    if "import site" not in lines:
        lines.append("import site")
    pth.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log("Python configurado.")

def _install_ytdlp_source(cache, log, prog=None):
    log("Buscando actualizaciones de yt-dlp…")
    rel = _http_json("https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest")
    tag = rel.get("tag_name", "").strip()
    asset_zip = None
    for a in rel.get("assets", []):
        n = (a.get("name") or "").lower()
        if n.endswith(".zip") and "source" in n:
            asset_zip = a.get("browser_download_url")
            break
    if not asset_zip: asset_zip = rel.get("zipball_url")
    current_ver = ""
    if YTDLP_DIR.exists() and (YTDLP_DIR / "__version__.py").exists():
        try:
            text = (YTDLP_DIR / "__version__.py").read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", text)
            if m: current_ver = m.group(1)
        except Exception: current_ver = ""
    need = (not YTDLP_DIR.exists()) or (tag and (current_ver != tag))
    if not need:
        log("yt-dlp: ya está actualizado.")
        return False
    if prog: prog(10)
    log(f"Descargando yt-dlp {tag}…")
    data = _http_bytes(asset_zip)
    ext = cache / "ytdlp_src"
    shutil.rmtree(ext, ignore_errors=True)
    _ensure_dir(ext)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        z.extractall(ext)
    src_pkg = None
    for root, dirs, files in os.walk(ext):
        if "yt_dlp" in dirs:
            src_pkg = Path(root) / "yt_dlp"
            break
    if not src_pkg: raise RuntimeError("No se encontró el paquete yt_dlp en el ZIP.")
    shutil.rmtree(YTDLP_DIR, ignore_errors=True)
    _ensure_dir(SITE_PACKAGES)
    shutil.copytree(src_pkg, YTDLP_DIR)
    log(f"yt-dlp actualizado a {tag}.")
    if prog: prog(20)
    return True

def _install_aria2(cache, log, prog=None):
    log("Buscando actualizaciones de aria2c…")
    rel = _http_json("https://api.github.com/repos/aria2/aria2/releases/latest")
    tag = rel.get("tag_name", "") or ""
    cur = _aria_ver_line(_run_ver(ARIA2C_EXE, ["-v"])) if ARIA2C_EXE.exists() else ""
    need = (not cur) or (tag and tag.replace("release-", "").strip("v") not in cur)
    if not need:
        log("aria2c: ya está actualizado.")
        return False
    asset = None
    for a in rel.get("assets", []):
        n = (a.get("name") or "").lower()
        if "win-64bit" in n and n.endswith(".zip"):
            asset = a.get("browser_download_url")
            break
    if not asset:
        log("No se encontró asset win-64bit para aria2c; se omite.")
        return False
    if prog: prog(35)
    log(f"Descargando aria2c {tag}…")
    data = _http_bytes(asset)
    ext = cache / "aria2c_ext"
    shutil.rmtree(ext, ignore_errors=True)
    _ensure_dir(ext)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        z.extractall(ext)
    found = None
    for root, _, files in os.walk(ext):
        if "aria2c.exe" in files:
            found = Path(root)
            break
    if not found: raise RuntimeError("aria2c.exe no encontrado en el zip.")
    _copytree(found, BIN_DIR)
    log(f"aria2c actualizado a {tag}.")
    if prog: prog(50)
    return True

def _install_impersonate_deps(cache, log, prog=None):
    log("Verificando curl_cffi...")
    
    if CURL_CFFI_MARKER.exists():
        log("curl_cffi: ya instalado.")
        return False

    if prog: prog(60)
    
    cp_tag = "cp311"
    try:
        for f in PY_EMBED_DIR.glob("python3*.dll"):
            m = re.search(r"python(3\d+)", f.name)
            if m:
                cp_tag = f"cp{m.group(1)}"
                break
    except: pass
    
    _ensure_dir(SITE_PACKAGES)

    packages = [
        {
            "name": "pycparser",
            "filter": lambda n: n.endswith(".whl")
        },
        {
            "name": "cffi",
            "filter": lambda n: "win_amd64" in n and cp_tag in n
        },
        {
            "name": "curl_cffi",
            "filter": lambda n: "win_amd64" in n and ("abi3" in n or cp_tag in n)
        }
    ]

    for pkg in packages:
        name = pkg["name"]
        try:
            ver, url = _get_pypi_download_url(name, pkg["filter"])
            if not url:
                log(f"Error: No se encontró versión compatible de {name}")
                continue
                
            log(f"Descargando {name} {ver}…")
            data = _http_bytes(url)
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                z.extractall(SITE_PACKAGES)
            
            log(f"{name} instalado.")
            
        except Exception as e:
            log(f"Error instalando {name}: {e}")
            return False

    if prog: prog(65)
    return True

def _install_deno_and_scripts(cache, log, prog=None):
    log("Verificando Deno y Scripts...")
    
    if not DENO_EXE.exists():
        if prog: prog(70)
        
        rel = _http_json("https://api.github.com/repos/denoland/deno/releases/latest")
        tag = rel.get("tag_name", "latest")
        
        log(f"Descargando Deno {tag}…")
        try:
            url = "https://github.com/denoland/deno/releases/latest/download/deno-x86_64-pc-windows-msvc.zip"
            data = _http_bytes(url)
            ext = cache / "deno_temp"
            shutil.rmtree(ext, ignore_errors=True)
            _ensure_dir(ext)
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                z.extractall(ext)
            deno_bin = None
            for root, _, files in os.walk(ext):
                if "deno.exe" in files:
                    deno_bin = Path(root) / "deno.exe"
                    break
            if not deno_bin: raise RuntimeError("deno.exe no encontrado en el zip.")
            shutil.copy2(deno_bin, DENO_EXE)
            log("Deno instalado.")
        except Exception as e:
            log(f"Error Deno: {e}")
            return False
    else:
        log("Deno: ya está instalado.")

    log("Buscando última versión de solver.js...")
    
    api_url = "https://api.github.com/repos/yt-dlp/ejs/releases/latest"
    
    try:
        release_info = _http_json(api_url)
        tag_name = release_info.get("tag_name", "unknown")
        
        asset_url = None
        for asset in release_info.get("assets", []):
            if asset.get("name") == "yt.solver.lib.min.js":
                asset_url = asset.get("browser_download_url")
                break
        
        if asset_url:
            log(f"Descargando solver.js {tag_name}...")
            js_data = _http_bytes(asset_url)
            with open(SOLVER_JS, "wb") as f:
                f.write(js_data)
            log("solver.js actualizado.")
        else:
            raise Exception("Asset no encontrado")

    except Exception:
        if not SOLVER_JS.exists():
            try:
                fallback_url = "https://raw.githubusercontent.com/yt-dlp/ejs/master/yt.solver.lib.min.js"
                js_data = _http_bytes(fallback_url)
                with open(SOLVER_JS, "wb") as f:
                    f.write(js_data)
                log("solver.js instalado (Fallback).")
            except Exception:
                pass
    
    if prog: prog(80)
    return True

def _install_ffmpeg(cache, log, prog=None):
    log("Buscando actualizaciones de ffmpeg…")
    cur = _ff_ver_line(_run_ver(FFMPEG_EXE, ["-version"])) if FFMPEG_EXE.exists() else ""
    latest_short = _http_text("https://www.gyan.dev/ffmpeg/builds/release-version").split()[0]
    if cur and latest_short and cur.startswith(latest_short):
        log("ffmpeg: ya está actualizado.")
        return False
    if prog: prog(90)
    log(f"Descargando ffmpeg release essentials ({latest_short})…")
    data = _http_bytes("https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip")
    ext = cache / "ffmpeg_ext"
    shutil.rmtree(ext, ignore_errors=True)
    _ensure_dir(ext)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        z.extractall(ext)
    cand = None
    for root, _, files in os.walk(ext):
        if "ffmpeg.exe" in files:
            cand = Path(root)
            break
    if not cand: raise RuntimeError("ffmpeg.exe no encontrado en el zip.")
    _copytree(cand, BIN_DIR)
    new_ver = _ff_ver_line(_run_ver(FFMPEG_EXE, ["-version"]))
    log(f"ffmpeg actualizado a {new_ver}.")
    if prog: prog(95)
    return True

def check_and_update_all(log=print, prog=lambda p: None):
    cache = _cache_path()
    log("Iniciando reinstalación completa del entorno...")
    prog(0)
    try:
        if BIN_DIR.exists():
            log("Limpiando instalación anterior...")
            for item in [PY_EMBED_DIR, SITE_PACKAGES, FFMPEG_EXE, FFPROBE_EXE, ARIA2C_EXE, DENO_EXE, SOLVER_JS]:
                try:
                    if Path(item).is_file(): Path(item).unlink(missing_ok=True)
                    elif Path(item).is_dir(): shutil.rmtree(item, ignore_errors=True)
                except Exception as e: log(f"[CleanupOld] No se pudo eliminar {item}: {e}")
            shutil.rmtree(SITE_PACKAGES, ignore_errors=True)
        _ensure_dir(BIN_DIR)
        log("Componentes antiguos eliminados correctamente.")
        prog(5)
        _install_embedded_python(cache, log)
        prog(20)
        _install_ytdlp_source(cache, log, prog)
        prog(35)
        _install_aria2(cache, log, prog)
        prog(50)
        _install_impersonate_deps(cache, log, prog)
        _install_deno_and_scripts(cache, log, prog)
        _install_ffmpeg(cache, log, prog)
        prog(95)
        try:
            shutil.rmtree(cache, ignore_errors=True)
            log("Archivos temporales eliminados correctamente.")
        except Exception as e: log(f"[Cleanup] No se pudo eliminar cache temporal: {e}")
        prog(100)
        log("Reinstalación completa finalizada exitosamente.")
        return True
    except Exception as e:
        log(f"[Updater][Error durante la reinstalación] {e}")
        try: shutil.rmtree(cache, ignore_errors=True)
        except Exception: pass
        prog(100)
        return False

def _ensure_dependencies(log=print, prog=lambda p: None):
    need = False
    missing = []
    if not PYTHON_EXE.exists(): need = True; missing.append("Python")
    if not YTDLP_DIR.exists(): need = True; missing.append("yt-dlp")
    if not FFMPEG_EXE.exists(): need = True; missing.append("ffmpeg")
    if not ARIA2C_EXE.exists(): need = True; missing.append("aria2c")
    if not DENO_EXE.exists(): need = True; missing.append("deno")
    if not SOLVER_JS.exists(): need = True; missing.append("solver.js")
    if not CURL_CFFI_MARKER.exists(): need = True; missing.append("curl_cffi")

    if need:
        log("Autorrepación: faltan componentes → " + ", ".join(missing))
        check_and_update_all(log, prog)
    return True

def _build_env_for_embed():
    env = os.environ.copy()
    env["PYTHONHOME"] = str(PY_EMBED_DIR)
    extra_path = str(SITE_PACKAGES)
    existed = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (extra_path + os.pathsep + existed) if existed else extra_path
    current_path = env.get("PATH", "")
    env["PATH"] = str(BIN_DIR) + os.pathsep + current_path
    env["XDG_CACHE_HOME"] = str(BIN_DIR)
    return env

def cancel_download():
    cancel_event.set()
    with _active_processes_lock:
        for p in list(_active_processes):
            try: _kill_tree(p)
            except Exception: pass

def get_video_info_json(url):
    _ensure_dependencies()
    os.environ["PATH"] = str(BIN_DIR) + os.pathsep + os.environ.get("PATH", "")
    env_vars = _build_env_for_embed()
    deno_arg = f"deno:{DENO_EXE}"
    
    cmd = [
        str(PYTHON_EXE), "-m", "yt_dlp",
        "--no-check-certificate",
        "--js-runtimes", deno_arg,
        "-J", url
    ]
    
    if SOLVER_JS.exists():
        cmd.extend(["--extractor-args", f"youtube:player_client=all;solver_url=file:///{str(SOLVER_JS).replace(os.sep, '/')}"])
        cmd.extend(["--cache-dir", str(BIN_DIR)])
    else:
        cmd.extend(["--extractor-args", "youtube:player_client=all"])
        cmd.extend(["--cache-dir", str(BIN_DIR)])
    
    try:
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore", env=env_vars, creationflags=CREATE_NO_WINDOW)
        if out.returncode == 0:
            return json.loads(out.stdout)
        return None
    except:
        return None

def download_video(url, directory, progress_callback=None, download_format="bestvideo+bestaudio/best", output_merge_format=None, transcode_to_h264=False, convert_to_mp3=False, extract_audio=False, embed_subs=False, sub_langs=None, multi_audio=False):
    cancel_event.clear()
    _ensure_dir(Path(directory))
    _ensure_dependencies()
    
    if getattr(sys, 'frozen', False):
        BASE_EXEC_DIR = Path(sys.executable).parent
    else:
        BASE_EXEC_DIR = Path(__file__).parent
        
    temp_dir = BASE_EXEC_DIR / "gatodownload"
    _ensure_dir(temp_dir)
    
    if transcode_to_h264:
        out_tmpl_string = "DescarGato - %(title).51s - %(extractor_key)s.mp4"
    else:
        out_tmpl_string = "DescarGato - %(title).51s - %(extractor_key)s.%(ext)s"

    os.environ["PATH"] = str(BIN_DIR) + os.pathsep + os.environ.get("PATH", "")
    env_vars = _build_env_for_embed()

    deno_arg = f"deno:{DENO_EXE}"

    aria2_args = [
        "--max-connection-per-server=16",
        "--min-split-size=1M",
        "--split=16",
        "--console-log-level=warn",
        "--summary-interval=0"
    ]
    aria2_args_str = " ".join(aria2_args)

    cmd = [
        str(PYTHON_EXE),
        "-m", "yt_dlp",
        "--no-check-certificate",
        "--js-runtimes", deno_arg,
        "-f", download_format,
        "-o", os.path.join(temp_dir, out_tmpl_string),
        "--no-playlist",
        "--ffmpeg-location", str(FFMPEG_EXE),
        "--downloader", "aria2c",
        "--downloader-args", f"aria2c:{aria2_args_str}",
        "--restrict-filenames"
    ]

    cmd.extend(["--remote-components", "ejs:github"])
    cmd.extend(["--cache-dir", str(BIN_DIR)])
    
    if SOLVER_JS.exists():
        cmd.extend(["--extractor-args", f"youtube:player_client=all;solver_url=file:///{str(SOLVER_JS).replace(os.sep, '/')}"])
    else:
        cmd.extend(["--extractor-args", "youtube:player_client=all"])
    
    if output_merge_format:
        cmd.extend(["--merge-output-format", output_merge_format])
        
        if output_merge_format == "mp4" and transcode_to_h264:
            cmd.extend(["--recode-video", "mp4"])
            cmd.extend(["--postprocessor-args", "merger:-c:v libx264 -c:a aac"])
            cmd.extend(["--postprocessor-args", "video_convertor:-c:v libx264 -c:a aac"])

    if multi_audio:
        cmd.append("--audio-multistreams")
    
    if embed_subs:
        cmd.extend(["--embed-subs", "--write-subs", "--embed-metadata", "--convert-subs", "srt"])
        if sub_langs:
            cmd.extend(["--sub-langs", sub_langs])
        else:
            cmd.extend(["--sub-langs", "all"])

    if extract_audio:
        cmd.append("-x")
        if convert_to_mp3:
            cmd.extend(["--audio-format", "mp3", "--audio-quality", "320"])

    cmd.append(url)

    ARIA_REGEX = re.compile(r"\[#\w+\s+(?P<cur>[\w\.]+)/(?P<tot>[\w\.]+)\((?P<pct>\d+)%\).*?DL:(?P<spd>[\w\.]+)(?:.*?ETA:(?P<eta>[\w:]+))?")
    DL_PERCENT = re.compile(r"(\d+(?:\.\d+)?)%")
    ARIA_NOISE_START = re.compile(r"^\s*\[#?[0-9a-fA-F]{4,}.*?\]")

    print("[Info] Iniciando descarga...")
    
    with subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8", 
        errors="ignore", 
        bufsize=1,
        env=env_vars,
        creationflags=CREATE_NO_WINDOW
    ) as p:
        _add_active_process(p)
        try:
            for raw in p.stdout:
                if cancel_event.is_set():
                    _kill_tree(p)
                    raise KeyboardInterrupt("Cancelado por usuario.")
                
                line = raw.rstrip()
                if not line: continue 

                if "impersonation" in line or "impersonate target" in line:
                    continue
                if "Requested format is not available" in line:
                    continue
                if "Not converting media file" in line and "already is in target format" in line:
                    continue

                if ARIA_NOISE_START.match(line):
                    m = ARIA_REGEX.search(line)
                    if m:
                        pct = m.group("pct")
                        tot = m.group("tot")
                        spd = m.group("spd")
                        eta = m.group("eta") if m.group("eta") else "?"
                        
                        if progress_callback:
                            try: progress_callback(int(float(pct)))
                            except: pass
                        
                        print(f"[download] {pct}% de {tot} a {spd}/s ETA {eta}", flush=True)
                    else:
                        m2 = DL_PERCENT.search(line)
                        if m2 and progress_callback:
                            try: progress_callback(int(float(m2.group(1))))
                            except: pass
                    continue
                
                print(line, flush=True)

            p.wait()
            if p.returncode != 0:
                raise RuntimeError(f"Error código {p.returncode}.")
            
            for filename in os.listdir(temp_dir):
                src_path = temp_dir / filename
                if "part" in filename or "ytdl" in filename: continue
                
                name_part, ext_part = os.path.splitext(filename)
                
                if ext_part.lower() in ['.vtt', '.srt', '.ttml', '.json', '.ass']: continue
                
                prefix = "DescarGato - "
                clean_name = name_part
                if clean_name.startswith(prefix):
                    clean_name = clean_name[len(prefix):]
                
                parts = clean_name.rsplit(" - ", 1)
                
                if len(parts) == 2:
                    title_part = parts[0]
                    platform_part = parts[1]
                else:
                    title_part = clean_name
                    platform_part = "Youtube"
                
                if len(title_part) > 50:
                    title_part = title_part[:50] + "..."
                
                final_name = f"{prefix}{title_part} - {platform_part}{ext_part}"
                
                final_dst = Path(directory) / final_name
                counter = 1
                
                final_stem = os.path.splitext(final_name)[0]
                while final_dst.exists():
                    counter += 1
                    final_dst = Path(directory) / f"{final_stem} ({counter}){ext_part}"
                
                try: shutil.move(str(src_path), str(final_dst))
                except: pass

        finally:
            _pop_active_process(p)
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
                
def _launch_gui_updater(zip_path, log):
    log("Preparando entorno seguro de actualización...")
    
    temp_dir = Path(tempfile.gettempdir()) / "GatoUpdaterEnv"
    shutil.rmtree(temp_dir, ignore_errors=True)
    _ensure_dir(temp_dir)

    temp_py_dir = temp_dir / "python"
    shutil.copytree(PY_EMBED_DIR, temp_py_dir)

    if getattr(sys, 'frozen', False):
        real_root_dir = Path(sys.executable).parent
    else:
        real_root_dir = APP_DIR

    script_path = temp_dir / "gatoupdater.py"
    script_code = """
import sys, os, time, zipfile, shutil, ctypes
from ctypes import wintypes

def center_console():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        win_width = rect.right - rect.left
        win_height = rect.bottom - rect.top
        
        x = (screen_width // 2) - (win_width // 2)
        y = (screen_height // 2) - (win_height // 2)
        
        user32.SetWindowPos(hwnd, 0, x, y, 0, 0, 0x0001 | 0x0004)

def run_update():
    center_console()

    app_dir = sys.argv[1]
    zip_path = sys.argv[2]
    exe_name = sys.argv[3]

    os.system("title DescarGato Updater")
    os.system("color 0B")
    
    print("==================================================")
    print("           INSTALANDO NUEVA VERSION               ")
    print("==================================================")
    print("\\n[!] Esperando a que el programa principal se cierre...")
    
    time.sleep(4) 

    try:
        internal_dir = os.path.join(app_dir, "_internal")
        if os.path.exists(internal_dir):
            print("[!] Eliminando carpeta '_internal' antigua...")
            shutil.rmtree(internal_dir, ignore_errors=True)
            
        bin_dir = os.path.join(app_dir, "bin")
        if os.path.exists(bin_dir):
            print("[!] Eliminando carpeta 'bin' antigua...")
            shutil.rmtree(bin_dir, ignore_errors=True)

        old_exe = os.path.join(app_dir, exe_name)
        if os.path.exists(old_exe):
            print(f"[!] Eliminando {exe_name} antiguo...")
            try:
                os.remove(old_exe)
            except Exception as e:
                print(f"[-] Nota: No se pudo eliminar el .exe previo. ({e})")

        print("[!] Extrayendo y reemplazando con la nueva version...")
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(app_dir)
            
        print("[!] Refrescando cache de iconos de Windows...")
        try:
            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0, None, None)
        except:
            pass
        
        print("\\n[+] ¡Actualizacion completada con exito!")
        print("[+] Iniciando DescarGato...")
        time.sleep(2.5)
        
        target_exe = os.path.join(app_dir, exe_name)
        os.startfile(target_exe)
        
    except Exception as e:
        print(f"\\n[X] ERROR CRITICO DURANTE LA ACTUALIZACION:")
        print(f"    {e}")
        print("\\nEsta ventana se cerrara en 15 segundos...")
        time.sleep(15)

if __name__ == '__main__':
    run_update()
"""
    script_path.write_text(script_code, encoding="utf-8")
    
    log("Iniciando actualizador. El programa se cerrará ahora.")
    python_exe = temp_py_dir / "python.exe"
    
    flags = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
    
    subprocess.Popen(
        [str(python_exe), str(script_path), str(real_root_dir), str(zip_path), "DescarGato.exe"],
        creationflags=flags
    )
def check_main_app_update(log=print, prog=lambda p: None):
    log("Buscando actualizaciones del núcleo de DescarGato...")
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    try:
        rel = _http_json(api_url)
        tag = rel.get("tag_name", "").strip("v")
        
        if tag and tag != APP_VERSION:
            log(f"¡Nueva versión del programa encontrada! (v{tag})")
            prog(10)
            
            asset_url = None
            for a in rel.get("assets", []):
                if a.get("name", "").endswith(".zip"):
                    asset_url = a.get("browser_download_url")
                    break
                    
            if asset_url:
                log("Descargando la nueva versión del DescarGato...")
                zip_data = _http_bytes(asset_url)
                
                zip_path = Path(tempfile.gettempdir()) / f"DescarGato_Update_v{tag}.zip"
                with open(zip_path, "wb") as f:
                    f.write(zip_data)
                
                prog(90)
                _launch_gui_updater(zip_path, log)
                return True
        else:
            log("El núcleo de DescarGato ya está en su última versión.")
    except Exception as e:
        log(f"No se pudo verificar actualizaciones del núcleo: {e}")
    return False

__all__ = [
    "check_and_update_all",
    "_ensure_dependencies",
    "download_video",
    "cancel_download",
    "cancel_event",
    "get_video_info_json",
    "check_main_app_update"
]
