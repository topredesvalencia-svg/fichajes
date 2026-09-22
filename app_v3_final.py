"""
REGISTRO DE JORNADA LABORAL - TopRedesValencia v3
VERSIÓN LIMPIA - SIN ERRORES DE IDs DUPLICADOS
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

# ============= SESSION STATE =============
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
st.markdown("<h1 style='text-align: center; color: #E5309F; margin-bottom: 10px;'>🐾 Registro de Jornada</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #999;'>TopRedesValencia - Sistema de Control de Jornada</p>", unsafe_allow_html=True)

# ============= LOGIN =============
if not st.session_state.usuario_logeado:
    st.divider()
    
    tab_login, tab_crear = st.tabs(["🔓 INICIAR SESIÓN", "📝 CREAR CUENTA"])
    
    # TAB LOGIN
    with tab_login:
        col_vacio, col_centro, col_vacio2 = st.columns([1, 2, 1])
        
        with col_centro:
            st.markdown("### 👤 Usuario")
            usuario_login = st.text_input(
                "Nombre", 
                placeholder="juan",
                key="login_usuario"
            )
            password_login = st.text_input(
                "Contraseña", 
                type="password", 
                placeholder="••••••••",
                key="login_pass"
            )
            
            if st.button("✅ ENTRAR", type="primary", use_container_width=True, key="btn_login"):
                usuarios = cargar_usuarios()
                if usuario_login in usuarios and usuarios[usuario_login]["contraseña"] == password_login:
                    st.session_state.usuario_logeado = usuario_login
                    st.session_state.es_admin = False
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
            
            st.divider()
            
            st.markdown("### 🔐 Acceso Admin")
            admin_password = st.text_input(
                "Contraseña admin", 
                type="password", 
                placeholder="••••••••",
                key="admin_pass_login"
            )
            
            if st.button("🔓 ENTRAR COMO ADMIN", type="primary", use_container_width=True, key="btn_admin_login"):
                if admin_password == "admin123":
                    st.session_state.usuario_logeado = "ADMIN"
                    st.session_state.es_admin = True
                    st.rerun()
                else:
                    st.error("❌ Contraseña admin incorrecta")
    
    # TAB CREAR CUENTA
    with tab_crear:
        col_vacio, col_centro, col_vacio2 = st.columns([1, 2, 1])
        
        with col_centro:
            st.markdown("### 📝 Crear Cuenta")
            nuevo_usuario = st.text_input(
                "Nombre de usuario", 
                placeholder="juan",
                key="crear_usuario"
            )
            nueva_password = st.text_input(
                "Contraseña", 
                type="password", 
                placeholder="••••••••",
                key="crear_pass1"
            )
            nueva_password_conf = st.text_input(
                "Confirmar contraseña", 
                type="password", 
                placeholder="••••••••",
                key="crear_pass2"
            )
            
            if st.button("✅ CREAR CUENTA", type="primary", use_container_width=True, key="btn_crear_cuenta"):
                usuarios = cargar_usuarios()
                if nuevo_usuario in usuarios:
                    st.error("❌ El usuario ya existe")
                elif nueva_password != nueva_password_conf:
                    st.error("❌ Las contraseñas no coinciden")
                elif len(nueva_password) < 4:
                    st.error("❌ Contraseña muy corta (mínimo 4 caracteres)")
                else:
                    usuarios[nuevo_usuario] = {
                        "contraseña": nueva_password,
                        "activo": True,
                        "fecha_registro": datetime.now().strftime("%Y-%m-%d")
                    }
                    guardar_usuarios(usuarios)
                    st.success("✅ Cuenta creada. Ahora inicia sesión.")

# ============= PANEL PRINCIPAL LOGEADO =============
else:
    # Header con usuario y hora
    col_user, col_spacer, col_hora = st.columns([1, 3, 1])
    with col_user:
        st.markdown(f"**👤 {st.session_state.usuario_logeado}**")
        if st.button("🚪 Salir", key="btn_salir"):
            st.session_state.usuario_logeado = None
            st.session_state.es_admin = False
            st.rerun()
    with col_hora:
        st.markdown(f"**{datetime.now().strftime('%d/%m/%Y %H:%M')}**")
    
    st.divider()
    
    # ============= PANEL ADMIN =============
    if st.session_state.es_admin:
        tab_usuarios, tab_registros = st.tabs(["👥 Gestión de Usuarios", "📊 Ver Registros"])
        
        with tab_usuarios:
            st.markdown("### 👥 Usuarios Registrados")
            
            usuarios = cargar_usuarios()
            
            # Mostrar tabla de usuarios
            if usuarios:
                data = []
                for user, info in usuarios.items():
                    estado = "✅ Activo" if info.get("activo") else "❌ Inactivo"
                    data.append({
                        "Usuario": user,
                        "Estado": estado,
                        "Fecha Registro": info.get("fecha_registro", "N/A")
                    })
                
                df_usuarios = pd.DataFrame(data)
                st.dataframe(df_usuarios, use_container_width=True, hide_index=True)
            else:
                st.info("No hay usuarios registrados")
            
            st.divider()
            
            st.markdown("### ➕ Crear Nuevo Usuario")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                nuevo_user_admin = st.text_input(
                    "Nombre usuario",
                    placeholder="juan",
                    key="admin_nuevo_user"
                )
            with col2:
                nueva_pass_admin = st.text_input(
                    "Contraseña",
                    type="password",
                    placeholder="••••••••",
                    key="admin_nueva_pass"
                )
            with col3:
                st.write("")  # Espaciado
                if st.button("✅ CREAR", type="primary", use_container_width=True, key="btn_admin_crear"):
                    if nuevo_user_admin and nueva_pass_admin:
                        if nuevo_user_admin in usuarios:
                            st.error("❌ El usuario ya existe")
                        else:
                            usuarios[nuevo_user_admin] = {
                                "contraseña": nueva_pass_admin,
                                "activo": True,
                                "fecha_registro": datetime.now().strftime("%Y-%m-%d")
                            }
                            guardar_usuarios(usuarios)
                            st.success(f"✅ Usuario '{nuevo_user_admin}' creado exitosamente")
                            st.rerun()
                    else:
                        st.error("⚠️ Completa todos los campos")
        
        with tab_registros:
            st.markdown("### 📊 Registros de Jornadas")
            
            usuarios = cargar_usuarios()
            usuarios_lista = [u for u in usuarios.keys() if u != "ADMIN"]
            
            if usuarios_lista:
                usuario_sel = st.selectbox(
                    "Selecciona un usuario",
                    usuarios_lista,
                    key="admin_select_usuario"
                )
                
                df = cargar_datos_usuario(usuario_sel)
                
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                    
                    # Estadísticas
                    col1, col2, col3 = st.columns(3)
                    col1.metric("📋 Total Jornadas", len(df))
                    col2.metric("⏱️ Total Horas", f"{df['Horas'].sum():.2f}h")
                    col3.metric("📊 Promedio Diario", f"{df['Horas'].mean():.2f}h")
                else:
                    st.info(f"Sin jornadas registradas para {usuario_sel}")
            else:
                st.info("No hay usuarios disponibles (solo admin)")
    
    # ============= PANEL USUARIO NORMAL =============
    else:
        tab_crono, tab_manual, tab_historial = st.tabs(["⏱️ CRONÓMETRO", "📝 MANUAL", "📊 HISTORIAL"])
        
        # TAB CRONÓMETRO
        with tab_crono:
            st.markdown("### ⏱️ Cronómetro de Jornada")
            
            # Calcular tiempo
            if st.session_state.cronometro_activo and st.session_state.tiempo_inicio:
                tiempo_total = (datetime.now() - st.session_state.tiempo_inicio).total_seconds() + st.session_state.tiempo_pausado
            else:
                tiempo_total = st.session_state.tiempo_pausado
            
            # Mostrar cronómetro
            st.markdown(
                f"<h1 style='text-align: center; color: #E5309F; font-family: monospace; font-size: 72px; margin: 30px 0;'>{formato_cronometro(tiempo_total)}</h1>",
                unsafe_allow_html=True
            )
            
            # Botones
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
            
            if st.button("✅ REGISTRAR JORNADA", use_container_width=True, type="primary", key="btn_registrar_crono"):
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
                    st.success(f"✅ ¡Jornada registrada! ({horas}h)")
                    st.rerun()
                else:
                    st.warning("⏱️ Inicia el cronómetro primero")
            
            # Auto-refresh si está activo
            if st.session_state.cronometro_activo:
                import time
                time.sleep(0.2)
                st.rerun()
        
        # TAB REGISTRO MANUAL
        with tab_manual:
            st.markdown("### 📝 Registro Manual de Jornada")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fecha_manual = st.date_input("Fecha", key="manual_fecha")
                entrada_manual = st.time_input("Hora entrada", value=datetime.strptime("08:00", "%H:%M").time(), key="manual_entrada")
            
            with col2:
                salida_manual = st.time_input("Hora salida", value=datetime.strptime("17:00", "%H:%M").time(), key="manual_salida")
            
            if st.button("✅ REGISTRAR", use_container_width=True, type="primary", key="btn_registrar_manual"):
                entrada_dt = datetime.combine(fecha_manual, entrada_manual)
                salida_dt = datetime.combine(fecha_manual, salida_manual)
                horas = round((salida_dt - entrada_dt).total_seconds() / 3600, 2)
                
                if horas > 0:
                    df = cargar_datos_usuario(st.session_state.usuario_logeado)
                    nueva_fila = pd.DataFrame({
                        "Fecha": [fecha_manual.strftime("%Y-%m-%d")],
                        "Entrada": [entrada_manual.strftime("%H:%M")],
                        "Salida": [salida_manual.strftime("%H:%M")],
                        "Horas": [horas]
                    })
                    df = pd.concat([df, nueva_fila], ignore_index=True)
                    guardar_datos_usuario(st.session_state.usuario_logeado, df)
                    
                    st.success(f"✅ Jornada registrada ({horas}h)")
                    st.rerun()
                else:
                    st.error("❌ La hora de salida debe ser posterior a la entrada")
        
        # TAB HISTORIAL
        with tab_historial:
            st.markdown("### 📊 Mi Historial de Jornadas")
            
            df = cargar_datos_usuario(st.session_state.usuario_logeado)
            
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                
                # Estadísticas
                col1, col2, col3 = st.columns(3)
                col1.metric("📋 Total Jornadas", len(df))
                col2.metric("⏱️ Total Horas", f"{df['Horas'].sum():.2f}h")
                col3.metric("📊 Promedio Diario", f"{df['Horas'].mean():.2f}h")
            else:
                st.info("Sin jornadas registradas aún")

# ============= FOOTER =============
st.divider()
st.caption("🐾 TopRedesValencia - Sistema de Registro de Jornada | v3.0 | Limpio y Funcional")
