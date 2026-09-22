"""
REGISTRO DE JORNADA LABORAL - TopRedesValencia
Versión limpia y funcional
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import json
from pathlib import Path

# ============= CONFIG =============
st.set_page_config(page_title="Registro de Jornada", page_icon="🐾", layout="wide")

# Crear carpetas
Path("datos_usuarios").mkdir(exist_ok=True)
Path("datos_sistema").mkdir(exist_ok=True)

# ============= FUNCIONES =============

def cargar_usuarios():
    archivo = "datos_sistema/usuarios.json"
    if os.path.exists(archivo):
        with open(archivo, 'r') as f:
            return json.load(f)
    return {"admin": {"contraseña": "admin123", "activo": True, "fecha_registro": "2024-01-01"}}

def guardar_usuarios(usuarios):
    with open("datos_sistema/usuarios.json", 'w') as f:
        json.dump(usuarios, f, indent=2)

def cargar_datos_usuario(usuario):
    archivo = f"datos_usuarios/{usuario}.csv"
    if os.path.exists(archivo):
        return pd.read_csv(archivo)
    return pd.DataFrame(columns=['Fecha', 'Entrada', 'Salida', 'Horas'])

def guardar_datos_usuario(usuario, df):
    df.to_csv(f"datos_usuarios/{usuario}.csv", index=False)

def formato_cronometro(segundos):
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = int(segundos % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

# ============= INICIALIZAR =============
if "usuario_logeado" not in st.session_state:
    st.session_state.usuario_logeado = None
if "es_admin" not in st.session_state:
    st.session_state.es_admin = False
if "cronometro_activo" not in st.session_state:
    st.session_state.cronometro_activo = False
if "tiempo_inicio" not in st.session_state:
    st.session_state.tiempo_inicio = None
if "tiempo_pausado" not in st.session_state:
    st.session_state.tiempo_pausado = 0

# ============= HEADER =============
st.markdown("<h1 style='text-align: center; color: #E5309F;'>🐾 Registro de Jornada</h1>", unsafe_allow_html=True)

# ============= LOGIN =============
if not st.session_state.usuario_logeado:
    st.divider()
    
    tab_login, tab_registro = st.tabs(["🔓 INICIAR SESIÓN", "📝 CREAR CUENTA"])
    
    with tab_login:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 👤 Usuario")
            usuario = st.text_input("Nombre", placeholder="juan")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            
            if st.button("✅ ENTRAR", type="primary", use_container_width=True):
                usuarios = cargar_usuarios()
                if usuario in usuarios and usuarios[usuario]["contraseña"] == password:
                    st.session_state.usuario_logeado = usuario
                    st.session_state.es_admin = False
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
            
            st.divider()
            
            st.markdown("### 🔐 Acceso Admin")
            admin_pass = st.text_input("Contraseña admin", type="password", placeholder="••••••••")
            
            if st.button("🔓 ENTRAR COMO ADMIN", type="primary", use_container_width=True):
                if admin_pass == "admin123":
                    st.session_state.usuario_logeado = "ADMIN"
                    st.session_state.es_admin = True
                    st.rerun()
                else:
                    st.error("❌ Contraseña admin incorrecta")
    
    with tab_registro:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 📝 Crear Cuenta")
            nuevo_user = st.text_input("Nombre de usuario", placeholder="juan")
            nueva_pass = st.text_input("Contraseña", type="password", placeholder="••••••••")
            nueva_pass_conf = st.text_input("Confirmar contraseña", type="password", placeholder="••••••••")
            
            if st.button("✅ CREAR CUENTA", type="primary", use_container_width=True):
                usuarios = cargar_usuarios()
                if nuevo_user in usuarios:
                    st.error("❌ El usuario ya existe")
                elif nueva_pass != nueva_pass_conf:
                    st.error("❌ Las contraseñas no coinciden")
                elif len(nueva_pass) < 4:
                    st.error("❌ Contraseña muy corta (mínimo 4 caracteres)")
                else:
                    usuarios[nuevo_user] = {
                        "contraseña": nueva_pass,
                        "activo": True,
                        "fecha_registro": datetime.now().strftime("%Y-%m-%d")
                    }
                    guardar_usuarios(usuarios)
                    st.success("✅ Cuenta creada. Ahora inicia sesión.")

# ============= PANEL PRINCIPAL =============
else:
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"**{st.session_state.usuario_logeado}**")
        if st.button("🚪 Salir"):
            st.session_state.usuario_logeado = None
            st.session_state.es_admin = False
            st.rerun()
    with col2:
        st.markdown(f"**{datetime.now().strftime('%d/%m/%Y %H:%M')}**")
    
    st.divider()
    
    # ADMIN
    if st.session_state.es_admin:
        tab_usuarios, tab_registros = st.tabs(["👥 Gestión de Usuarios", "📊 Ver Registros"])
        
        with tab_usuarios:
            st.markdown("### 👥 Usuarios Registrados")
            
            usuarios = cargar_usuarios()
            
            # Tabla
            data = []
            for user, info in usuarios.items():
                estado = "✅ Activo" if info.get("activo") else "❌ Inactivo"
                data.append({
                    "Usuario": user,
                    "Estado": estado,
                    "Registro": info.get("fecha_registro", "N/A")
                })
            
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.divider()
            
            st.markdown("### ➕ Crear Nuevo Usuario")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                nuevo_user = st.text_input("Usuario", placeholder="juan")
            with col2:
                nueva_pass = st.text_input("Contraseña", type="password", placeholder="••••••••")
            with col3:
                st.write("")
                if st.button("✅ CREAR", type="primary", use_container_width=True):
                    if nuevo_user and nueva_pass:
                        if nuevo_user in usuarios:
                            st.error("❌ El usuario ya existe")
                        else:
                            usuarios[nuevo_user] = {
                                "contraseña": nueva_pass,
                                "activo": True,
                                "fecha_registro": datetime.now().strftime("%Y-%m-%d")
                            }
                            guardar_usuarios(usuarios)
                            st.success(f"✅ Usuario '{nuevo_user}' creado")
                            st.rerun()
                    else:
                        st.error("⚠️ Completa todos los campos")
        
        with tab_registros:
            st.markdown("### 📊 Registros de Todos los Usuarios")
            
            usuarios = cargar_usuarios()
            usuario_sel = st.selectbox("Selecciona usuario", [u for u in usuarios.keys() if u != "ADMIN"])
            
            if usuario_sel:
                df = cargar_datos_usuario(usuario_sel)
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                    
                    # Descargar Excel
                    if st.button("📥 Descargar Excel"):
                        excel_file = f"{usuario_sel}_jornadas.xlsx"
                        df.to_excel(excel_file, index=False)
                        with open(excel_file, 'rb') as f:
                            st.download_button("Descargar", f, file_name=excel_file)
                else:
                    st.info(f"Sin jornadas registradas para {usuario_sel}")
    
    # USUARIO NORMAL
    else:
        tab1, tab2, tab3 = st.tabs(["⏱️ CRONÓMETRO", "📝 MANUAL", "📊 HISTORIAL"])
        
        with tab1:
            st.markdown("### ⏱️ Cronómetro de Jornada")
            
            # Calcular tiempo
            if st.session_state.cronometro_activo and st.session_state.tiempo_inicio:
                tiempo_total = (datetime.now() - st.session_state.tiempo_inicio).total_seconds() + st.session_state.tiempo_pausado
            else:
                tiempo_total = st.session_state.tiempo_pausado
            
            # Mostrar
            st.markdown(f"<h1 style='text-align: center; color: #E5309F; font-family: monospace;'>{formato_cronometro(tiempo_total)}</h1>", unsafe_allow_html=True)
            
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
                if tiempo_total > 0:
                    horas = round(tiempo_total / 3600, 2)
                    ahora = datetime.now()
                    entrada = (ahora - timedelta(seconds=tiempo_total)).time()
                    salida = ahora.time()
                    
                    df = cargar_datos_usuario(st.session_state.usuario_logeado)
                    nueva_fila = pd.DataFrame({
                        "Fecha": [ahora.strftime("%Y-%m-%d")],
                        "Entrada": [entrada.strftime("%H:%M")],
                        "Salida": [salida.strftime("%H:%M")],
                        "Horas": [horas]
                    })
                    df = pd.concat([df, nueva_fila], ignore_index=True)
                    guardar_datos_usuario(st.session_state.usuario_logeado, df)
                    
                    st.session_state.tiempo_pausado = 0
                    st.session_state.cronometro_activo = False
                    st.success(f"✅ ¡Registrado {horas} horas!")
                    st.rerun()
                else:
                    st.warning("⏱️ Inicia el cronómetro primero")
            
            # Auto-refresh
            if st.session_state.cronometro_activo:
                import time
                time.sleep(0.2)
                st.rerun()
        
        with tab2:
            st.markdown("### 📝 Registro Manual")
            
            col1, col2 = st.columns(2)
            with col1:
                fecha = st.date_input("Fecha")
                entrada = st.time_input("Entrada", value=datetime.strptime("08:00", "%H:%M").time())
            with col2:
                salida = st.time_input("Salida", value=datetime.strptime("17:00", "%H:%M").time())
                notas = st.text_input("Notas")
            
            if st.button("✅ REGISTRAR", use_container_width=True, type="primary"):
                entrada_dt = datetime.combine(fecha, entrada)
                salida_dt = datetime.combine(fecha, salida)
                horas = round((salida_dt - entrada_dt).total_seconds() / 3600, 2)
                
                df = cargar_datos_usuario(st.session_state.usuario_logeado)
                nueva_fila = pd.DataFrame({
                    "Fecha": [fecha.strftime("%Y-%m-%d")],
                    "Entrada": [entrada.strftime("%H:%M")],
                    "Salida": [salida.strftime("%H:%M")],
                    "Horas": [horas]
                })
                df = pd.concat([df, nueva_fila], ignore_index=True)
                guardar_datos_usuario(st.session_state.usuario_logeado, df)
                
                st.success("✅ Jornada registrada")
                st.rerun()
        
        with tab3:
            st.markdown("### 📊 Mi Historial")
            
            df = cargar_datos_usuario(st.session_state.usuario_logeado)
            
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                
                # Estadísticas
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Jornadas", len(df))
                col2.metric("Total Horas", round(df['Horas'].sum(), 2))
                col3.metric("Promedio Diario", round(df['Horas'].mean(), 2))
            else:
                st.info("Sin jornadas registradas aún")

st.divider()
st.caption("TopRedesValencia - Registro de Jornada | 🐾")
