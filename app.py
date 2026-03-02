import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin
import os
import urllib.parse

st.set_page_config(layout="centered")

# ======================
# ESTADO
# ======================

if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"

if "datos" not in st.session_state:
    st.session_state.datos = None

if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None

if "ig_paths" not in st.session_state:
    st.session_state.ig_paths = []

# ======================
# NAVEGACIÓN
# ======================

pagina = st.sidebar.radio(
    "Menú",
    ["Inicio", "Crear", "Vista previa"],
    index=["Inicio", "Crear", "Vista previa"].index(st.session_state.pagina)
)

# ======================
# INICIO
# ======================

if pagina == "Inicio":

    st.title("🧷 FanzineLab por Vindria")

    st.markdown("""
## Herramienta de creación

FanzineLab es un espacio para experimentar con la escritura, la imagen y la narrativa visual.

Permite crear un fanzine que puede:

- Imprimirse en formato físico  
- Compartirse digitalmente  
- Publicarse como carrusel en redes sociales  

---

## 🧷 Cómo hacer tu fanzine

1. **Exploración**
   - Define una idea o tema  
   - Piensa qué quieres compartir  

2. **Construcción**
   - Escribe textos breves, o no  
   - Agrega imágenes o dibujos (tómale foto)  
   - Experimenta con la composición  

3. **Organización**
   - Ajusta la posición del contenido  
   - Observa cómo quedan las páginas  

4. **Revisión**
   - Visualiza tu fanzine antes de exportar  
   - Realiza ajustes si es necesario  

5. **Publicación**
   - Descarga en PDF para impresión  
   - Exporta imágenes para redes  

---

## 📸 Salida digital (Instagram)

- Formato: 1080 x 1350  
- Pensado para carrusel  
- Una página por imagen  

---

## 🖨️ Impreso 

- Imprime en hoja tamaño carta  
- Dobla y corta para formar el cuadernillo  

---

## 🌱 Uso responsable

Esta herramienta está diseñada para la creación, expresión y aprendizaje.

No debe utilizarse para:

- generar odio  
- promover violencia  
- atacar a otras personas  

La creatividad implica responsabilidad.

---

## 📜 Licencia

Creative Commons BY-NC-SA  

- Puedes compartir y adaptar  
- Debes dar crédito  
- No usar con fines comerciales  
- Compartir con la misma licencia  
""")

    if st.button("✂️ Crear mi Fanzine"):
        st.session_state.pagina = "Crear"
        st.rerun()

# ======================
# CREAR
# ======================

if pagina == "Crear":

    st.title("🧷 Crear Fanzine")

    nombre = st.text_input("Autor")
    titulo = st.text_input("Título")

    textos = []
    imagenes = []

    for i in range(8):
        st.markdown(f"### Página {i+1}")

        texto = st.text_area(f"Texto {i+1}", key=f"t{i}")
        imagen = st.file_uploader(f"Imagen {i+1}", type=["png","jpg","jpeg"], key=f"i{i}")

        textos.append(texto)
        imagenes.append(imagen)

    st.subheader("🎯 Posición")

    alineaciones = []

    for i in range(8):
        col1, col2 = st.columns(2)

        with col1:
            h = st.selectbox("Horizontal", ["izquierda","centro","derecha"], key=f"h{i}")

        with col2:
            v = st.selectbox("Vertical", ["arriba","centro","abajo"], key=f"v{i}")

        alineaciones.append((h,v))

    if st.button("👁️ Ver mi fanzine"):

        st.session_state.datos = {
            "nombre": nombre,
            "titulo": titulo,
            "textos": textos,
            "imagenes": imagenes,
            "alineaciones": alineaciones
        }

        st.session_state.pagina = "Vista previa"
        st.rerun()

# ======================
# FUNCIONES
# ======================

def calcular_posicion(h, v, W, H, tw, th):
    x = 60 if h == "izquierda" else (W - tw)/2 if h == "centro" else W - tw - 60
    y = 60 if v == "arriba" else (H - th)/2 if v == "centro" else H - th - 60
    return x, y

def preview_grid(h, v):
    grid = [[" ", " ", " "],[" ", " ", " "],[" ", " ", " "]]
    col_map = {"izquierda":0,"centro":1,"derecha":2}
    row_map = {"arriba":0,"centro":1,"abajo":2}
    grid[row_map[v]][col_map[h]] = "X"
    return "\n".join(["[ " + " | ".join(r) + " ]" for r in grid])

