# Código creado por Oxadison con amor para Suidelame ♥

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from pathlib import Path

from downloader import (
    download_video,
    check_and_update_all,
    _ensure_dependencies,
    cancel_download,
    cancel_event,
    get_video_info_json,
    check_main_app_update
)

BASE_DIR = Path(getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))))

COLOR_DEFAULT = "#000000"
COLOR_SUCCESS = "#008000"
COLOR_ERROR = "#CC0000"
COLOR_INFO = "#0000CC"
COLOR_WARN = "#D2691E"

class StdoutRedirector:
    def __init__(self, app):
        self.app = app

    def write(self, string):
        if not string: return
        
        clean_str = string
        if clean_str.strip():
            if "[download]" in clean_str and "%" in clean_str:
                self.app.write_progress(clean_str.strip())
            else:
                self.app.write_console(clean_str.rstrip())

    def flush(self):
        pass

class DescarGatoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DescarGato - Descargador de Videos - v1.0.5")
        try:
            self.root.iconbitmap(os.path.join(BASE_DIR, "icon.ico"))
        except Exception:
            pass

        w, h = 700, 660
        self.root.geometry(f"{w}x{h}")
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.minsize(700, 660)
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(False, False)

        self.is_downloading = False
        self.is_updating = False
        self.is_repairing = True

        self.download_dir = tk.StringVar(value="Selecciona una carpeta")
        self.build_interface()

        self.stdout_redirector = StdoutRedirector(self)
        sys.stdout = self.stdout_redirector
        sys.stderr = self.stdout_redirector
        
        self.set_buttons_state()
        threading.Thread(target=self._auto_repair_boot, daemon=True).start()

    def build_interface(self):
        tk.Label(self.root, text="DescarGato - Descargador de Videos",
                 font=("Helvetica", 18, "bold"), bg="#f0f0f0").pack(pady=10)
        tk.Label(self.root, text="♥ De Oxadison para Suidelame ♥",
                 font=("Helvetica", 12, "bold"), bg="#f0f0f0").pack(pady=10)

        tk.Label(self.root, text="URL del Video:", bg="#f0f0f0").pack()
        self.url_entry = tk.Entry(self.root, width=80)
        self.url_entry.pack(pady=5)

        url_menu = tk.Menu(self.root, tearoff=0)
        url_menu.add_command(label="Copiar", command=lambda: self.url_entry.event_generate("<<Copy>>"))
        url_menu.add_command(label="Pegar", command=lambda: self.url_entry.event_generate("<<Paste>>"))
        self.url_entry.bind("<Button-3>", lambda e: self._popup_menu(e, url_menu, self.url_entry))

        tk.Button(self.root, text="Seleccionar Carpeta de Descarga",
                  command=self.select_directory).pack()
        self.dir_label = tk.Label(self.root, textvariable=self.download_dir, fg="blue", bg="#f0f0f0")
        self.dir_label.pack(pady=5)

        tk.Label(self.root, text="Opciones de Descarga:", bg="#f0f0f0").pack()
        self.quality_var = tk.StringVar(value="Mejor Calidad")
        self.quality_box = ttk.Combobox(
            self.root, textvariable=self.quality_var, state="readonly",
            values=["Mejor Calidad", "Multi-Lenguaje", "Modo Compatibilidad", "1080p", "720p", "480p", "360p", "Solo Audio"]
        )
        self.quality_box.pack(pady=5)

        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.btn_download = tk.Button(btn_frame, text="Descargar", command=self.start_download)
        self.btn_clean = tk.Button(btn_frame, text="Limpiar / Cancelar", command=self.clear_interface)
        self.btn_update = tk.Button(btn_frame, text="Actualizar", command=self.start_update)
        self.btn_download.pack(side="left", padx=5)
        self.btn_clean.pack(side="left", padx=5)
        self.btn_update.pack(side="left", padx=5)
        btn_frame.pack(pady=10)

        tk.Label(self.root, text="Consola de Detalles", bg="#f0f0f0").pack()
        self.console = tk.Text(
            self.root, height=15, width=85, bg="black", fg="lime",
            insertbackground="white", font=("Consolas", 10), wrap="word",
            state="disabled", insertontime=0
        )
        self.console.bind("<Control-c>", lambda e: (self.copy_selected(), "break"))
        self.console.bind("<Control-C>", lambda e: (self.copy_selected(), "break"))
        self.console.bind("<Button-3>", self.show_copy_menu)
        self.console.pack(pady=10)

        self.status_label = tk.Label(
            self.root,
            text="⭐ Realiza alguna acción para comenzar ⭐",
            wraplength=550,
            bg="#f0f0f0",
            fg=COLOR_DEFAULT,
            font=("Helvetica", 14, "bold"),
            justify="center"
        )
        self.status_label.pack(pady=5)

        self.watermark = tk.Label(self.root, text="© 2025 Creado por Oxadison",
                                  font=("Helvetica", 9, "italic"), fg="gray", bg="#f0f0f0")
        self.watermark.pack(pady=5)

    def write_console(self, text):
        self.root.after(0, self._safe_write_console, text)

    def _safe_write_console(self, text):
        self.console.configure(state="normal")
        
        if "progress_pos" in self.console.mark_names():
            self.console.mark_unset("progress_pos")

        self.console.insert(tk.END, text + "\n")
        self.console.see(tk.END)
        self.console.configure(state="disabled")

    def write_progress(self, text):
        self.root.after(0, self._safe_write_progress, text)

    def _safe_write_progress(self, text):
        self.console.configure(state="normal")
        
        mark_name = "progress_pos"
        
        if mark_name in self.console.mark_names():
            linestart = self.console.index(mark_name)
            self.console.delete(linestart, f"{linestart} lineend")
            self.console.insert(linestart, text)
        else:
            self.console.insert(tk.END, text + "\n")
            self.console.mark_set(mark_name, "end-2l linestart")
            self.console.mark_gravity(mark_name, tk.LEFT)

        if "100%" in text:
            self.console.mark_unset(mark_name)

        self.console.see(tk.END)
        self.console.configure(state="disabled")

    def show_copy_menu(self, event):
        console_menu = tk.Menu(self.root, tearoff=0)
        console_menu.add_command(label="Copiar", command=lambda: self.copy_selected())
        try:
            self.console.get("sel.first", "sel.last")
            console_menu.entryconfig("Copiar", state="normal")
        except tk.TclError:
            console_menu.entryconfig("Copiar", state="disabled")
        console_menu.tk_popup(event.x_root, event.y_root)

    def _popup_menu(self, event, menu, widget):
        try:
            widget.selection_get()
            menu.entryconfig("Copiar", state="normal")
        except tk.TclError:
            menu.entryconfig("Copiar", state="disabled")
        menu.tk_popup(event.x_root, event.y_root)

    def copy_selected(self):
        try:
            text = self.console.get("sel.first", "sel.last")
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
        except tk.TclError:
            pass

    def is_valid_url(self, url):
        return url.startswith("http://") or url.startswith("https://")

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_dir.set(directory)

    def set_buttons_state(self):
        if self.is_downloading or self.is_updating or self.is_repairing:
            self.btn_download.config(state="disabled")
            self.btn_update.config(state="disabled")
        else:
            self.btn_download.config(state="normal")
            self.btn_update.config(state="normal")
            
        if self.is_updating or self.is_repairing:
            self.btn_clean.config(state="disabled")
        else:
            self.btn_clean.config(state="normal")

    def ask_audio_preference(self):
        win = tk.Toplevel(self.root)
        win.title("Elección de Formato")
        win.geometry("520x200")
        win.resizable(False, False)
        win.configure(bg="#f0f0f0")
        
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (520 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (200 // 2)
        win.geometry(f"+{x}+{y}")

        try:
            win.iconbitmap(os.path.join(BASE_DIR, "icon.ico"))
        except Exception:
            pass

        win.bell()

        main_frame = tk.Frame(win, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        icon_lbl = tk.Label(main_frame, text="🎧", font=("Segoe UI Emoji", 40), bg="#f0f0f0", fg="#000000")
        icon_lbl.pack(side="left", anchor="n", padx=(0, 15))

        msg_text = (
            "¿Cómo deseas guardar el archivo de audio?\n\n"
            "- Original: Mejor calidad de sonido, descarga rápida.\n\n"
            "- MP3: Mayor compatibilidad, conversión lenta.\n"
        )
        msg_lbl = tk.Label(main_frame, text=msg_text, bg="#f0f0f0", justify="left", font=("Segoe UI", 10))
        msg_lbl.pack(side="left", fill="both", expand=True)

        self._audio_choice = None

        def set_choice(choice):
            self._audio_choice = choice
            win.destroy()

        btn_frame = tk.Frame(win, bg="#f0f0f0")
        btn_frame.pack(side="bottom", fill="x", pady=10, padx=20)

        btn_inner = tk.Frame(btn_frame, bg="#f0f0f0")
        btn_inner.pack(side="right")

        tk.Button(btn_inner, text="Original", width=12, command=lambda: set_choice("original")).pack(side="left", padx=5)
        tk.Button(btn_inner, text="MP3", width=12, command=lambda: set_choice("mp3")).pack(side="left", padx=5)
        tk.Button(btn_inner, text="Cancelar", width=12, command=lambda: set_choice("cancel")).pack(side="left", padx=5)

        win.transient(self.root)
        win.grab_set()
        self.root.wait_window(win)
        return self._audio_choice

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url or not self.is_valid_url(url):
            messagebox.showwarning("Error", "Por favor, ingresa una URL válida.")
            return
        if self.download_dir.get() == "Selecciona una carpeta":
            messagebox.showwarning("Error", "Por favor, selecciona una carpeta de descarga.")
            return

        if self.is_updating:
            messagebox.showinfo("Ocupado", "No puedes descargar mientras se actualiza.")
            return

        mp3_mode = False 

        if self.quality_var.get() == "Modo Compatibilidad":
            mensaje_aviso = (
                "Este es un modo especial que garantiza compatibilidad universal.\n\n"
                "Si el formato compatible no está disponible, DescarGato iniciará una "
                "conversión forzada del video.\n\n"
                "Esto puede tardar un rato y consumirá más recursos de tu PC.\n\n"
                "Se recomienda NO usar esta opción en videos muy largos y de alta calidad si es que tienes prisa o una computadora de bajos recursos.\n\n"
                "¿Deseas continuar?"
            )
            response = messagebox.askokcancel(
                "Advertencia",
                mensaje_aviso,
                icon='warning'
            )
            if not response:
                return

        if self.quality_var.get() == "Solo Audio":
            choice = self.ask_audio_preference()
            if choice == "cancel" or choice is None:
                return
            if choice == "mp3":
                mp3_mode = True
            else:
                mp3_mode = False 

        self.is_downloading = True
        cancel_event.clear()
        self.status_label.config(text="Descargando… ⏳", fg=COLOR_INFO)
        self.set_buttons_state()

        threading.Thread(target=self._download_thread, args=(url, mp3_mode), daemon=True).start()

    def _download_thread(self, url, force_mp3_conversion):
        try:
            _ensure_dependencies(log=self._log, prog=lambda p: None)

            selected_quality = self.quality_var.get()

            h264_req = "[vcodec^=avc]+bestaudio[ext=m4a]"
            
            primary_fmt = None
            fallback_fmt = None
            merge_target = None 
            use_fallback_logic = False
            extract_audio_mode = False

            if selected_quality in ["1080p", "720p", "480p", "360p"]:
                target_height = int(selected_quality.replace("p", ""))
                self.write_console(f"Analizando calidades para {selected_quality}...")
                
                info = get_video_info_json(url)
                
                final_height = None
                available_heights = set()
                
                if info and 'formats' in info:
                    for f in info['formats']:
                        h = f.get('height')
                        if h:
                            available_heights.add(h)
                
                sorted_heights = sorted(list(available_heights), reverse=True)
                
                for h in sorted_heights:
                    if h <= target_height:
                        final_height = h
                        break
                
                if final_height:
                    if final_height < target_height:
                        self.write_console(f"⚠️ {target_height}p no disponible. Bajando a {final_height}p (la más cercana disponible).")
                    else:
                        self.write_console(f"Calidad {final_height}p confirmada.")

                    primary_fmt = f"bestvideo[height<={final_height}]+bestaudio/best[height<={final_height}]"
                    merge_target = None
                    use_fallback_logic = False
                else:
                    self.write_console(f"⚠️ Calidad no disponible: {selected_quality} (ni inferiores).")
                    
                    if sorted_heights:
                        msg_avail = ", ".join([f"{h}p" for h in sorted_heights])
                        self.write_console(f"Calidades disponibles: {msg_avail}")
                    else:
                        self.write_console("No se pudo obtener la lista de calidades.")
                        
                    self.root.after(0, lambda: self.status_label.config(text="Calidad no disponible ❌", fg=COLOR_WARN))
                    return

            elif selected_quality == "Mejor Calidad":
                primary_fmt = "bestvideo+bestaudio/best"
                merge_target = None
                use_fallback_logic = False
            
            elif selected_quality == "Multi-Lenguaje":
                self.write_console("Modo Multilenguaje activado: Buscando audio Español y Original + Subtítulos...")
                primary_fmt = "bestvideo+bestaudio[language^=es]+bestaudio/bestvideo+bestaudio"
                merge_target = "mkv"
                use_fallback_logic = False
            
            elif selected_quality == "Modo Compatibilidad":
                primary_fmt = f"bestvideo{h264_req}/best[ext=mp4][vcodec^=avc]"
                fallback_fmt = "bestvideo+bestaudio/best"
                merge_target = "mp4"
                use_fallback_logic = True
            
            elif selected_quality == "Solo Audio":
                primary_fmt = "bestaudio/best"
                merge_target = None
                use_fallback_logic = False
                extract_audio_mode = True
            
            else:
                primary_fmt = "bestvideo+bestaudio/best"
                merge_target = None
                use_fallback_logic = False

            def progress_hook(percent):
                self.root.after(0, lambda: self.status_label.config(text="Descargando… ⏳", fg=COLOR_INFO))

            if not use_fallback_logic:
                is_multi = (selected_quality == "Multi-Lenguaje")
                langs_req = "es.*,en.*,orig,und" if is_multi else None
                
                download_video(
                    url,
                    directory=self.download_dir.get(),
                    progress_callback=progress_hook,
                    download_format=primary_fmt,
                    output_merge_format=merge_target,
                    transcode_to_h264=False,
                    convert_to_mp3=force_mp3_conversion,
                    extract_audio=extract_audio_mode,
                    embed_subs=is_multi,
                    sub_langs=langs_req,
                    multi_audio=is_multi
                )
            else:
                try:
                    self.write_console("Modo Compatibilidad: Buscando formato nativo H.264...")
                    download_video(
                        url,
                        directory=self.download_dir.get(),
                        progress_callback=progress_hook,
                        download_format=primary_fmt,
                        output_merge_format=merge_target,
                        transcode_to_h264=False
                    )
                except Exception as e:
                    error_str = str(e)
                    if "Requested format is not available" in error_str or "exit code" in error_str or "Error código 1" in error_str:
                        msg = "⚠️ Formato nativo no encontrado. Activando Conversión Forzada (Esto puede tardar)..."
                        self.write_console(msg)
                        self.root.after(0, lambda: self.status_label.config(text="Convirtiendo… ⏳", fg=COLOR_WARN))
                        
                        download_video(
                            url,
                            directory=self.download_dir.get(),
                            progress_callback=progress_hook,
                            download_format=fallback_fmt,
                            output_merge_format=merge_target,
                            transcode_to_h264=True
                        )
                    else:
                        raise e 

            if not cancel_event.is_set():
                self.root.after(0, lambda: self.status_label.config(text="Completado ✅", fg=COLOR_SUCCESS))
        
        except KeyboardInterrupt:
            self.root.after(0, lambda: self.status_label.config(text="Cancelado ⏹️", fg=COLOR_WARN))
            self.write_console("Proceso cancelado por el usuario.")
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text="Error ❌", fg=COLOR_ERROR))
            err = str(e)
            print(f"[Error] {err}")
            if "Requested format is not available" in err:
                self.write_console("Error: No se encontró ningún formato descargable para este video.")
        finally:
            self.is_downloading = False
            self.root.after(0, self.set_buttons_state)

    def start_update(self):
        if self.is_downloading:
            messagebox.showinfo("Ocupado", "No puedes actualizar mientras hay una descarga.")
            return

        self.is_updating = True
        cancel_event.clear()
        self.status_label.config(text="Actualizando… 🔄", fg=COLOR_INFO)
        self.set_buttons_state()

        threading.Thread(target=self._run_update, daemon=True).start()

    def _run_update(self):
        try:
            def log(msg):
                self.write_console(msg)
                if len(msg) < 80:
                    self.root.after(0, lambda: self.status_label.config(text=f"{msg} 🔄", fg=COLOR_INFO))

            def prog(pct):
                pass 

            self.write_console("Actualizando componentes…")
            self.root.after(0, lambda: self.status_label.config(text="Buscando actualizaciones… 🔄", fg=COLOR_INFO))

            has_core_update = check_main_app_update(log, prog)
            
            if has_core_update:
                os._exit(0)
                return

            updated = check_and_update_all(log, prog)

            if cancel_event.is_set():
                self.root.after(0, lambda: self.status_label.config(text="Cancelado ⏹️", fg=COLOR_WARN))
                self.write_console("Proceso cancelado por el usuario.")
            else:
                if updated:
                    self.root.after(0, lambda: self.status_label.config(text="Actualización completada ✅", fg=COLOR_SUCCESS))
                    self.write_console("Actualización completada satisfactoriamente.")
                else:
                    self.root.after(0, lambda: self.status_label.config(text="Sin novedades 👍", fg=COLOR_DEFAULT))
                    self.write_console("No se han encontrado nuevas actualizaciones.")
        except KeyboardInterrupt:
            self.root.after(0, lambda: self.status_label.config(text="Cancelado ⏹️", fg=COLOR_WARN))
            self.write_console("Proceso cancelado por el usuario.")
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text="Error durante la actualización ❌", fg=COLOR_ERROR))
            print(f"[Update][Error] {e}")
        finally:
            self.is_updating = False
            self.root.after(0, self.set_buttons_state)

    def clear_interface(self):
        if self.is_downloading or self.is_updating:
            cancel_download()

        if self.is_downloading or self.is_updating:
            self.write_console("Proceso cancelado por el usuario.")

        self.url_entry.delete(0, tk.END)
        self.status_label.config(text="⭐ Realiza alguna acción para comenzar ⭐", fg=COLOR_DEFAULT)
        self.console.configure(state="normal")
        self.console.delete("1.0", tk.END)
        self.console.configure(state="disabled")

        self.is_downloading = False
        self.is_updating = False
        self.set_buttons_state()

    def _log(self, msg):
        print(msg)

    def _auto_repair_boot(self):
        try:
            self.write_console("Verificando entorno…")
            self.root.after(0, lambda: self.status_label.config(text="Verificando entorno… 🛠️", fg=COLOR_INFO))

            def log(msg):
                self.write_console(msg)
                if len(msg) < 80:
                    self.root.after(0, lambda: self.status_label.config(text=f"{msg} 🛠️", fg=COLOR_INFO))

            def prog(pct):
                pass

            _ensure_dependencies(log=log, prog=prog)

            self.write_console("Entorno verificado correctamente.")
            self.root.after(0, lambda: self.status_label.config(text="⭐ Realiza alguna acción para comenzar ⭐", fg=COLOR_DEFAULT))
        except Exception as e:
            self.write_console(f"[AutoRepair] {e}")
            self.root.after(0, lambda: self.status_label.config(text="Error durante la reparación ❌", fg=COLOR_ERROR))
        finally:
            self.is_repairing = False
            self.root.after(0, self.set_buttons_state)

if __name__ == "__main__":
    root = tk.Tk()
    app = DescarGatoApp(root)
    root.mainloop()
