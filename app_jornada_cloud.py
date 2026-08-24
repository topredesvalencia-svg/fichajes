import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import io
import openpyxl
from openpyxl.styles import PatternFill, Alignment, Font, Border, Side

# ============= CONFIGURACIÓN STREAMLIT =============
st.set_page_config(
    page_title="Mi Jornada - TopRedesValencia",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
    :root {
        --color-primary: #E01B7D;
    }
    
    .main {
        padding: 2rem;
    }
    
    h1, h2, h3 {
        color: #E01B7D;
    }
    
    .metric-card {
        background-color: #f8f3ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #E01B7D;
    }
    </style>
    """, unsafe_allow_html=True)

# ============= FUNCIONES DE GOOGLE SHEETS =============

@st.cache_resource
def conectar_google_sheets():
    """Conecta con Google Sheets usando credenciales de Streamlit Secrets"""
    try:
        # Para desarrollo local, usar archivo de credenciales
        # Para Streamlit Cloud, usar st.secrets
        
        if "google_sheets_credentials" in st.secrets:
            creds_dict = st.secrets["google_sheets_credentials"]
        else:
            # Cargar desde archivo local para desarrollo
            try:
                with open("credentials.json") as f:
                    creds_dict = json.load(f)
            except FileNotFoundError:
                st.error("❌ Credenciales no configuradas. Ver instrucciones en la barra lateral.")
                st.stop()
        
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        return client
    except Exception as e:
        st.error(f"Error conectando a Google Sheets: {str(e)}")
        return None

def obtener_google_sheet(client, sheet_name="Mi Jornada"):
    """Obtiene la hoja de Google Sheets"""
    try:
        # Intenta abrir por nombre
        spreadsheet = client.open(sheet_name)
        worksheet = spreadsheet.sheet1
        return spreadsheet, worksheet
    except:
        # Si no existe, crea una nueva
        try:
            spreadsheet = client.create(sheet_name)
            worksheet = spreadsheet.sheet1
            
            # Agregar encabezados
            worksheet.append_row(['Fecha', 'Entrada', 'Salida', 'Horas'])
            
            return spreadsheet, worksheet
        except Exception as e:
            st.error(f"Error creando Google Sheet: {str(e)}")
            return None, None

def cargar_datos_google():
    """Carga datos de Google Sheets"""
    try:
        client = conectar_google_sheets()
        if not client:
            return pd.DataFrame(columns=['Fecha', 'Entrada', 'Salida', 'Horas'])
        
        spreadsheet, worksheet = obtener_google_sheet(client)
        if worksheet is None:
            return pd.DataFrame(columns=['Fecha', 'Entrada', 'Salida', 'Horas'])
        
        datos = worksheet.get_all_values()
        
        if len(datos) <= 1:
            return pd.DataFrame(columns=['Fecha', 'Entrada', 'Salida', 'Horas'])
        
        df = pd.DataFrame(datos[1:], columns=datos[0])
        
        # Convertir tipos
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df['Horas'] = pd.to_numeric(df['Horas'], errors='coerce')
        
        return df.dropna(subset=['Fecha'])
    
    except Exception as e:
        st.error(f"Error cargando datos: {str(e)}")
        return pd.DataFrame(columns=['Fecha', 'Entrada', 'Salida', 'Horas'])

def guardar_datos_google(df):
    """Guarda datos en Google Sheets"""
    try:
        client = conectar_google_sheets()
        if not client:
            st.error("No se pudo conectar a Google Sheets")
            return False
        
        spreadsheet, worksheet = obtener_google_sheet(client)
        if worksheet is None:
            return False
        
        # Limpiar hoja
        worksheet.clear()
        
        # Agregar encabezados
        worksheet.append_row(['Fecha', 'Entrada', 'Salida', 'Horas'])
        
        # Agregar datos
        for idx, row in df.iterrows():
            worksheet.append_row([
                row['Fecha'].strftime('%Y-%m-%d'),
                row['Entrada'],
                row['Salida'],
                str(row['Horas'])
            ])
        
        return True
    except Exception as e:
        st.error(f"Error guardando datos: {str(e)}")
        return False

def calcular_horas(entrada, salida):
    """Calcula horas entre entrada y salida"""
    if not entrada or not salida:
        return None
    
    if isinstance(entrada, str):
        entrada = pd.to_datetime(entrada, format='%H:%M').time()
    if isinstance(salida, str):
        salida = pd.to_datetime(salida, format='%H:%M').time()
    
    dt_entrada = datetime.combine(datetime.today(), entrada)
    dt_salida = datetime.combine(datetime.today(), salida)
    
    if dt_salida < dt_entrada:
        dt_salida += timedelta(days=1)
    
    diff = dt_salida - dt_entrada
    horas = diff.total_seconds() / 3600
    return round(horas, 2)

def formato_horas(horas):
    """Formatea horas decimales a formato H:MM"""
    if pd.isna(horas) or horas is None:
        return "—"
    hours = int(horas)
    minutes = int((horas - hours) * 60)
    return f"{hours}h {minutes}m"

# ============= SIDEBAR - CONFIGURACIÓN =============

with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    
    with st.expander("🔑 Credenciales Google Sheets", expanded=False):
        st.markdown("""
        ### Pasos para conectar:
        
        1. **Crear Google Cloud Project**
           - Ve a [Google Cloud Console](https://console.cloud.google.com/)
           - Crea un nuevo proyecto
        
        2. **Activar API de Sheets**
           - Busca "Google Sheets API"
           - Haz clic en "Activar"
        
        3. **Crear credenciales de servicio**
           - Ve a "Credenciales"
           - Crea una "Cuenta de servicio"
           - Descarga el JSON
        
        4. **Para desarrollo local:**
           - Guarda el JSON como `credentials.json`
           - En la carpeta del proyecto
        
        5. **Para Streamlit Cloud:**
           - Copia el contenido del JSON
           - Guárdalo en Secrets (en Streamlit Cloud dashboard)
           - Nombre: `google_sheets_credentials`
        
        ---
        
        **Alternativa rápida:**
        - [Sigue esta guía en 5 minutos](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app)
        """)
    
    st.divider()
    
    st.markdown("## 📋 Menú")
    opcion = st.radio(
        "Selecciona una opción:",
        ["📝 Registro Diario", "📊 Historial", "📥 Exportar Excel", "📈 Estadísticas"]
    )

# ============= HEADER =============

col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("## 🐾")
with col2:
    st.title("Mi Jornada")
    st.markdown("**TopRedesValencia** • Registro de horas laborales")

# Cargar datos
df = cargar_datos_google()

# ============= SECCIÓN 1: REGISTRO DIARIO =============

if opcion == "📝 Registro Diario":
    st.markdown("## Registro de Entrada y Salida")
    
    fecha_hoy = datetime.today().date()
    registros_hoy = df[df['Fecha'].dt.date == fecha_hoy]
    
    # Estado actual
    if not registros_hoy.empty:
        ultima_jornada = registros_hoy.iloc[-1]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Última Entrada", ultima_jornada['Entrada'])
        with col2:
            st.metric("Última Salida", ultima_jornada['Salida'] if pd.notna(ultima_jornada['Salida']) else "—")
        with col3:
            st.metric("Total Hoy", formato_horas(registros_hoy['Horas'].sum()))
    
    st.divider()
    
    # Formulario
    st.markdown("### Agregar Jornada")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fecha = st.date_input("Fecha", value=fecha_hoy, key="fecha_registro")
    with col2:
        entrada = st.time_input("Entrada", value=datetime.strptime("09:00", "%H:%M").time())
    with col3:
        salida = st.time_input("Salida", value=datetime.strptime("18:00", "%H:%M").time())
    
    # Calcular
    horas_calc = calcular_horas(entrada, salida)
    st.info(f"**Horas trabajadas:** {formato_horas(horas_calc)}")
    
    # Botón
    if st.button("✅ Registrar Jornada", type="primary", use_container_width=True):
        nueva_fila = pd.DataFrame({
            'Fecha': [pd.Timestamp(fecha)],
            'Entrada': [entrada.strftime("%H:%M")],
            'Salida': [salida.strftime("%H:%M")],
            'Horas': [horas_calc]
        })
        
        df = pd.concat([df, nueva_fila], ignore_index=True)
        df = df.sort_values('Fecha').reset_index(drop=True)
        
        if guardar_datos_google(df):
            st.success("✅ Jornada registrada correctamente")
            st.rerun()
        else:
            st.error("❌ Error al guardar")

# ============= SECCIÓN 2: HISTORIAL =============

elif opcion == "📊 Historial":
    st.markdown("## Historial de Jornadas")
    
    if df.empty:
        st.warning("No hay registros aún")
    else:
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fecha_desde = st.date_input("Desde", value=datetime.today().date() - timedelta(days=30))
        with col2:
            fecha_hasta = st.date_input("Hasta", value=datetime.today().date())
        with col3:
            st.write("")
        
        # Filtrar
        df_filtrado = df[
            (df['Fecha'].dt.date >= fecha_desde) & 
            (df['Fecha'].dt.date <= fecha_hasta)
        ].sort_values('Fecha', ascending=False)
        
        if df_filtrado.empty:
            st.info("No hay registros en este período")
        else:
            st.markdown("### Registros")
            
            editar = st.checkbox("✏️ Habilitar edición")
            
            if editar:
                st.markdown("**Modifica los datos directamente**")
                
                for idx in df_filtrado.index:
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                    
                    with col1:
                        fecha_edit = st.date_input(
                            "Fecha",
                            value=df.loc[idx, 'Fecha'].date(),
                            key=f"fecha_{idx}",
                            label_visibility="collapsed"
                        )
                        df.loc[idx, 'Fecha'] = pd.Timestamp(fecha_edit)
                    
                    with col2:
                        entrada_edit = st.time_input(
                            "Entrada",
                            value=pd.to_datetime(df.loc[idx, 'Entrada'], format='%H:%M').time(),
                            key=f"entrada_{idx}",
                            label_visibility="collapsed"
                        )
                        df.loc[idx, 'Entrada'] = entrada_edit.strftime("%H:%M")
                    
                    with col3:
                        salida_edit = st.time_input(
                            "Salida",
                            value=pd.to_datetime(df.loc[idx, 'Salida'], format='%H:%M').time(),
                            key=f"salida_{idx}",
                            label_visibility="collapsed"
                        )
                        df.loc[idx, 'Salida'] = salida_edit.strftime("%H:%M")
                    
                    with col4:
                        horas_calc = calcular_horas(df.loc[idx, 'Entrada'], df.loc[idx, 'Salida'])
                        st.metric("Horas", formato_horas(horas_calc), label_visibility="collapsed")
                        df.loc[idx, 'Horas'] = horas_calc
                    
                    with col5:
                        if st.button("🗑️", key=f"delete_{idx}"):
                            df = df.drop(idx).reset_index(drop=True)
                            if guardar_datos_google(df):
                                st.success("Eliminado")
                                st.rerun()
                
                if st.button("💾 Guardar cambios", type="primary", use_container_width=True):
                    if guardar_datos_google(df):
                        st.success("✅ Cambios guardados")
                        st.rerun()
            
            else:
                # Vista normal
                tabla = df_filtrado.copy()
                tabla['Fecha'] = tabla['Fecha'].dt.strftime('%Y-%m-%d')
                tabla['Horas'] = tabla['Horas'].apply(formato_horas)
                
                st.dataframe(tabla, use_container_width=True, hide_index=True)
            
            # Resumen
            st.divider()
            st.markdown("### Resumen del Período")
            
            col1, col2, col3, col4 = st.columns(4)
            
            total_horas = df_filtrado['Horas'].sum()
            total_jornadas = len(df_filtrado)
            promedio = total_horas / total_jornadas if total_jornadas > 0 else 0
            
            with col1:
                st.metric("Jornadas", total_jornadas)
            with col2:
                st.metric("Total Horas", formato_horas(total_horas))
            with col3:
                st.metric("Promedio/Día", formato_horas(promedio))
            with col4:
                st.metric("Período (días)", (fecha_hasta - fecha_desde).days + 1)

# ============= SECCIÓN 3: EXPORTAR EXCEL =============

elif opcion == "📥 Exportar Excel":
    st.markdown("## Exportar a Excel")
    
    if df.empty:
        st.warning("No hay datos para exportar")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            mes = st.selectbox(
                "Mes",
                range(1, 13),
                format_func=lambda x: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                                       "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"][x-1]
            )
        
        with col2:
            año = st.number_input("Año", value=datetime.today().year, min_value=2020)
        
        # Filtrar
        df_mes = df[
            (df['Fecha'].dt.month == mes) &
            (df['Fecha'].dt.year == año)
        ].sort_values('Fecha')
        
        if df_mes.empty:
            st.warning(f"No hay registros para este mes")
        else:
            # Preview
            st.markdown("### Vista Previa")
            tabla = df_mes.copy()
            tabla['Fecha'] = tabla['Fecha'].dt.strftime('%Y-%m-%d')
            tabla['Horas'] = tabla['Horas'].apply(formato_horas)
            
            st.dataframe(tabla, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Jornadas", len(df_mes))
            with col2:
                st.metric("Total Horas", formato_horas(df_mes['Horas'].sum()))
            with col3:
                st.metric("Promedio/Día", formato_horas(df_mes['Horas'].mean()))
            
            # Crear Excel en memoria
            st.divider()
            st.markdown("### Descargar")
            
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export = df_mes.copy()
                df_export['Fecha'] = df_export['Fecha'].dt.strftime('%Y-%m-%d')
                df_export['Horas'] = df_export['Horas'].apply(formato_horas)
                
                # Agregar total
                total_row = pd.DataFrame({
                    'Fecha': ['TOTAL'],
                    'Entrada': [''],
                    'Salida': [''],
                    'Horas': [formato_horas(df_mes['Horas'].sum())]
                })
                df_export = pd.concat([df_export, total_row], ignore_index=True)
                
                df_export.to_excel(writer, sheet_name='Jornada', index=False)
                
                # Formatear
                worksheet = writer.sheets['Jornada']
                
                fill_header = PatternFill(start_color="E01B7D", end_color="E01B7D", fill_type="solid")
                font_header = Font(bold=True, color="FFFFFF")
                alignment = Alignment(horizontal="center", vertical="center")
                
                for col_num in range(1, 5):
                    cell = worksheet.cell(row=1, column=col_num)
                    cell.fill = fill_header
                    cell.font = font_header
                    cell.alignment = alignment
                
                # Formatear total
                for col_num in range(1, 5):
                    cell = worksheet.cell(row=len(df_export), column=col_num)
                    cell.fill = fill_header
                    cell.font = font_header
                    cell.alignment = alignment
                
                worksheet.column_dimensions['A'].width = 12
                worksheet.column_dimensions['B'].width = 12
                worksheet.column_dimensions['C'].width = 12
                worksheet.column_dimensions['D'].width = 15
            
            output.seek(0)
            
            st.download_button(
                label="📥 Descargar Excel",
                data=output.getvalue(),
                file_name=f"jornada_{año}-{mes:02d}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )

# ============= SECCIÓN 4: ESTADÍSTICAS =============

elif opcion == "📈 Estadísticas":
    st.markdown("## Estadísticas Generales")
    
    if df.empty:
        st.warning("No hay datos para mostrar")
    else:
        col1, col2 = st.columns(2)
        with col1:
            fecha_desde = st.date_input("Desde", value=datetime.today().date() - timedelta(days=90))
        with col2:
            fecha_hasta = st.date_input("Hasta", value=datetime.today().date())
        
        df_stats = df[
            (df['Fecha'].dt.date >= fecha_desde) &
            (df['Fecha'].dt.date <= fecha_hasta)
        ]
        
        if df_stats.empty:
            st.warning("No hay registros en este período")
        else:
            st.markdown("### Resumen General")
            col1, col2, col3, col4 = st.columns(4)
            
            total_horas = df_stats['Horas'].sum()
            total_jornadas = len(df_stats)
            
            with col1:
                st.metric("Total Horas", formato_horas(total_horas))
            with col2:
                st.metric("Jornadas", total_jornadas)
            with col3:
                st.metric("Promedio/Día", formato_horas(total_horas / total_jornadas if total_jornadas > 0 else 0))
            with col4:
                st.metric("Días del Período", (fecha_hasta - fecha_desde).days + 1)
            
            st.divider()
            
            # Gráfico
            st.markdown("### Horas Trabajadas por Día")
            grafico_data = df_stats.copy()
            grafico_data['Fecha'] = grafico_data['Fecha'].dt.strftime('%Y-%m-%d')
            grafico_agg = grafico_data.groupby('Fecha')['Horas'].sum()
            
            st.bar_chart(grafico_agg, height=400)
            
            st.divider()
            
            # Semanal
            st.markdown("### Análisis Semanal")
            semanal = df_stats.copy()
            semanal['Semana'] = semanal['Fecha'].dt.strftime('%Y-W%U')
            semanal_agg = semanal.groupby('Semana')['Horas'].agg(['sum', 'count', 'mean']).round(2)
            semanal_agg.columns = ['Total Horas', 'Jornadas', 'Promedio']
            
            st.dataframe(semanal_agg, use_container_width=True)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #999; font-size: 0.9rem; margin-top: 2rem;'>
    <p>🔧 <strong>TopRedesValencia</strong> • Registro de Jornada Laboral</p>
    <p>📱 683 597 759 • 🌐 topredesvalencia.com</p>
    <p style='font-size: 0.85rem; margin-top: 1rem;'>
        Datos sincronizados con Google Sheets • Sin pérdida de información
    </p>
</div>
""", unsafe_allow_html=True)
