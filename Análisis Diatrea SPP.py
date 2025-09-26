import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

# ======================
# Funciones de exportación
# ======================
def exportar_excel(datos_hacienda, muestreo_df, ii, control):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame([datos_hacienda]).to_excel(writer, sheet_name="Hacienda", index=False)
        muestreo_df.to_excel(writer, sheet_name="Muestreo", index=False)
        pd.DataFrame([{"Índice de Infestación (%)": ii, "Estado": control["estado"], "Acciones": control["acciones"]}]).to_excel(writer, sheet_name="Resultados", index=False)
    output.seek(0)
    return output

def exportar_pdf(datos_hacienda, muestreo_df, ii, control, fig):
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Hacienda
    elements.append(Paragraph("Resultados del Análisis de Diatrea SPP", styles["Title"]))
    elements.append(Spacer(1, 12))
    for k, v in datos_hacienda.items():
        elements.append(Paragraph(f"<b>{k}:</b> {v}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Muestreo
    if not muestreo_df.empty:
        tabla = [muestreo_df.columns.tolist()] + muestreo_df.values.tolist()
        table = Table(tabla)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("GRID", (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

    # Resultados
    elements.append(Paragraph(f"Índice de Infestación (I.I): <b>{ii:.2f}%</b>", styles["Normal"]))
    elements.append(Paragraph(f"Estado del Cultivo: <b>{control['estado']}</b>", styles["Normal"]))
    elements.append(Paragraph(f"Control sugerido: <b>{control['acciones']}</b>", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Gráfico
    img_buf = BytesIO()
    fig.savefig(img_buf, format="png")
    img_buf.seek(0)
    elements.append(RLImage(img_buf))

    doc.build(elements)
    output.seek(0)
    return output

# ======================
# Configuración de estilo global
# ======================
st.set_page_config(page_title="Proyecto Final - Caña de Azúcar", layout="centered")
st.markdown(
    """
    <style>
    .stApp { background-color: #5ACC12; color: black; font-family: Arial, sans-serif; }
    div.stButton > button { background-color: #ff9800; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; transition: 0.3s; }
    div.stButton > button:hover { background-color: #e68900; color: white; }
    </style>
    """,
    unsafe_allow_html=True
)

# ======================
# Página de inicio
# ======================
if "page" not in st.session_state:
    st.session_state.page = "inicio"

if st.session_state.page == "inicio":
    st.markdown(
        """
        <h1 style='text-align: center; color: black;'>¡BIENVENIDOS!</h1>
        <h3 style='text-align: center; color: black;'>Proyecto final del curso de cultivo de caña de azúcar XI</h3>
        <div style="text-align: center; background-color: rgba(255, 255, 255, 0.6); padding: 10px; border-radius: 10px; border: 2px solid black;">
            <p style="color: black; font-weight: bold;">Analiza Diatrea SPP en el cultivo de caña.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", use_container_width=True)
        if st.button("➡️ Continuar"):
            st.session_state.page = "analisis"

# ======================
# Página de análisis
# ======================
elif st.session_state.page == "analisis":
    st.title("Análisis de Diatrea SPP")

    # 1. Datos de identificación de la suerte
    st.header("1. Datos de identificación de la suerte")
    datos_hacienda = {
        "Hacienda": st.text_input("Hacienda"),
        "Suerte": st.text_input("Suerte"),
        "Variedad": st.text_input("Variedad"),
        "Fecha de siembra": st.date_input("Fecha de siembra"),
        "Fecha de corte": st.date_input("Fecha de corte"),
        "Edad de corte (meses)": st.number_input("Edad de corte (meses)", min_value=0),
        "Número de corte": st.number_input("Número de corte", min_value=0),
        "Evaluador": st.text_input("Evaluador"),
        "Fecha de evaluación": st.date_input("Fecha de evaluación"),
    }

    # 2. Información del Muestreo
    st.header("2. Información del Muestreo")

    if "muestreo" not in st.session_state:
        st.session_state.muestreo = []

    entrenudos_input = st.number_input("Total entrenudos", min_value=1, step=1, key="entrenudos")
    barrenados_input = st.number_input("Entrenudos barrenados", min_value=0, max_value=entrenudos_input, step=1, key="barrenados")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Agregar tallo"):
            st.session_state.muestreo.append({
                "Tallo": len(st.session_state.muestreo)+1,
                "Total entrenudos": entrenudos_input,
                "Entrenudos barrenados": barrenados_input
            })
    with col2:
        if st.button("❌ Eliminar último") and st.session_state.muestreo:
            st.session_state.muestreo.pop()
    with col3:
        if st.button("🗑️ Eliminar todo"):
            st.session_state.muestreo.clear()

    # Mostrar tabla estilizada
    muestreo_df = pd.DataFrame(st.session_state.muestreo)
    if not muestreo_df.empty:
        def color_fila(row):
            return ['background-color: #f2f2f2' if row.name % 2 == 0 else 'background-color: white']*len(row)

        styled_df = muestreo_df.style.apply(color_fila, axis=1).set_properties(**{
            'text-align': 'center',
            'color': 'black',
            'border-color': 'black'
        }).set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#555555'),
                                         ('color', 'white'),
                                         ('font-weight', 'bold'),
                                         ('text-align', 'center')]},
        ])
        st.write("Tabla de muestreo de tallos:")
        st.write(styled_df)

        # 3. Resultados
        total_entrenudos = muestreo_df["Total entrenudos"].sum()
        total_barrenados = muestreo_df["Entrenudos barrenados"].sum()
        ii = (total_barrenados / total_entrenudos) * 100 if total_entrenudos > 0 else 0

        if ii < 4:
            estado = "SANO"
            acciones = "15 Parejas de moscas / Ha - 7 meses"
        elif 4 <= ii <= 10:
            estado = "DAÑADO"
            acciones = "15 Parejas de moscas / Ha - 5 y 7 meses, 50 Pulg de avispas / Ha - 7 meses"
        else:
            estado = "MUY DAÑADO"
            acciones = "15 Parejas de moscas / Ha - 5, 7 y 9 meses, 50 Pulg de avispas / Ha - 5 y 7 meses"

        control = {"estado": estado, "acciones": acciones}

        st.header("3. Resultados")
        st.write(f"Índice de Infestación (I.I): **{ii:.2f}%**")
        st.write(f"Estado del Cultivo: **{estado}**")
        st.write(f"Control sugerido: **{acciones}**")

        # Gráfico circular
        sanos = total_entrenudos - total_barrenados
        afectados = total_barrenados
        fig, ax = plt.subplots()
        ax.pie([sanos, afectados], labels=["Sanos", "Afectados"], autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

        # 4. Exportar resultados
        excel = exportar_excel(datos_hacienda, muestreo_df, ii, control)
        st.download_button("📊 Exportar a Excel", excel, file_name="analisis_diatrea.xlsx")

        pdf = exportar_pdf(datos_hacienda, muestreo_df, ii, control, fig)
        st.download_button("📄 Exportar a PDF", pdf, file_name="analisis_diatrea.pdf")
