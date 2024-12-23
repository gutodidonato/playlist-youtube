import os
import time
from tkinter import Tk, Label, Entry, Button, filedialog, StringVar, Text, END, ttk, Listbox
import yt_dlp

# Lista para armazenar URLs das playlists
playlist_urls = []

# Função para selecionar pasta de saída
def select_folder():
    folder = filedialog.askdirectory()
    output_folder_var.set(folder)

# Função para adicionar URL à lista de playlists
def add_playlist():
    playlist_url = url_var.get()
    if not playlist_url:
        log_text.insert(END, "Por favor, insira uma URL válida.\n")
        return

    playlist_urls.append(playlist_url)
    playlist_listbox.insert(END, playlist_url)
    url_var.set("")
    log_text.insert(END, f"Playlist adicionada: {playlist_url}\n")

# Função para remover URL da lista de playlists
def remove_playlist():
    selected = playlist_listbox.curselection()
    if not selected:
        log_text.insert(END, "Por favor, selecione uma playlist para remover.\n")
        return

    index = selected[0]
    removed_url = playlist_urls.pop(index)
    playlist_listbox.delete(index)
    log_text.insert(END, f"Playlist removida: {removed_url}\n")

# Função para processar todas as playlists na lista
def download_playlists():
    output_folder = output_folder_var.get()

    if not playlist_urls:
        log_text.insert(END, "A lista de playlists está vazia.\n")
        return

    if not output_folder:
        log_text.insert(END, "Por favor, selecione uma pasta de saída.\n")
        return

    for playlist_url in playlist_urls:
        log_text.insert(END, f"Processando playlist: {playlist_url}\n")
        try:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(output_folder, "%(title)s.%(ext)s"),
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "progress_hooks": [progress_hook],
                "ignoreerrors": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    ydl.download([playlist_url])
                except yt_dlp.utils.DownloadError as e:
                    if "This video has been removed for violating YouTube's Terms of Service" in str(e):
                        log_text.insert(END, "Vídeo removido por violar os Termos de Serviço do YouTube. Pulando...\n")
                    elif "Connection to" in str(e) and "timed out" in str(e):
                        log_text.insert(END, "Erro de conexão. Tentando novamente...\n")
                        time.sleep(5)  # Espera 5 segundos antes de tentar novamente
                        ydl.download([playlist_url])
                    else:
                        log_text.insert(END, f"Erro ao processar a playlist: {e}\n")
                        continue
        except Exception as e:
            log_text.insert(END, f"Erro ao processar a playlist: {e}\n")
            continue

    log_text.insert(END, "Todos os downloads foram concluídos.\n")

# Função para exibir progresso do download
def progress_hook(d):
    if d["status"] == "downloading":
        log_text.insert(END, f"Baixando: {d['_percent_str']} concluído\n")
        log_text.see(END)
    elif d["status"] == "finished":
        log_text.insert(END, "Download concluído. Convertendo...\n")
        log_text.see(END)

# Interface gráfica usando Tkinter
app = Tk()
app.title("Downloader de Playlists do YouTube com yt-dlp")
app.geometry("700x500")

# URL da playlist
Label(app, text="URL da Playlist:").pack(pady=5)
url_var = StringVar()
Entry(app, textvariable=url_var, width=70).pack(pady=5)

# Botões para gerenciar playlists
Button(app, text="Adicionar Playlist", command=add_playlist).pack(pady=5)
Button(app, text="Remover Playlist", command=remove_playlist).pack(pady=5)

# Lista de playlists
Label(app, text="Playlists na Fila:").pack(pady=5)
playlist_listbox = Listbox(app, width=80, height=10)
playlist_listbox.pack(pady=5)

# Pasta de saída
Label(app, text="Pasta de Saída:").pack(pady=5)
output_folder_var = StringVar()
Entry(app, textvariable=output_folder_var, width=50).pack(side="left", padx=10)
Button(app, text="Selecionar Pasta", command=select_folder).pack(side="left", padx=5)

# Botão para iniciar downloads
Button(app, text="Baixar Todas as Playlists", command=download_playlists).pack(pady=20)

# Log de mensagens
Label(app, text="Log:").pack(pady=5)
log_text = Text(app, height=10, width=80)
log_text.pack(pady=5)

# Inicia a interface
app.mainloop()
