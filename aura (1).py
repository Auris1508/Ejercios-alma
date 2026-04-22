import customtkinter as ctk
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os

# =============================================
#   CONFIGURACIÓN Y DATOS
# =============================================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

FILE_CSV = "02_2024Investigadores.csv"
FILE_USERS = "usuarios.txt"

try:
    df = pd.read_csv(FILE_CSV)
except Exception as e:
    print(f"Error al cargar CSV: {e}")
    # Crear un df vacío para que no truene si no encuentra el archivo inmediatamente
    df = pd.DataFrame(columns=["no", "nombre", "grado", "genero", "categoria", "unidad", "nivel_snii"])

# =============================================
#   LÓGICA DE USUARIOS
# =============================================

def validar_login():
    user = entry_user.get().strip()
    pwd = entry_pass.get().strip()

    # Credenciales por defecto si el archivo no existe
    credenciales = {"admin": "1234"} 
    
    if os.path.exists(FILE_USERS):
        with open(FILE_USERS, "r") as f:
            for linea in f:
                if "," in linea:
                    u, p = linea.strip().split(",")
                    credenciales[u] = p

    if user in credenciales and credenciales[user] == pwd:
        login_frame.pack_forget()
        abrir_interfaz_principal()
    else:
        lbl_msg.configure(text="Usuario o contraseña incorrectos", text_color="red")

# =============================================
#   MOSTRAR TABLAS (FRAME DE RESULTADOS)
# =============================================
def mostrar_en_tabla(data, titulo="Resultados"):
    for w in frame_contenido.winfo_children():
        w.destroy()

    ctk.CTkLabel(frame_contenido, text=titulo, font=("Arial", 18, "bold")).pack(pady=10)

    if data.empty:
        ctk.CTkLabel(frame_contenido, text="No se encontraron registros.").pack(pady=20)
        return

    # Contenedor con Scroll
    scroll_frame = ctk.CTkScrollableFrame(frame_contenido, width=800, height=500)
    scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Encabezados
    for j, col in enumerate(data.columns):
        lbl = ctk.CTkLabel(scroll_frame, text=col.upper(), font=("Arial", 11, "bold"), 
                           fg_color="#3b8ed0", text_color="white", corner_radius=5, width=140)
        lbl.grid(row=0, column=j, padx=2, pady=5)

    # Datos
    for idx, (i, row) in enumerate(data.head(100).iterrows()): # Limitado a 100 para fluidez
        for j, value in enumerate(row):
            bg = "#f2f2f2" if idx % 2 == 0 else "#ffffff"
            lbl = ctk.CTkLabel(scroll_frame, text=str(value), width=140, fg_color=bg, anchor="w", padx=5)
            lbl.grid(row=idx+1, column=j, padx=1, pady=1)

# =============================================
#   CONSULTAS COMPLEJAS
# =============================================
def query_search():
    val = entry_search.get().lower()
    res = df[df['nombre'].str.lower().contains(val, na=False) | df['unidad'].str.lower().contains(val, na=False)]
    mostrar_en_tabla(res, f"Búsqueda: {val}")

def abrir_dashboard():
    for w in frame_contenido.winfo_children():
        w.destroy()
    
    if df.empty:
        ctk.CTkLabel(frame_contenido, text="No hay datos para mostrar").pack(pady=20)
        return
    
    scroll = ctk.CTkScrollableFrame(frame_contenido)
    scroll.pack(fill="both", expand=True)

    fig, axs = plt.subplots(2, 1, figsize=(6, 10))
    plt.subplots_adjust(hspace=0.4)

    # Grafica 1: Investigadores por Grado
    df['grado'].value_counts().plot(kind='bar', ax=axs[0], color='#3b8ed0')
    axs[0].set_title("Distribución por Grado Académico")
    axs[0].tick_params(axis='x', rotation=45)

    # Grafica 2: SNII por Género
    pd.crosstab(df['nivel_snii'], df['genero'], dropna=False).plot(kind='bar', stacked=True, ax=axs[1])
    axs[1].set_title("Nivel SNII por Género")

    canvas = FigureCanvasTkAgg(fig, master=scroll)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, pady=20)

# =============================================
#   INTERFAZ PRINCIPAL
# =============================================
def abrir_interfaz_principal():
    global frame_contenido, entry_search
    
    # Sidebar
    sidebar = ctk.CTkFrame(root, width=240, corner_radius=0)
    sidebar.pack(side="left", fill="y")

    ctk.CTkLabel(sidebar, text="SISTEMA SNII", font=("Arial", 20, "bold")).pack(pady=20)

    # Buscador
    entry_search = ctk.CTkEntry(sidebar, placeholder_text="Buscar nombre o unidad...")
    entry_search.pack(pady=10, padx=10, fill="x")
    ctk.CTkButton(sidebar, text="🔍 Buscar", command=query_search).pack(pady=5, padx=10, fill="x")

    # Lista de 10 Consultas
    queries = [
        ("🏠 Ver Todo (Primeros 50)", lambda: mostrar_en_tabla(df.head(50))),
        ("📊 Dashboard Gráfico", abrir_dashboard),
        ("🎓 Investigadores por Grado", lambda: mostrar_en_tabla(df['grado'].value_counts().reset_index())),
        ("🏢 Top 10 Unidades", lambda: mostrar_en_tabla(df['unidad'].value_counts().head(10).reset_index())),
        ("⭐ Nivel SNII (2 y 3)", lambda: mostrar_en_tabla(df[df['nivel_snii'] >= 2])),
        ("👩 Género por Unidad", lambda: mostrar_en_tabla(pd.crosstab(df['unidad'], df['genero']).reset_index())),
        ("📜 Listar Doctores", lambda: mostrar_en_tabla(df[df['grado'] == 'Doctorado'])),
        ("🔬 Categorías Tecnólogo", lambda: mostrar_en_tabla(df[df['categoria'].str.contains("Tecnólogo", na=False)])),
        ("📉 Sin Nivel SNII (0)", lambda: mostrar_en_tabla(df[df['nivel_snii'] == 0])),
        ("📋 Resumen por Categoría", lambda: mostrar_en_tabla(df.groupby('categoria')['nivel_snii'].mean().reset_index()))
    ]

    for texto, comando in queries:
        ctk.CTkButton(sidebar, text=texto, command=comando, fg_color="transparent", 
                       text_color="black", hover_color="#d1d1d1", anchor="w").pack(fill="x", padx=10, pady=2)

    # Frame de Contenido
    frame_contenido = ctk.CTkFrame(root, fg_color="white")
    frame_contenido.pack(side="right", fill="both", expand=True, padx=10, pady=10)
    
    mostrar_en_tabla(df.head(10), "Bienvenido - Registros Recientes")

# =============================================
#   LOGIN UI
# =============================================

root = ctk.CTk()
root.title("Investigadores 2024 - Sistema de Consultas")
root.geometry("1100x700")

login_frame = ctk.CTkFrame(root, width=350, height=400)
login_frame.place(relx=0.5, rely=0.5, anchor="center")

ctk.CTkLabel(login_frame, text="INICIO DE SESIÓN", font=("Arial", 18, "bold")).pack(pady=20)

entry_user = ctk.CTkEntry(login_frame, placeholder_text="Usuario", width=250)
entry_user.pack(pady=10)

entry_pass = ctk.CTkEntry(login_frame, placeholder_text="Contraseña", show="*", width=250)
entry_pass.pack(pady=10)

ctk.CTkButton(login_frame, text="Entrar", command=validar_login, width=250).pack(pady=20)

lbl_msg = ctk.CTkLabel(login_frame, text="")
lbl_msg.pack()

root.mainloop()