def generar_preview_real(textos, imagenes):

    W, H = 1100, 850
    base = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(base)

    cell_w = W//2
    cell_h = H//4
    orden = [7,0,1,6,5,2,3,4]

    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()

    for i, idx in enumerate(orden):

        col = i % 2
        row = i // 2

        x = col * cell_w
        y = row * cell_h

        page = Image.new("RGB", (cell_h, cell_w), "white")
        pdraw = ImageDraw.Draw(page)

        if imagenes[idx]:
            img = Image.open(imagenes[idx]).resize((cell_h, cell_w))
            page.paste(img, (0,0))

        if textos[idx]:
            pdraw.text((20,20), textos[idx][:50], fill="black", font=font)

        page = page.rotate(-90 if i in [0,2,4,6] else 90, expand=True)

        base.paste(page, (x,y))
        draw.rectangle([x,y,x+cell_w,y+cell_h], outline="black")

    return base

def crear_imagen_instagram(texto, imagen, n):

    W,H = 1080,1350
    base = Image.new("RGB",(W,H),"white")

    if imagen:
        img = Image.open(imagen).resize((W,H))
        base.paste(img,(0,0))

    draw = ImageDraw.Draw(base,"RGBA")

    try:
        font = ImageFont.truetype("arial.ttf",40)
    except:
        font = ImageFont.load_default()

    if texto:
        draw.text((60,60), texto[:100], fill="white", font=font)

    draw.text((20,H-40),"FanzineLab · Vindria · CC",fill=(255,255,255,120),font=font)

    meta = PngImagePlugin.PngInfo()
    meta.add_text("Author","FanzineLab por Vindria")

    if not os.path.exists("fanzines"):
        os.makedirs("fanzines")

    path = f"fanzines/ig_{n}.png"
    base.save(path, pnginfo=meta)

    return path

# ======================
# VISTA PREVIA
# ======================

if pagina == "Vista previa":

    st.title("👁️ Vista previa")

    if not st.session_state.datos:
        st.warning("Primero crea tu fanzine")
        st.stop()

    datos = st.session_state.datos

    textos = datos["textos"]
    imagenes = datos["imagenes"]
    alineaciones = datos["alineaciones"]
    titulo = datos["titulo"]

    st.markdown("### 📐 Posición")

    cols = st.columns(4)

    for i in range(8):
        with cols[i%4]:
            st.text(f"P{i+1}")
            st.text(preview_grid(*alineaciones[i]))

    st.markdown("### 🧾 Vista de impresión")

    img_preview = generar_preview_real(textos, imagenes)
    st.image(img_preview, width="stretch")

    if st.button("✏️ Volver a editar"):
        st.session_state.pagina = "Crear"
        st.rerun()

    # PDF
    if st.button("📄 Generar PDF"):

        if not os.path.exists("fanzines"):
            os.makedirs("fanzines")

        path = "fanzines/fanzine.pdf"

        c = canvas.Canvas(path, pagesize=letter)
        c.setAuthor("FanzineLab por Vindria")

        width,height = letter
        style = getSampleStyleSheet()["Normal"]

        cell_w = width/2
        cell_h = height/4
        orden = [7,0,1,6,5,2,3,4]

        for i,idx in enumerate(orden):

            col = i%2
            row = i//2

            x = col*cell_w
            y = height-(row+1)*cell_h

            ang = -90 if i in [0,2,4,6] else 90

            c.saveState()
            c.translate(x+cell_w/2,y+cell_h/2)
            c.rotate(ang)

            if imagenes[idx]:
                img = Image.open(imagenes[idx])
                c.drawImage(ImageReader(img),-cell_h/2,-cell_w/2,cell_h,cell_w)

            if textos[idx]:
                p = Paragraph(textos[idx], style)
                tw,th = p.wrap(cell_h-40,cell_w-40)

                px,py = calcular_posicion(*alineaciones[idx],cell_h,cell_w,tw,th)
                p.drawOn(c,-cell_h/2+px,-cell_w/2+py)

            c.setFont("Helvetica",6)
            c.setFillGray(0.6)
            c.drawString(-cell_h/2+5,-cell_w/2+5,"FanzineLab · Vindria · CC")

            c.restoreState()
            c.rect(x,y,cell_w,cell_h)

        c.save()

        st.session_state.pdf_path = path
        st.success("PDF generado")

    if st.session_state.pdf_path:
        with open(st.session_state.pdf_path,"rb") as f:
            st.download_button("⬇️ Descargar PDF", f, "fanzine.pdf")

    # INSTAGRAM
    if st.button("📸 Generar imágenes Instagram"):

        paths = []
        for i in range(8):
            paths.append(crear_imagen_instagram(textos[i], imagenes[i], i+1))

        st.session_state.ig_paths = paths

    if st.session_state.ig_paths:

        cols = st.columns(2)

        for i,path in enumerate(st.session_state.ig_paths):

            with cols[i%2]:
                st.image(path, width="stretch")

                with open(path,"rb") as f:
                    st.download_button(f"⬇️ Página {i+1}", f, f"pagina_{i+1}.png")

    # WHATSAPP
    msg = urllib.parse.quote(f"Mi fanzine: {titulo}")
    st.link_button("📱 Compartir en WhatsApp", f"https://wa.me/?text={msg}")
