import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
import os
import json
import openpyxl
from openpyxl.styles import PatternFill, Alignment, Font

# ============= CONFIGURACIÓN =============
st.set_page_config(
    page_title="Mi Jornada - TopRedesValencia",
    page_icon="🐾",
    layout="wide"
)

# ============= CSS CORPORATIVO =============
st.markdown("""<style>
    /* Variables Corporativas - Colores reales de TopRedesValencia */
    :root {
        --primary: #E5309F;
        --primary-dark: #B31378;
        --accent: #E5309F;
        --light-bg: #FFF5F9;
        --text-dark: #FFFFFF;
        --text-light: #E8E8E8;
        --border-color: #E0E0E0;
    }
    
    /* Colores y Tipografía */
    * {
        color: #FFFFFF;
    }
    
    body {
        background-color: #1A1A1A;
        color: #FFFFFF;
    }
    
    p {
        color: #FFFFFF;
    }
    
    label {
        color: #FFFFFF !important;
        font-weight: 600;
    }
    
    /* Header Principal */
    .header-corporate {
        background: linear-gradient(135deg, #E5309F 0%, #B31378 100%);
        color: white;
        padding: 30px 40px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 8px 20px rgba(229, 48, 159, 0.3);
    }
    
    .header-corporate h1 {
        color: white;
        margin: 10px 0 0 0;
        font-size: 2.2em;
        font-weight: 900;
        letter-spacing: 0px;
    }
    
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 5px;
    }
    
    .logo-container svg {
        width: 100px;
        height: 100px;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.15));
    }
    
    /* Títulos */
    h1, h2, h3 {
        color: #FFFFFF;
        font-weight: bold;
    }
    
    /* Botones */
    .stButton > button {
        background-color: var(--primary);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: bold;
        font-size: 1em;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(224, 27, 125, 0.2);
    }
    
    .stButton > button:hover {
        background-color: var(--primary-dark);
        box-shadow: 0 4px 12px rgba(224, 27, 125, 0.3);
        transform: translateY(-2px);
    }
    
    .stButton > button[type="primary"] {
        background-color: var(--accent);
    }
    
    .stButton > button[type="primary"]:hover {
        background-color: var(--primary);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        border-bottom: 3px solid #E5309F;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #2A2A2A;
        border: 2px solid #404040;
        border-radius: 8px 8px 0 0;
        color: #CCCCCC;
        font-weight: 700;
        padding: 14px 24px;
        font-size: 1.05em;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #333333;
        border-color: #E5309F;
        color: #FFFFFF;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #E5309F 0%, #B31378 100%);
        color: #FFFFFF;
        border-color: #E5309F;
        box-shadow: 0 4px 8px rgba(229, 48, 159, 0.2);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stTimeInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: #2A2A2A !important;
        border: 2px solid #404040 !important;
        border-radius: 8px;
        padding: 10px;
        font-size: 1em;
        color: #FFFFFF !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stDateInput > div > div > input:focus,
    .stTimeInput > div > div > input:focus {
        border-color: #E5309F !important;
        box-shadow: 0 0 0 3px rgba(229, 48, 159, 0.2) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #888888 !important;
    }
    
    /* Cronómetro */
    .cronometro {
        font-size: 60px;
        font-weight: bold;
        color: var(--primary);
        text-align: center;
        padding: 40px;
        background: linear-gradient(135deg, var(--light-bg) 0%, rgba(224, 27, 125, 0.05) 100%);
        border: 3px solid var(--primary);
        border-radius: 15px;
        font-family: 'Courier New', monospace;
        box-shadow: 0 4px 15px rgba(224, 27, 125, 0.15);
        margin: 20px 0;
    }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, var(--light-bg) 0%, white 100%);
        border: 2px solid var(--border-color);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Badges */
    .admin-badge {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9em;
        box-shadow: 0 2px 8px rgba(255, 165, 0, 0.3);
        display: inline-block;
    }
    
    .badge-activo {
        background: #4CAF50;
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.85em;
    }
    
    .badge-inactivo {
        background: #F44336;
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.85em;
    }
    
    /* Alert/Warning/Info */
    .stWarning, .stError, .stSuccess, .stInfo {
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        color: #FFFFFF;
    }
    
    .stSuccess {
        background-color: #1B5E20;
        border-color: #28A745;
        border-left: 4px solid #4CAF50;
    }
    
    .stError {
        background-color: #B71C1C;
        border-left: 4px solid #DC3545;
    }
    
    .stWarning {
        background-color: #F57F17;
        border-left: 4px solid #FF9800;
    }
    
    .stInfo {
        background-color: #01579B;
        border-left: 4px solid #2196F3;
    }
    
    /* Dataframe */
    .stDataFrame {
        border: 2px solid #404040;
        border-radius: 10px;
        overflow: hidden;
        background-color: #2A2A2A;
    }
    
    .stDataFrame th {
        background-color: #E5309F !important;
        color: #FFFFFF !important;
    }
    
    .stDataFrame td {
        color: #FFFFFF;
    }
    
    /* Divider */
    hr {
        border: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #E5309F, transparent);
        margin: 20px 0;
    }
    
    /* Footer */
    .footer-corporate {
        background: linear-gradient(135deg, #E5309F 0%, #B31378 100%);
        color: white;
        padding: 35px;
        text-align: center;
        border-radius: 15px;
        margin-top: 50px;
        box-shadow: 0 8px 20px rgba(229, 48, 159, 0.3);
    }
    
    .footer-corporate a {
        color: #FFE066;
        text-decoration: none;
        font-weight: bold;
        transition: color 0.3s ease;
    }
    
    .footer-corporate a:hover {
        color: #FFF;
        text-decoration: underline;
    }
    
    /* Responsivo */
    @media (max-width: 640px) {
        .header-corporate h1 {
            font-size: 1.8em;
        }
        .cronometro {
            font-size: 40px;
            padding: 20px;
        }
    }
</style>""", unsafe_allow_html=True)

