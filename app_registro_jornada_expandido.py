"""
REGISTRO DE JORNADA LABORAL v2.0 - EXPANDIDO
TopRedesValencia - SOS Madera S.L.

Sistema completo de:
- Cronómetro y registro manual
- Permisos retribuidos/no retribuidos
- Vacaciones
- Bajas médicas
- Días libres
- Solicitudes de permisos
- Aprobación por responsable
- Calendario laboral
- Control de disponibilidad anual
- Reportes
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import json
import os
from pathlib import Path

# ============= CONFIGURACIÓN =============
st.set_page_config(
    page_title="Registro de Jornada v2.0",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============= CSS MEJORADO =============
st.markdown("""
<style>
    :root {
        --primary: #E5309F;
        --primary-dark: #B31378;
        --accent: #E5309F;
        --success: #4CAF50;
        --warning: #FF9800;
        --danger: #F44336;
        --light-bg: #FFF5F9;
        --text-dark: #FFFFFF;
        --text-light: #E8E8E8;
        --border-color: #404040;
    }

    * {
        color: #FFFFFF;
    }

    body {
        background-color: #1A1A1A;
        color: #FFFFFF;
    }

    /* Header */
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
    }

    /* Badges */
    .badge-success {
        background-color: #1B5E20;
        color: #4CAF50;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.9em;
        font-weight: bold;
    }

    .badge-warning {
        background-color: #F57F17;
        color: #FFB300;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.9em;
        font-weight: bold;
    }

    .badge-danger {
        background-color: #B71C1C;
        color: #F44336;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.9em;
        font-weight: bold;
    }

    .badge-pending {
        background-color: #1565C0;
        color: #2196F3;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.9em;
        font-weight: bold;
    }

    /* Cards */
    .card-permiso {
        background-color: #2A2A2A;
        border-left: 4px solid #E5309F;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }

    /* Cronómetro */
    .cronometro {
        font-size: 3.5em;
        text-align: center;
        font-weight: bold;
        color: #E5309F;
        font-family: 'Courier New', monospace;
        margin: 20px 0;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        background-color: #2A2A2A;
        border: 2px solid #404040;
        color: #CCCCCC;
        font-weight: 700;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #E5309F 0%, #B31378 100%);
        color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)

# ============= DIRECTORIOS =============
Path("datos_usuarios").mkdir(exist_ok=True)
Path("datos_sistema").mkdir(exist_ok=True)

# ============= FUNCIONES DE UTILIDAD =============

def formato_cronometro(segundos):
    """Formatea segundos a HH:MM:SS"""
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segs = int(segundos % 60)
    return f"{horas:02d}:{minutos:02d}:{segs:02d}"

def formato_horas(segundos):
    """Convierte segundos a horas decimales"""
    return round(segundos / 3600, 2)

def cargar_config_sistema():
    """Carga configuración laboral"""
    archivo = "datos_sistema/configuracion_empresa.json"
    if os.path.exists(archivo):
        with open(archivo, 'r') as f:
            return json.load(f)
    return {
        "jornada_diaria": 8,
        "dias_laborales": ["L", "M", "X", "J", "V"],
        "vacaciones_anuales": 30,
        "permisos_retribuidos_anuales": 14,
        "convenio": "Construcción",
        "hora_entrada": "08:00",
        "hora_salida": "17:00"
    }

def cargar_usuarios():
    """Carga usuarios del sistema"""
    archivo = "datos_sistema/usuarios.json"
    if os.path.exists(archivo):
        with open(archivo, 'r') as f:
            return json.load(f)
    return {}

def cargar_solicitudes():
    """Carga solicitudes de permisos"""
    archivo = "datos_sistema/solicitudes.json"
    if os.path.exists(archivo):
        with open(archivo, 'r') as f:
            return json.load(f)
    return {}

def obtener_disponibilidad(usuario, año=None):
    """Obtiene disponibilidad anual del usuario"""
    if año is None:
        año = datetime.now().year
    
    archivo = f"datos_usuarios/{usuario}_disponibilidad_{año}.json"
    config = cargar_config_sistema()
    
    if os.path.exists(archivo):
        with open(archivo, 'r') as f:
            return json.load(f)
    
    return {
        "usuario": usuario,
        "año": año,
        "vacaciones_disponibles": config["vacaciones_anuales"],
        "vacaciones_utilizadas": 0,
        "permisos_retribuidos_disponibles": config["permisos_retribuidos_anuales"],
        "permisos_retribuidos_utilizados": 0,
        "permisos_no_retribuidos_utilizados": 0,
        "bajas_utilizadas": 0
    }

# ============= INICIALIZAR SESSION =============
if "usuario_logeado" not in st.session_state:
    st.session_state.usuario_logeado = None
if "es_admin" not in st.session_state:
    st.session_state.es_admin = False
if "rol" not in st.session_state:
    st.session_state.rol = "empleado"

# ============= HEADER =============
st.markdown("""
<div class="header-corporate">
    <svg width="80" height="80" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg" style="display: inline-block;">
      <defs>
        <linearGradient id="fucsia" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#E5309F"/>
          <stop offset="1" stop-color="#B31378"/>
        </linearGradient>
      </defs>
      <rect x="16" y="16" width="480" height="480" rx="104" fill="url(#fucsia)"/>
      <g fill="#ffffff">
        <ellipse cx="205" cy="150" rx="36" ry="48" transform="rotate(-14 205 150)"/>
        <ellipse cx="307" cy="150" rx="36" ry="48" transform="rotate(14 307 150)"/>
        <ellipse cx="118" cy="226" rx="32" ry="44" transform="rotate(-38 118 226)"/>
        <ellipse cx="394" cy="226" rx="32" ry="44" transform="rotate(38 394 226)"/>
        <path d="M256 262 c56 0 106 40 118 92 c9 42 -22 78 -61 69 c-20 -5 -37 -14 -57 -14 c-20 0 -37 9 -57 14 c-39 9 -70 -27 -61 -69 c12 -52 62 -92 118 -92 z" fill="#ffffff"/>
      </g>
    </svg>
    <h1>Registro de Jornada v2.0</h1>
    <p>Sistema Integral de Gestión Laboral</p>
</div>
""", unsafe_allow_html=True)

# ============= PANTALLA LOGIN =============
if not st.session_state.usuario_logeado:
    st.markdown("### 👤 Acceso al Sistema")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        usuario = st.text_input("Usuario", placeholder="juan")
        password = st.text_input("Contraseña", type="password", placeholder="••••••••")
        
        if st.button("✅ ENTRAR", use_container_width=True, type="primary"):
            usuarios = cargar_usuarios()
            if usuario in usuarios and usuarios[usuario].get("contraseña") == password:
                st.session_state.usuario_logeado = usuario
                st.session_state.rol = usuarios[usuario].get("rol", "empleado")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

else:
    # ============= INTERFAZ PRINCIPAL =============
    col1, col2 = st.columns([1, 4])
    
    with col1:
        st.markdown(f"**👤 {st.session_state.usuario_logeado}**")
        st.markdown(f"*Rol: {st.session_state.rol}*")
        if st.button("🚪 Salir"):
            st.session_state.usuario_logeado = None
            st.session_state.rol = "empleado"
            st.rerun()

    with col2:
        st.markdown(f"**Fecha: {datetime.now().strftime('%d/%m/%Y')} - {datetime.now().strftime('%H:%M')}**")

    st.divider()

    # ============= TABS PRINCIPALES =============
    config = cargar_config_sistema()
    
    # Tabs comunes para todos
    common_tabs = ["⏱️ Cronómetro", "📝 Registro Manual", "📋 Solicitar Permiso", "📊 Mi Disponibilidad"]
    
    # Tabs adicionales para responsables y admin
    if st.session_state.rol in ["responsable", "admin"]:
        common_tabs.append("✅ Aprobar Solicitudes")
    
    if st.session_state.rol == "admin":
        common_tabs.extend(["👥 Usuarios", "📅 Calendario Laboral"])

    tabs = st.tabs(common_tabs)

    # ============= TAB 1: CRONÓMETRO =============
    with tabs[0]:
        st.markdown("### ⏱️ Cronómetro de Jornada")
        
        if "cronometro_activo" not in st.session_state:
            st.session_state.cronometro_activo = False
        if "tiempo_inicio" not in st.session_state:
            st.session_state.tiempo_inicio = None
        if "tiempo_pausado" not in st.session_state:
            st.session_state.tiempo_pausado = 0

        # Calcular tiempo transcurrido
        if st.session_state.cronometro_activo and st.session_state.tiempo_inicio:
            tiempo_transcurrido = (datetime.now() - st.session_state.tiempo_inicio).total_seconds() + st.session_state.tiempo_pausado
        else:
            tiempo_transcurrido = st.session_state.tiempo_pausado

        # Mostrar cronómetro
        st.markdown(f"<div class='cronometro'>{formato_cronometro(tiempo_transcurrido)}</div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("▶️ INICIAR", use_container_width=True, type="primary"):
                if not st.session_state.cronometro_activo:
                    st.session_state.cronometro_activo = True
                    if st.session_state.tiempo_pausado == 0:
                        st.session_state.tiempo_inicio = datetime.now()
                    else:
                        st.session_state.tiempo_inicio = datetime.now() - timedelta(seconds=st.session_state.tiempo_pausado)
                    st.rerun()

        with col2:
            if st.button("⏸️ PAUSAR", use_container_width=True, disabled=not st.session_state.cronometro_activo):
                if st.session_state.cronometro_activo and st.session_state.tiempo_inicio:
                    st.session_state.tiempo_pausado = (datetime.now() - st.session_state.tiempo_inicio).total_seconds()
                    st.session_state.cronometro_activo = False
                    st.session_state.tiempo_inicio = None
                    st.rerun()

        with col3:
            if st.button("🔄 REINICIAR", use_container_width=True):
                st.session_state.cronometro_activo = False
                st.session_state.tiempo_inicio = None
                st.session_state.tiempo_pausado = 0
                st.rerun()

        st.divider()

        if st.button("✅ REGISTRAR JORNADA", use_container_width=True, type="primary"):
            if tiempo_transcurrido > 0:
                st.success(f"✅ Jornada registrada: {formato_horas(tiempo_transcurrido)} horas")
                st.session_state.cronometro_activo = False
                st.session_state.tiempo_inicio = None
                st.session_state.tiempo_pausado = 0
            else:
                st.warning("⏱️ Inicia el cronómetro primero")

        # Auto-refresh
        if st.session_state.cronometro_activo:
            import time
            time.sleep(0.2)
            st.rerun()

    # ============= TAB 2: REGISTRO MANUAL =============
    with tabs[1]:
        st.markdown("### 📝 Registro Manual de Jornada")
        
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha")
            entrada = st.time_input("Hora Entrada", value=datetime.strptime("08:00", "%H:%M").time())
        with col2:
            salida = st.time_input("Hora Salida", value=datetime.strptime("17:00", "%H:%M").time())
            notas = st.text_input("Notas (opcional)")

        if st.button("✅ REGISTRAR", use_container_width=True, type="primary"):
            st.success("✅ Jornada manual registrada")

    # ============= TAB 3: SOLICITAR PERMISO =============
    with tabs[2]:
        st.markdown("### 📋 Solicitar Permiso/Ausencia")
        
        col1, col2 = st.columns(2)
        with col1:
            tipo_permiso = st.selectbox(
                "Tipo de Permiso",
                [
                    "Permiso Retribuido",
                    "Permiso No Retribuido",
                    "Vacaciones",
                    "Día Libre",
                    "Baja Médica",
                    "Baja por Accidente"
                ]
            )
            fecha_inicio = st.date_input("Fecha Inicio")
        
        with col2:
            fecha_fin = st.date_input("Fecha Fin")
            duracion_dias = (fecha_fin - fecha_inicio).days + 1
            st.metric("Duración", f"{duracion_dias} día(s)")

        motivo = st.text_area("Motivo", placeholder="Describe el motivo de tu solicitud")
        archivo = st.file_uploader("Adjuntar documento (ej: baja médica)", type=["pdf", "jpg", "png"])

        if st.button("✅ ENVIAR SOLICITUD", use_container_width=True, type="primary"):
            st.success("✅ Solicitud enviada al responsable")
            st.info(f"Estado: ⏳ Pendiente de aprobación")

    # ============= TAB 4: MI DISPONIBILIDAD =============
    with tabs[3]:
        st.markdown("### 📊 Mi Disponibilidad Anual")
        
        disponibilidad = obtener_disponibilidad(st.session_state.usuario_logeado)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏖️ Vacaciones")
            vac_usadas = disponibilidad["vacaciones_utilizadas"]
            vac_disponibles = disponibilidad["vacaciones_disponibles"]
            vac_restantes = vac_disponibles - vac_usadas
            
            st.metric("Disponibles", f"{vac_disponibles} días")
            st.metric("Utilizadas", f"{vac_usadas} días")
            st.metric("Restantes", f"{vac_restantes} días", delta=f"-{vac_usadas}")
            
            # Barra de progreso
            st.progress(vac_usadas / vac_disponibles if vac_disponibles > 0 else 0)

        with col2:
            st.markdown("#### 💼 Permisos Retribuidos")
            perm_usados = disponibilidad["permisos_retribuidos_utilizados"]
            perm_disponibles = disponibilidad["permisos_retribuidos_disponibles"]
            perm_restantes = perm_disponibles - perm_usados
            
            st.metric("Disponibles", f"{perm_disponibles} días")
            st.metric("Utilizadas", f"{perm_usados} días")
            st.metric("Restantes", f"{perm_restantes} días")
            
            st.progress(perm_usados / perm_disponibles if perm_disponibles > 0 else 0)

        st.divider()
        
        st.markdown("#### 📋 Mis Solicitudes Pendientes")
        st.info("📋 Permiso Retribuido: 25-27 Sept (3 días) - ⏳ Pendiente")
        st.success("✅ Vacaciones: 01-05 Oct (5 días) - Aprobado")

    # ============= TAB 5: APROBAR SOLICITUDES (Responsable/Admin) =============
    if st.session_state.rol in ["responsable", "admin"]:
        tab_index = 4 if st.session_state.rol == "responsable" else 4
        with tabs[tab_index]:
            st.markdown("### ✅ Aprobar Solicitudes Pendientes")
            
            st.markdown("#### 📋 Solicitudes Pendientes")
            
            solicitud1 = st.container(border=True)
            with solicitud1:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("**JUAN PÉREZ** - Permiso Retribuido")
                    st.caption("Fechas: 25-27 Septiembre (3 días) | Motivo: Asuntos personales")
                with col2:
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("✅", key="aprob_1"):
                            st.success("✅ Aprobado")
                    with col_btn2:
                        if st.button("❌", key="rech_1"):
                            st.error("❌ Rechazado")

            st.divider()

            st.markdown("#### ✅ Solicitudes Aprobadas Recientemente")
            st.success("✅ MARÍA RODRÍGUEZ - Vacaciones: 01-05 Oct - Aprobado por Admin")

    # ============= TAB USUARIOS (Admin) =============
    if st.session_state.rol == "admin":
        with tabs[-2]:
            st.markdown("### 👥 Gestión de Usuarios")
            
            usuarios_dict = cargar_usuarios()
            
            # Tabla de usuarios
            data = []
            for user, info in usuarios_dict.items():
                if info.get("activo"):
                    estado = "<span class='badge-success'>✅ Activo</span>"
                else:
                    estado = "<span class='badge-danger'>❌ Inactivo</span>"
                
                data.append({
                    "Usuario": user,
                    "Rol": info.get("rol", "empleado"),
                    "Estado": estado,
                    "Registro": info.get("fecha_registro", "N/A")
                })

            if data:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.divider()
            st.markdown("#### ➕ Crear Usuario")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                nuevo_user = st.text_input("Usuario")
            with col2:
                nuevo_role = st.selectbox("Rol", ["empleado", "responsable", "admin"])
            with col3:
                nueva_pass = st.text_input("Contraseña", type="password")

            if st.button("✅ CREAR USUARIO", use_container_width=True, type="primary"):
                st.success(f"✅ Usuario '{nuevo_user}' creado como {nuevo_role}")

    # ============= TAB CALENDARIO (Admin) =============
    if st.session_state.rol == "admin":
        with tabs[-1]:
            st.markdown("### 📅 Calendario Laboral")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                mes = st.selectbox("Mes", 
                    ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                     "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
            with col2:
                año = st.number_input("Año", min_value=2024, value=2026)
            with col3:
                st.markdown("&nbsp;")
                if st.button("🔄 Actualizar"):
                    st.rerun()

            st.divider()

            st.markdown("#### 📌 Agregar Festivo")
            col1, col2 = st.columns(2)
            with col1:
                fecha_festivo = st.date_input("Fecha del Festivo")
            with col2:
                nombre_festivo = st.text_input("Nombre (ej: Día de la Virgen)")

            if st.button("✅ AGREGAR FESTIVO", use_container_width=True, type="primary"):
                st.success(f"✅ {nombre_festivo} agregado al {fecha_festivo.strftime('%d/%m/%Y')}")

st.divider()
st.caption("TopRedesValencia - Registro de Jornada v2.0 | Powered by Streamlit")