# ============= INICIALIZAR SESSION STATE =============
if 'usuario_logeado' not in st.session_state:
    st.session_state.usuario_logeado = None
if 'es_admin' not in st.session_state:
    st.session_state.es_admin = False
if 'cronometro_activo' not in st.session_state:
    st.session_state.cronometro_activo = False
if 'tiempo_inicio' not in st.session_state:
    st.session_state.tiempo_inicio = None
if 'tiempo_pausado' not in st.session_state:
    st.session_state.tiempo_pausado = 0

# Crear carpetas
if not os.path.exists('datos_usuarios'):
    os.makedirs('datos_usuarios')
if not os.path.exists('datos_sistema'):
    os.makedirs('datos_sistema')

# ============= FUNCIONES =============
def cargar_usuarios_registrados():
    archivo_usuarios = 'datos_sistema/usuarios.json'
    if os.path.exists(archivo_usuarios):
        with open(archivo_usuarios, 'r') as f:
            return json.load(f)
    return {}

def guardar_usuarios_registrados(usuarios):
    archivo_usuarios = 'datos_sistema/usuarios.json'
    with open(archivo_usuarios, 'w') as f:
        json.dump(usuarios, f, indent=2)

def registrar_usuario(nombre, contra):
    usuarios = cargar_usuarios_registrados()
    if nombre.lower() in usuarios:
        return False, "Este usuario ya existe"
    usuarios[nombre.lower()] = {
        'nombre': nombre,
        'contraseña': contra,
        'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'activo': True
    }
    guardar_usuarios_registrados(usuarios)
    return True, "Usuario registrado exitosamente"

def verificar_usuario(nombre, contra):
    usuarios = cargar_usuarios_registrados()
    if nombre.lower() not in usuarios:
        return False, "Usuario no encontrado"
    usuario = usuarios[nombre.lower()]
    if not usuario.get('activo', False):
        return False, "Usuario desactivado por admin"
    if usuario['contraseña'] != contra:
        return False, "Contraseña incorrecta"
    return True, "OK"

def obtener_archivo_usuario(usuario):
    return f'datos_usuarios/{usuario.lower()}.csv'

def cargar_datos_usuario(usuario):
    archivo = obtener_archivo_usuario(usuario)
    if os.path.exists(archivo):
        df = pd.read_csv(archivo)
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        return df
    return pd.DataFrame(columns=['Fecha', 'Entrada', 'Salida', 'Horas'])

def guardar_datos_usuario(usuario, df):
    archivo = obtener_archivo_usuario(usuario)
    df_copy = df.copy()
    # Asegurar que Fecha es datetime
    df_copy['Fecha'] = pd.to_datetime(df_copy['Fecha'])
    # Convertir a string para CSV
    df_copy['Fecha'] = df_copy['Fecha'].dt.strftime('%Y-%m-%d')
    df_copy.to_csv(archivo, index=False)

def obtener_todos_usuarios():
    usuarios = cargar_usuarios_registrados()
    return sorted([u for u, v in usuarios.items() if v.get('activo', False)])

def formato_horas(horas):
    if pd.isna(horas) or horas is None:
        return "—"
    hours = int(horas)
    minutes = int((horas - hours) * 60)
    return f"{hours}h {minutes}m"

def formato_cronometro(segundos):
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    secs = int(segundos % 60)
    return f"{horas:02d}:{minutos:02d}:{secs:02d}"

def crear_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export = df.copy()
        df_export['Fecha'] = df_export['Fecha'].dt.strftime('%Y-%m-%d')
        df_export['Horas'] = df_export['Horas'].apply(formato_horas)
        
        total_row = pd.DataFrame({
            'Fecha': ['TOTAL'],
            'Entrada': [''],
            'Salida': [''],
            'Horas': [formato_horas(df['Horas'].sum())]
        })
        df_export = pd.concat([df_export, total_row], ignore_index=True)
        
        df_export.to_excel(writer, sheet_name='Jornada', index=False)
        worksheet = writer.sheets['Jornada']
        
        fill_header = PatternFill(start_color="E01B7D", end_color="E01B7D", fill_type="solid")
        font_header = Font(bold=True, color="FFFFFF")
        alignment = Alignment(horizontal="center", vertical="center")
        
        for col_num in range(1, 5):
            cell = worksheet.cell(row=1, column=col_num)
            cell.fill = fill_header
            cell.font = font_header
            cell.alignment = alignment
        
        for col_num in range(1, 5):
            cell = worksheet.cell(row=len(df_export), column=col_num)
            cell.fill = fill_header
            cell.font = font_header
            cell.alignment = alignment
        
        for col_num, width in enumerate([12, 12, 12, 15], 1):
            worksheet.column_dimensions[chr(64 + col_num)].width = width
    
    output.seek(0)
    return output.getvalue()

# ============= PANTALLA DE LOGIN =============
if not st.session_state.usuario_logeado:
    # Header
    st.markdown("""
    <div class="header-corporate">
        <div class="logo-container">
            <svg width="100" height="100" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="fucsia" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0" stop-color="#E5309F"/>
                  <stop offset="1" stop-color="#B31378"/>
                </linearGradient>
                <pattern id="malla" width="76" height="76" patternUnits="userSpaceOnUse" patternTransform="rotate(45 256 256)">
                  <path d="M0 0H76M0 0V76" stroke="#ffffff" stroke-opacity=".55" stroke-width="9"/>
                </pattern>
                <clipPath id="placa"><rect x="16" y="16" width="480" height="480" rx="104"/></clipPath>
              </defs>
              <rect x="16" y="16" width="480" height="480" rx="104" fill="url(#fucsia)"/>
              <g clip-path="url(#placa)">
                <rect x="16" y="16" width="480" height="480" fill="url(#malla)"/>
              </g>
              <g fill="#ffffff">
                <ellipse cx="205" cy="150" rx="36" ry="48" transform="rotate(-14 205 150)"/>
                <ellipse cx="307" cy="150" rx="36" ry="48" transform="rotate(14 307 150)"/>
                <ellipse cx="118" cy="226" rx="32" ry="44" transform="rotate(-38 118 226)"/>
                <ellipse cx="394" cy="226" rx="32" ry="44" transform="rotate(38 394 226)"/>
                <path d="M256 262 c56 0 106 40 118 92 c9 42 -22 78 -61 69 c-20 -5 -37 -14 -57 -14 c-20 0 -37 9 -57 14 c-39 9 -70 -27 -61 -69 c12 -52 62 -92 118 -92 z" fill="#ffffff"/>
              </g>
            </svg>
        </div>
        <h1>Registro de Jornada</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    tab_login, tab_registro = st.tabs(["🔓 Iniciar Sesión", "📝 Crear Cuenta"])
    
    with tab_login:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### 👤 Usuario")
            usuario = st.text_input("Nombre de usuario", placeholder="juan", key="login_user")
            contra = st.text_input("Contraseña", type="password", placeholder="••••••••", key="login_pass")
            
            if st.button("✅ ENTRAR", type="primary", use_container_width=True, key="btn_login"):
                if usuario.strip() and contra.strip():
                    success, msg = verificar_usuario(usuario, contra)
                    if success:
                        st.session_state.usuario_logeado = usuario.strip()
                        st.session_state.es_admin = False
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Completa todos los campos")
        
        st.divider()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### 🔐 Acceso Admin")
            admin_pass = st.text_input("Contraseña de admin", type="password", placeholder="••••••••", key="admin_pass")
            
            if st.button("🔓 ENTRAR COMO ADMIN", type="primary", use_container_width=True, key="btn_admin"):
                if admin_pass.strip() == "admin123":
                    st.session_state.usuario_logeado = "ADMIN"
                    st.session_state.es_admin = True
                    st.rerun()
                elif admin_pass.strip() == "":
                    st.error("Ingresa la contraseña de admin")
                else:
                    st.error("❌ Contraseña admin incorrecta")
    
    with tab_registro:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### 📝 Crear Nueva Cuenta")
            st.markdown("Ingresa tus datos para registrarte")
            
            nuevo_usuario = st.text_input("👤 Nombre de usuario", placeholder="juan", key="nuevo_user")
            nueva_contra = st.text_input("🔐 Contraseña", type="password", placeholder="••••••••", key="nueva_pass")
            nueva_contra_conf = st.text_input("🔐 Confirmar contraseña", type="password", placeholder="••••••••", key="nueva_pass_conf")
            
            st.divider()
            
            if st.button("✅ CREAR CUENTA", type="primary", use_container_width=True, key="btn_registro"):
                if not nuevo_usuario.strip():
                    st.error("Ingresa un nombre de usuario")
                elif not nueva_contra.strip():
                    st.error("Ingresa una contraseña")
                elif nueva_contra != nueva_contra_conf:
                    st.error("Las contraseñas no coinciden")
                elif len(nueva_contra) < 4:
                    st.error("La contraseña debe tener al menos 4 caracteres")
                else:
                    success, msg = registrar_usuario(nuevo_usuario.strip(), nueva_contra)
                    if success:
                        st.success("✅ Cuenta creada exitosamente. Ahora inicia sesión.")
                        st.balloons()
                    else:
                        st.error(msg)
    
    st.divider()
    st.markdown("""
    <div style="background: #FFF5F9; padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #E01B7D;">
        <strong>💡 Consejo:</strong> Si es tu primera vez, crea una cuenta. 
        <br><strong>🔑 Admin default:</strong> Contraseña: <code>admin123</code>
    </div>
    """, unsafe_allow_html=True)

else:
    # ============= INTERFAZ PRINCIPAL =============
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.button("🚪 Salir", use_container_width=True):
            st.session_state.usuario_logeado = None
            st.session_state.es_admin = False
            st.rerun()
    
    with col2:
        if st.session_state.es_admin:
            st.markdown("""
            <div class="header-corporate">
                <div class="logo-container">
                    <svg width="100" height="100" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
                      <defs>
                        <linearGradient id="fucsia2" x1="0" y1="0" x2="1" y2="1">
                          <stop offset="0" stop-color="#E5309F"/>
                          <stop offset="1" stop-color="#B31378"/>
                        </linearGradient>
                        <pattern id="malla2" width="76" height="76" patternUnits="userSpaceOnUse" patternTransform="rotate(45 256 256)">
                          <path d="M0 0H76M0 0V76" stroke="#ffffff" stroke-opacity=".55" stroke-width="9"/>
                        </pattern>
                        <clipPath id="placa2"><rect x="16" y="16" width="480" height="480" rx="104"/></clipPath>
                      </defs>
                      <rect x="16" y="16" width="480" height="480" rx="104" fill="url(#fucsia2)"/>
                      <g clip-path="url(#placa2)">
                        <rect x="16" y="16" width="480" height="480" fill="url(#malla2)"/>
                      </g>
                      <g fill="#ffffff">
                        <ellipse cx="205" cy="150" rx="36" ry="48" transform="rotate(-14 205 150)"/>
                        <ellipse cx="307" cy="150" rx="36" ry="48" transform="rotate(14 307 150)"/>
                        <ellipse cx="118" cy="226" rx="32" ry="44" transform="rotate(-38 118 226)"/>
                        <ellipse cx="394" cy="226" rx="32" ry="44" transform="rotate(38 394 226)"/>
                        <path d="M256 262 c56 0 106 40 118 92 c9 42 -22 78 -61 69 c-20 -5 -37 -14 -57 -14 c-20 0 -37 9 -57 14 c-39 9 -70 -27 -61 -69 c12 -52 62 -92 118 -92 z" fill="#ffffff"/>
                      </g>
                    </svg>
                </div>
                <h1>Panel Admin</h1>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="header-corporate">
                <div class="logo-container">
                    <svg width="100" height="100" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
                      <defs>
                        <linearGradient id="fucsia3" x1="0" y1="0" x2="1" y2="1">
                          <stop offset="0" stop-color="#E5309F"/>
                          <stop offset="1" stop-color="#B31378"/>
                        </linearGradient>
                        <pattern id="malla3" width="76" height="76" patternUnits="userSpaceOnUse" patternTransform="rotate(45 256 256)">
                          <path d="M0 0H76M0 0V76" stroke="#ffffff" stroke-opacity=".55" stroke-width="9"/>
                        </pattern>
                        <clipPath id="placa3"><rect x="16" y="16" width="480" height="480" rx="104"/></clipPath>
                      </defs>
                      <rect x="16" y="16" width="480" height="480" rx="104" fill="url(#fucsia3)"/>
                      <g clip-path="url(#placa3)">
                        <rect x="16" y="16" width="480" height="480" fill="url(#malla3)"/>
                      </g>
                      <g fill="#ffffff">
                        <ellipse cx="205" cy="150" rx="36" ry="48" transform="rotate(-14 205 150)"/>
                        <ellipse cx="307" cy="150" rx="36" ry="48" transform="rotate(14 307 150)"/>
                        <ellipse cx="118" cy="226" rx="32" ry="44" transform="rotate(-38 118 226)"/>
                        <ellipse cx="394" cy="226" rx="32" ry="44" transform="rotate(38 394 226)"/>
                        <path d="M256 262 c56 0 106 40 118 92 c9 42 -22 78 -61 69 c-20 -5 -37 -14 -57 -14 c-20 0 -37 9 -57 14 c-39 9 -70 -27 -61 -69 c12 -52 62 -92 118 -92 z" fill="#ffffff"/>
                      </g>
                    </svg>
                </div>
                <h1>Registro de Jornada</h1>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if st.session_state.es_admin:
            st.markdown('<span class="admin-badge">🔐 ADMIN</span>', unsafe_allow_html=True)
    
    st.divider()
    
    # ============= PANEL ADMIN =============
    if st.session_state.es_admin:
        tab_usuarios, tab_registros = st.tabs(["👥 Gestión de Usuarios", "📊 Registros"])
        
        with tab_usuarios:
            st.markdown("### 👥 Usuarios Registrados")
            
            usuarios_dict = cargar_usuarios_registrados()
            usuarios = obtener_todos_usuarios()
            
            if not usuarios_dict:
                st.warning("No hay usuarios registrados aún")
            else:
                data_usuarios = []
                for uid, udata in usuarios_dict.items():
                    df_usuario = cargar_datos_usuario(uid)
                    estado_badge = '<span class="badge-activo">✅ Activo</span>' if udata.get('activo', False) else '<span class="badge-inactivo">❌ Inactivo</span>'
                    data_usuarios.append({
                        'Usuario': udata['nombre'],
                        'Jornadas': len(df_usuario),
                        'Total Horas': formato_horas(df_usuario['Horas'].sum()) if not df_usuario.empty else "—",
                        'Registrado': udata['fecha_registro'],
                        'Estado': estado_badge
                    })
                
                df_usuarios_tabla = pd.DataFrame(data_usuarios)
                st.dataframe(df_usuarios_tabla, use_container_width=True, hide_index=True)
                
                st.divider()
                
                st.markdown("### ➕ Crear Usuario")
                col1, col2, col3 = st.columns(3)
                with col1:
                    nuevo_user_admin = st.text_input("Nombre de usuario", key="new_user_admin")
                with col2:
                    nueva_pass_admin = st.text_input("Contraseña", type="password", key="new_pass_admin")
                with col3:
                    st.write("")
                    if st.button("➕ CREAR", key="btn_crear_user_admin", use_container_width=True):
                        if nuevo_user_admin and nueva_pass_admin:
                            success, msg = registrar_usuario(nuevo_user_admin, nueva_pass_admin)
                            if success:
                                st.success(f"✅ Usuario {nuevo_user_admin} creado")
                                st.rerun()
                            else:
                                st.error(msg)
                        else:
                            st.error("Completa todos los campos")
                
                st.divider()
                
                st.markdown("### ⚙️ Activar/Desactivar Usuarios")
                usuario_a_gestionar = st.selectbox("Selecciona usuario", list(usuarios_dict.keys()), format_func=lambda x: usuarios_dict[x]['nombre'])
                
                usuario_data = usuarios_dict[usuario_a_gestionar]
                col1, col2 = st.columns(2)
                
                with col1:
                    if usuario_data.get('activo', False):
                        if st.button("❌ DESACTIVAR", use_container_width=True, key="btn_desactivar"):
                            usuarios_dict[usuario_a_gestionar]['activo'] = False
                            guardar_usuarios_registrados(usuarios_dict)
                            st.success(f"Usuario {usuario_data['nombre']} desactivado")
                            st.rerun()
                    else:
                        if st.button("✅ ACTIVAR", use_container_width=True, key="btn_activar"):
                            usuarios_dict[usuario_a_gestionar]['activo'] = True
                            guardar_usuarios_registrados(usuarios_dict)
                            st.success(f"Usuario {usuario_data['nombre']} activado")
                            st.rerun()
        
        with tab_registros:
            usuarios_activos = obtener_todos_usuarios()
            
            if not usuarios_activos:
                st.warning("No hay usuarios activos")
            else:
                usuario_seleccionado = st.selectbox("Selecciona usuario", usuarios_activos)
                df = cargar_datos_usuario(usuario_seleccionado)
                
                if df.empty:
                    st.info(f"No hay registros para {usuario_seleccionado}")
                else:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📋 Jornadas", len(df))
                    with col2:
                        st.metric("⏱️ Total Horas", formato_horas(df['Horas'].sum()))
                    with col3:
                        st.metric("📊 Promedio", formato_horas(df['Horas'].mean()))
                    with col4:
                        st.metric("👤 Usuario", usuario_seleccionado)
                    
                    st.divider()
                    
                    editar = st.checkbox("✏️ Editar datos")
                    
                    if editar:
                        for idx in range(len(df)):
                            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                            with col1:
                                fecha = st.date_input("Fecha", value=df.loc[idx, 'Fecha'].date(), key=f"admin_f_{idx}", label_visibility="collapsed")
                                df.loc[idx, 'Fecha'] = pd.Timestamp(fecha)
                            with col2:
                                entrada = st.time_input("Entrada", value=pd.to_datetime(df.loc[idx, 'Entrada'], format='%H:%M').time(), key=f"admin_e_{idx}", label_visibility="collapsed")
                                df.loc[idx, 'Entrada'] = entrada.strftime("%H:%M")
                            with col3:
                                salida = st.time_input("Salida", value=pd.to_datetime(df.loc[idx, 'Salida'], format='%H:%M').time(), key=f"admin_s_{idx}", label_visibility="collapsed")
                                df.loc[idx, 'Salida'] = salida.strftime("%H:%M")
                            with col4:
                                dt_e = pd.to_datetime(df.loc[idx, 'Entrada'], format='%H:%M').time()
                                dt_s = pd.to_datetime(df.loc[idx, 'Salida'], format='%H:%M').time()
                                dt_entrada = datetime.combine(datetime.today(), dt_e)
                                dt_salida = datetime.combine(datetime.today(), dt_s)
                                if dt_salida < dt_entrada:
                                    dt_salida += timedelta(days=1)
                                horas = round((dt_salida - dt_entrada).total_seconds() / 3600, 2)
                                st.metric("H", formato_horas(horas), label_visibility="collapsed")
                                df.loc[idx, 'Horas'] = horas
                            with col5:
                                if st.button("🗑️", key=f"admin_d_{idx}"):
                                    df = df.drop(idx).reset_index(drop=True)
                                    guardar_datos_usuario(usuario_seleccionado, df)
                                    st.rerun()
                        
                        if st.button("💾 Guardar cambios", use_container_width=True):
                            guardar_datos_usuario(usuario_seleccionado, df)
                            st.success("✅ Cambios guardados")
                    else:
                        tabla = df.copy()
                        tabla['Fecha'] = tabla['Fecha'].dt.strftime('%Y-%m-%d')
                        tabla['Horas'] = tabla['Horas'].apply(formato_horas)
                        st.dataframe(tabla, use_container_width=True, hide_index=True)
                    
                    st.divider()
                    col1, col2 = st.columns(2)
                    with col1:
                        mes = st.selectbox("Mes", range(1, 13), format_func=lambda x: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"][x-1])
                    with col2:
                        año = st.number_input("Año", value=datetime.today().year, min_value=2020)
                    
                    df_mes = df[(df['Fecha'].dt.month == mes) & (df['Fecha'].dt.year == año)]
                    
                    if not df_mes.empty:
                        excel_data = crear_excel(df_mes)
                        st.download_button(
                            label=f"📥 Descargar Excel - {usuario_seleccionado}",
                            data=excel_data,
                            file_name=f"jornada_{usuario_seleccionado}_{año}-{mes:02d}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
    
    else:
        # ============= INTERFAZ USUARIO NORMAL =============
        df = cargar_datos_usuario(st.session_state.usuario_logeado)
        
        tab1, tab2, tab3 = st.tabs(["⏱️ Cronómetro", "📝 Manual", "📊 Historial"])
        
        with tab1:
            st.markdown("## ⏱️ Cronómetro de Jornada")
            
            fecha_crono = st.date_input("Fecha", value=datetime.today().date(), key="fecha_crono")
            st.divider()
            
            tiempo_transcurrido = 0
            if st.session_state.cronometro_activo and st.session_state.tiempo_inicio:
                tiempo_transcurrido = (datetime.now() - st.session_state.tiempo_inicio).total_seconds() + st.session_state.tiempo_pausado
            elif st.session_state.tiempo_pausado > 0:
                tiempo_transcurrido = st.session_state.tiempo_pausado
            
            st.markdown(f"<div class='cronometro'>{formato_cronometro(tiempo_transcurrido)}</div>", unsafe_allow_html=True)
            st.divider()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("▶️ INICIAR", use_container_width=True, type="primary", key="btn_iniciar"):
                    if not st.session_state.cronometro_activo:
                        st.session_state.cronometro_activo = True
                        if st.session_state.tiempo_pausado == 0:
                            st.session_state.tiempo_inicio = datetime.now()
                        else:
                            st.session_state.tiempo_inicio = datetime.now() - timedelta(seconds=st.session_state.tiempo_pausado)
                        st.rerun()
            with col2:
                if st.button("⏸️ PAUSAR", use_container_width=True, disabled=not st.session_state.cronometro_activo, key="btn_pausar"):
                    if st.session_state.cronometro_activo and st.session_state.tiempo_inicio:
                        st.session_state.tiempo_pausado = (datetime.now() - st.session_state.tiempo_inicio).total_seconds()
                        st.session_state.cronometro_activo = False
                        st.session_state.tiempo_inicio = None
                        st.rerun()
            with col3:
                if st.button("🔄 REINICIAR", use_container_width=True, key="btn_reiniciar"):
                    st.session_state.cronometro_activo = False
                    st.session_state.tiempo_inicio = None
                    st.session_state.tiempo_pausado = 0
                    st.rerun()
            
            st.divider()
            
            if st.button("✅ REGISTRAR JORNADA", use_container_width=True, type="primary", key="btn_registrar"):
                if st.session_state.tiempo_pausado > 0 or tiempo_transcurrido > 0:
                    horas_totales = (st.session_state.tiempo_pausado + tiempo_transcurrido) / 3600
                    ahora = datetime.now()
                    segundos_totales = st.session_state.tiempo_pausado + tiempo_transcurrido
                    entrada_est = (ahora - timedelta(seconds=segundos_totales)).time()
                    salida_est = ahora.time()
                    
                    nueva_fila = pd.DataFrame({
                        'Fecha': [pd.Timestamp(fecha_crono)],
                        'Entrada': [entrada_est.strftime("%H:%M")],
                        'Salida': [salida_est.strftime("%H:%M")],
                        'Horas': [round(horas_totales, 2)]
                    })
                    
                    df = pd.concat([df, nueva_fila], ignore_index=True).sort_values('Fecha').reset_index(drop=True)
                    guardar_datos_usuario(st.session_state.usuario_logeado, df)
                    
                    st.session_state.cronometro_activo = False
                    st.session_state.tiempo_inicio = None
                    st.session_state.tiempo_pausado = 0
                    
                    st.success(f"✅ ¡Jornada registrada! {formato_horas(horas_totales)}")
                    st.rerun()
                else:
                    st.warning("Inicia el cronómetro primero")
            
            # Auto-refresh cuando el cronómetro está activo
            # IMPORTANTE: Va al final para que los botones funcionen correctamente
            if st.session_state.cronometro_activo:
                import time
                time.sleep(0.2)  # Actualizar cada 200ms
                st.rerun()
        
        with tab2:
            st.markdown("## 📝 Registrar Manualmente")
            col1, col2, col3 = st.columns(3)
            with col1:
                fecha = st.date_input("Fecha", value=datetime.today().date(), key="fecha_manual")
            with col2:
                entrada = st.time_input("Entrada", value=datetime.strptime("09:00", "%H:%M").time())
            with col3:
                salida = st.time_input("Salida", value=datetime.strptime("18:00", "%H:%M").time())
            
            if entrada and salida:
                dt_entrada = datetime.combine(datetime.today(), entrada)
                dt_salida = datetime.combine(datetime.today(), salida)
                if dt_salida < dt_entrada:
                    dt_salida += timedelta(days=1)
                diff = dt_salida - dt_entrada
                horas_calc = round(diff.total_seconds() / 3600, 2)
                st.success(f"⏱️ **Horas: {formato_horas(horas_calc)}**")
            else:
                horas_calc = 0
            
            if st.button("✅ REGISTRAR", type="primary", use_container_width=True, key="btn_registrar_manual"):
                nueva_fila = pd.DataFrame({
                    'Fecha': [pd.Timestamp(fecha)],
                    'Entrada': [entrada.strftime("%H:%M")],
                    'Salida': [salida.strftime("%H:%M")],
                    'Horas': [horas_calc]
                })
                df = pd.concat([df, nueva_fila], ignore_index=True).sort_values('Fecha').reset_index(drop=True)
                guardar_datos_usuario(st.session_state.usuario_logeado, df)
                st.success("✅ ¡Jornada registrada!")
                st.rerun()
        
        with tab3:
            st.markdown("## 📊 Mi Historial")
            
            if df.empty:
                st.warning("No hay registros aún")
            else:
                col1, col2, col3 = st.columns(3)
                with col1:
                    fecha_desde = st.date_input("Desde", value=datetime.today().date() - timedelta(days=30), key="desde")
                with col2:
                    fecha_hasta = st.date_input("Hasta", value=datetime.today().date(), key="hasta")
                with col3:
                    editar = st.checkbox("✏️ Editar")
                
                df_filtrado = df[(df['Fecha'].dt.date >= fecha_desde) & (df['Fecha'].dt.date <= fecha_hasta)].reset_index(drop=True)
                
                if df_filtrado.empty:
                    st.info("No hay registros en este período")
                else:
                    if editar:
                        for idx in range(len(df_filtrado)):
                            df_real_idx = df[df['Fecha'] == df_filtrado.iloc[idx]['Fecha']].index[0]
                            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                            with col1:
                                fecha_edit = st.date_input("Fecha", value=df.loc[df_real_idx, 'Fecha'].date(), key=f"f_{idx}", label_visibility="collapsed")
                                df.loc[df_real_idx, 'Fecha'] = pd.Timestamp(fecha_edit)
                            with col2:
                                entrada_edit = st.time_input("Entrada", value=pd.to_datetime(df.loc[df_real_idx, 'Entrada'], format='%H:%M').time(), key=f"e_{idx}", label_visibility="collapsed")
                                df.loc[df_real_idx, 'Entrada'] = entrada_edit.strftime("%H:%M")
                            with col3:
                                salida_edit = st.time_input("Salida", value=pd.to_datetime(df.loc[df_real_idx, 'Salida'], format='%H:%M').time(), key=f"s_{idx}", label_visibility="collapsed")
                                df.loc[df_real_idx, 'Salida'] = salida_edit.strftime("%H:%M")
                            with col4:
                                dt_e = pd.to_datetime(df.loc[df_real_idx, 'Entrada'], format='%H:%M').time()
                                dt_s = pd.to_datetime(df.loc[df_real_idx, 'Salida'], format='%H:%M').time()
                                dt_entrada = datetime.combine(datetime.today(), dt_e)
                                dt_salida = datetime.combine(datetime.today(), dt_s)
                                if dt_salida < dt_entrada:
                                    dt_salida += timedelta(days=1)
                                horas = round((dt_salida - dt_entrada).total_seconds() / 3600, 2)
                                st.metric("H", formato_horas(horas), label_visibility="collapsed")
                                df.loc[df_real_idx, 'Horas'] = horas
                            with col5:
                                if st.button("🗑️", key=f"d_{idx}"):
                                    df = df.drop(df_real_idx).reset_index(drop=True)
                                    guardar_datos_usuario(st.session_state.usuario_logeado, df)
                                    st.rerun()
                    else:
                        tabla = df_filtrado.copy()
                        tabla['Fecha'] = tabla['Fecha'].dt.strftime('%Y-%m-%d')
                        tabla['Horas'] = tabla['Horas'].apply(formato_horas)
                        st.dataframe(tabla, use_container_width=True, hide_index=True)
                    
                    st.divider()
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📋 Jornadas", len(df_filtrado))
                    with col2:
                        st.metric("⏱️ Total", formato_horas(df_filtrado['Horas'].sum()))
                    with col3:
                        st.metric("📊 Promedio", formato_horas(df_filtrado['Horas'].mean()))
                    with col4:
                        st.metric("📅 Días", (fecha_hasta - fecha_desde).days + 1)
                    
                    st.divider()
                    col1, col2 = st.columns(2)
                    with col1:
                        mes = st.selectbox("Mes", range(1, 13), format_func=lambda x: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"][x-1])
                    with col2:
                        año = st.number_input("Año", value=datetime.today().year, min_value=2020)
                    
                    df_mes = df[(df['Fecha'].dt.month == mes) & (df['Fecha'].dt.year == año)]
                    
                    if not df_mes.empty:
                        excel_data = crear_excel(df_mes)
                        st.download_button(
                            label="📥 Descargar Excel",
                            data=excel_data,
                            file_name=f"jornada_{año}-{mes:02d}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )

st.divider()
st.markdown("""
<div class="footer-corporate">
    <p style="font-size: 1.2em; margin-bottom: 10px;">🐾 <strong>TopRedesValencia</strong></p>
    <p style="margin: 5px 0;">Redes de seguridad para gatos y niños</p>
    <p style="margin: 10px 0;">
        📱 <strong><a href="tel:+34683597759">683 597 759</a></strong> • 
        🌐 <strong><a href="https://topredesvalencia.com" target="_blank">www.topredesvalencia.com</a></strong>
    </p>
    <p style="font-size: 0.9em; margin-top: 15px; opacity: 0.9;">
        Serving Valencia, Castellón & Alicante with TIAKI brand safety nets
    </p>
</div>
""", unsafe_allow_html=True)
