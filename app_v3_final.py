"""
REGISTRO DE JORNADA LABORAL - TopRedesValencia v3
VERSIÓN LIMPIA - SIN ERRORES DE IDs DUPLICADOS
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import json
import io
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
    return pd.DataFrame(columns=['Fecha', 'Entrada', 'Salida', 'Horas', 'Ubicacion'])

def guardar_datos_usuario(usuario, df):
    df.to_csv(f"datos_usuarios/{usuario}.csv", index=False)

def formato_cronometro(segundos):
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = int(segundos % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def calcular_horas_semanales(df_usuario):
    """Calcula horas por semana (semana ISO: lunes a domingo)"""
    if df_usuario.empty:
        return pd.DataFrame()
    
    df_usuario['Fecha'] = pd.to_datetime(df_usuario['Fecha'])
    df_usuario['Semana'] = df_usuario['Fecha'].dt.isocalendar().week
    df_usuario['Año'] = df_usuario['Fecha'].dt.year
    
    horas_por_semana = df_usuario.groupby(['Año', 'Semana']).agg({
        'Horas': 'sum',
        'Fecha': ['min', 'max', 'count']
    }).round(2)
    
    horas_por_semana.columns = ['Total_Horas', 'Fecha_Inicio', 'Fecha_Fin', 'Jornadas']
    horas_por_semana['Extras'] = (horas_por_semana['Total_Horas'] - 40).apply(lambda x: max(0, x))
    horas_por_semana['Deficit'] = (40 - horas_por_semana['Total_Horas']).apply(lambda x: max(0, x))
    horas_por_semana['Estado'] = horas_por_semana.apply(
        lambda row: f"+{row['Extras']:.2f}h extras" if row['Extras'] > 0 
        else f"-{row['Deficit']:.2f}h falta" if row['Deficit'] > 0 
        else "✅ 40h exactas",
        axis=1
    )
    
    return horas_por_semana.reset_index()

# Ubicaciones típicas de TopRedesValencia
UBICACIONES = [
    "Bétera (Oficina)",
    "Valencia",
    "Castellón",
    "Alicante",
    "En ruta",
    "Teletrabajo",
    "Otro"
]

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
        tab_usuarios, tab_registros, tab_semanal = st.tabs(["👥 Gestión de Usuarios", "📊 Ver Registros", "⏱️ Control Semanal"])
        
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
            st.markdown("### 📊 Registros de Jornadas - Todos los Usuarios")
            
            usuarios = cargar_usuarios()
            usuarios_lista = [u for u in usuarios.keys() if u != "ADMIN"]
            
            if usuarios_lista:
                # Opción 1: Ver todos o filtrar
                tab_todos, tab_individual = st.tabs(["👥 Todos los Usuarios", "👤 Usuario Individual"])
                
                with tab_todos:
                    st.markdown("#### 📋 Todas las Jornadas Registradas")
                    
                    # Combinar datos de todos los usuarios
                    todos_datos = []
                    for usuario in usuarios_lista:
                        df_usuario = cargar_datos_usuario(usuario)
                        if not df_usuario.empty:
                            df_usuario['Usuario'] = usuario
                            todos_datos.append(df_usuario)
                    
                    if todos_datos:
                        df_combinado = pd.concat(todos_datos, ignore_index=True)
                        
                        # Reorganizar columnas
                        columnas_orden = ['Usuario', 'Fecha', 'Entrada', 'Salida', 'Horas', 'Ubicacion']
                        df_combinado = df_combinado[columnas_orden]
                        
                        # Ordenar por fecha descendente
                        df_combinado = df_combinado.sort_values('Fecha', ascending=False)
                        
                        # Mostrar tabla
                        st.dataframe(df_combinado, use_container_width=True, hide_index=True)
                        
                        st.divider()
                        
                        # Estadísticas globales
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("👥 Usuarios Activos", len(usuarios_lista))
                        col2.metric("📋 Total Jornadas", len(df_combinado))
                        col3.metric("⏱️ Total Horas", f"{df_combinado['Horas'].sum():.2f}h")
                        col4.metric("📊 Promedio por Jornada", f"{df_combinado['Horas'].mean():.2f}h")
                        
                        st.divider()
                        
                        # Estadísticas por usuario
                        st.markdown("#### 📊 Resumen por Usuario")
                        resumen_usuarios = df_combinado.groupby('Usuario').agg({
                            'Horas': ['sum', 'count', 'mean']
                        }).round(2)
                        resumen_usuarios.columns = ['Total Horas', 'Jornadas', 'Promedio']
                        st.dataframe(resumen_usuarios, use_container_width=True)
                        
                        st.divider()
                        
                        # Descargar Excel
                        col_excel, col_espacio = st.columns([1, 2])
                        with col_excel:
                            excel_buffer = io.BytesIO()
                            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                                df_combinado.to_excel(writer, sheet_name='Jornadas', index=False)
                                resumen_usuarios.to_excel(writer, sheet_name='Resumen')
                            excel_buffer.seek(0)
                            
                            st.download_button(
                                label="📥 Descargar Excel Completo",
                                data=excel_buffer,
                                file_name=f"jornadas_todas_{datetime.now().strftime('%Y%m%d')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    else:
                        st.info("Sin jornadas registradas aún")
                
                with tab_individual:
                    st.markdown("#### 👤 Filtrar por Usuario")
                    
                    usuario_sel = st.selectbox(
                        "Selecciona un usuario",
                        usuarios_lista,
                        key="admin_select_usuario"
                    )
                    
                    df = cargar_datos_usuario(usuario_sel)
                    
                    if not df.empty:
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        # Estadísticas individuales
                        col1, col2, col3 = st.columns(3)
                        col1.metric("📋 Total Jornadas", len(df))
                        col2.metric("⏱️ Total Horas", f"{df['Horas'].sum():.2f}h")
                        col3.metric("📊 Promedio Diario", f"{df['Horas'].mean():.2f}h")
                        
                        st.divider()
                        
                        # Descargar individual
                        excel_buffer = io.BytesIO()
                        df.to_excel(excel_buffer, sheet_name='Jornadas', index=False)
                        excel_buffer.seek(0)
                        
                        st.download_button(
                            label=f"📥 Descargar Excel de {usuario_sel}",
                            data=excel_buffer,
                            file_name=f"jornadas_{usuario_sel}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.info(f"Sin jornadas registradas para {usuario_sel}")
            else:
                st.info("No hay usuarios disponibles (solo admin)")
        
        with tab_semanal:
            st.markdown("### ⏱️ Control de Horas Semanales (40h/semana)")
            
            usuarios = cargar_usuarios()
            usuarios_lista = [u for u in usuarios.keys() if u != "ADMIN"]
            
            if usuarios_lista:
                # Opción 1: Ver todos o filtrar
                tab_todas_sem, tab_usuario_sem = st.tabs(["👥 Resumen Global", "👤 Por Usuario"])
                
                with tab_todas_sem:
                    st.markdown("#### 📊 Resumen Semanal de Todos los Usuarios")
                    
                    # Compilar datos de todas las semanas de todos los usuarios
                    todas_semanas = []
                    for usuario in usuarios_lista:
                        df = cargar_datos_usuario(usuario)
                        if not df.empty:
                            df_sem = calcular_horas_semanales(df.copy())
                            if not df_sem.empty:
                                df_sem['Usuario'] = usuario
                                todas_semanas.append(df_sem)
                    
                    if todas_semanas:
                        df_todas = pd.concat(todas_semanas, ignore_index=True)
                        
                        # Reorganizar y formatear
                        df_todas['Fecha_Inicio'] = pd.to_datetime(df_todas['Fecha_Inicio']).dt.strftime('%Y-%m-%d')
                        df_todas['Fecha_Fin'] = pd.to_datetime(df_todas['Fecha_Fin']).dt.strftime('%Y-%m-%d')
                        
                        # Reordenar columnas y ordenar
                        columnas_orden = ['Año', 'Semana', 'Usuario', 'Fecha_Inicio', 'Fecha_Fin', 'Jornadas', 'Total_Horas', 'Extras', 'Deficit', 'Estado']
                        df_todas = df_todas[columnas_orden].sort_values(['Año', 'Semana', 'Usuario'], ascending=[False, False, True])
                        
                        # Mostrar tabla
                        st.dataframe(df_todas, use_container_width=True, hide_index=True)
                        
                        st.divider()
                        
                        # Estadísticas globales
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("⏱️ Total Horas", f"{df_todas['Total_Horas'].sum():.2f}h")
                        col2.metric("⚡ Total Extras", f"{df_todas['Extras'].sum():.2f}h")
                        col3.metric("❌ Total Déficit", f"{df_todas['Deficit'].sum():.2f}h")
                        col4.metric("📊 Promedio/Semana", f"{df_todas['Total_Horas'].mean():.2f}h")
                        
                        st.divider()
                        
                        # Resumen por usuario
                        st.markdown("#### 👥 Totales por Usuario")
                        resumen_usuarios_sem = df_todas.groupby('Usuario').agg({
                            'Total_Horas': 'sum',
                            'Extras': 'sum',
                            'Deficit': 'sum',
                            'Jornadas': 'sum'
                        }).round(2)
                        resumen_usuarios_sem.columns = ['Total Horas', 'Horas Extras', 'Horas Déficit', 'Total Jornadas']
                        st.dataframe(resumen_usuarios_sem, use_container_width=True)
                    else:
                        st.info("Sin datos de jornadas registradas")
                
                with tab_usuario_sem:
                    st.markdown("#### 👤 Control Semanal por Usuario")
                    
                    usuario_sel = st.selectbox(
                        "Selecciona un usuario",
                        usuarios_lista,
                        key="admin_select_usuario_semanal"
                    )
                    
                    df = cargar_datos_usuario(usuario_sel)
                    
                    if not df.empty:
                        df_sem = calcular_horas_semanales(df.copy())
                        
                        if not df_sem.empty:
                            # Formatear fechas
                            df_sem['Fecha_Inicio'] = pd.to_datetime(df_sem['Fecha_Inicio']).dt.strftime('%Y-%m-%d')
                            df_sem['Fecha_Fin'] = pd.to_datetime(df_sem['Fecha_Fin']).dt.strftime('%Y-%m-%d')
                            
                            # Reorganizar y ordenar
                            columnas_orden = ['Año', 'Semana', 'Fecha_Inicio', 'Fecha_Fin', 'Jornadas', 'Total_Horas', 'Extras', 'Deficit', 'Estado']
                            df_sem = df_sem[columnas_orden].sort_values(['Año', 'Semana'], ascending=[False, False])
                            
                            # Mostrar tabla
                            st.dataframe(df_sem, use_container_width=True, hide_index=True)
                            
                            st.divider()
                            
                            # Estadísticas del usuario
                            col1, col2, col3, col4 = st.columns(4)
                            col1.metric("⏱️ Total Horas", f"{df_sem['Total_Horas'].sum():.2f}h")
                            col2.metric("⚡ Total Extras", f"{df_sem['Extras'].sum():.2f}h")
                            col3.metric("❌ Total Déficit", f"{df_sem['Deficit'].sum():.2f}h")
                            col4.metric("📊 Promedio/Semana", f"{df_sem['Total_Horas'].mean():.2f}h")
                            
                            st.divider()
                            
                            # Última semana destacada
                            if len(df_sem) > 0:
                                ultima_semana = df_sem.iloc[0]
                                st.markdown("#### 📌 Última Semana")
                                col1, col2, col3 = st.columns(3)
                                col1.metric("Semana", f"{int(ultima_semana['Año'])}-S{int(ultima_semana['Semana'])}")
                                col2.metric("Horas Trabajadas", f"{ultima_semana['Total_Horas']:.2f}h")
                                col3.metric("Estado", ultima_semana['Estado'])
                        else:
                            st.info(f"Sin datos de semanas para {usuario_sel}")
                    else:
                        st.info(f"Sin jornadas registradas para {usuario_sel}")
            else:
                st.info("No hay usuarios disponibles (solo admin)")
    else:
        tab_crono, tab_manual, tab_historial, tab_resumen_sem = st.tabs(["⏱️ CRONÓMETRO", "📝 MANUAL", "📊 HISTORIAL", "📊 RESUMEN SEMANAL"])
        
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
            
            # Ubicación para cronómetro
            col_ubi1, col_ubi2 = st.columns([2, 1])
            with col_ubi1:
                ubicacion_crono = st.selectbox(
                    "📍 Ubicación de trabajo",
                    UBICACIONES,
                    key="crono_ubicacion"
                )
            with col_ubi2:
                if ubicacion_crono == "Otro":
                    ubicacion_crono = st.text_input(
                        "Especifica ubicación",
                        placeholder="Ej: Casa del cliente",
                        key="crono_ubicacion_custom"
                    )
            
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
                        "Horas": [horas],
                        "Ubicacion": [ubicacion_crono if ubicacion_crono else "Sin especificar"]
                    })
                    df = pd.concat([df, nueva_fila], ignore_index=True)
                    guardar_datos_usuario(st.session_state.usuario_logeado, df)
                    
                    st.session_state.tiempo_pausado = 0
                    st.session_state.cronometro_activo = False
                    st.success(f"✅ ¡Jornada registrada! ({horas}h en {ubicacion_crono})")
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
            
            st.divider()
            
            # Ubicación para registro manual
            col_ubi1, col_ubi2 = st.columns([2, 1])
            with col_ubi1:
                ubicacion_manual = st.selectbox(
                    "📍 Ubicación de trabajo",
                    UBICACIONES,
                    key="manual_ubicacion"
                )
            with col_ubi2:
                if ubicacion_manual == "Otro":
                    ubicacion_manual = st.text_input(
                        "Especifica ubicación",
                        placeholder="Ej: Casa del cliente",
                        key="manual_ubicacion_custom"
                    )
            
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
                        "Horas": [horas],
                        "Ubicacion": [ubicacion_manual if ubicacion_manual else "Sin especificar"]
                    })
                    df = pd.concat([df, nueva_fila], ignore_index=True)
                    guardar_datos_usuario(st.session_state.usuario_logeado, df)
                    
                    st.success(f"✅ Jornada registrada ({horas}h en {ubicacion_manual})")
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
        
        with tab_resumen_sem:
            st.markdown("### 📊 Resumen Semanal (40h/semana)")
            
            df = cargar_datos_usuario(st.session_state.usuario_logeado)
            
            if not df.empty:
                df_sem = calcular_horas_semanales(df.copy())
                
                if not df_sem.empty:
                    # Formatear fechas
                    df_sem['Fecha_Inicio'] = pd.to_datetime(df_sem['Fecha_Inicio']).dt.strftime('%Y-%m-%d')
                    df_sem['Fecha_Fin'] = pd.to_datetime(df_sem['Fecha_Fin']).dt.strftime('%Y-%m-%d')
                    
                    # Reorganizar y ordenar
                    columnas_orden = ['Año', 'Semana', 'Fecha_Inicio', 'Fecha_Fin', 'Jornadas', 'Total_Horas', 'Extras', 'Deficit', 'Estado']
                    df_sem = df_sem[columnas_orden].sort_values(['Año', 'Semana'], ascending=[False, False])
                    
                    # Mostrar tabla
                    st.dataframe(df_sem, use_container_width=True, hide_index=True)
                    
                    st.divider()
                    
                    # Estadísticas
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("⏱️ Total Horas", f"{df_sem['Total_Horas'].sum():.2f}h")
                    col2.metric("⚡ Extras Acumuladas", f"{df_sem['Extras'].sum():.2f}h")
                    col3.metric("❌ Déficit Acumulado", f"{df_sem['Deficit'].sum():.2f}h")
                    col4.metric("📊 Promedio/Semana", f"{df_sem['Total_Horas'].mean():.2f}h")
                    
                    st.divider()
                    
                    # Última semana destacada
                    if len(df_sem) > 0:
                        ultima_semana = df_sem.iloc[0]
                        st.markdown("#### 📌 Última Semana")
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Semana", f"{int(ultima_semana['Año'])}-S{int(ultima_semana['Semana'])}")
                        col2.metric("Horas Trabajadas", f"{ultima_semana['Total_Horas']:.2f}h")
                        col3.metric("Horas Extras/Déficit", ultima_semana['Estado'])
                        col4.metric("Jornadas", int(ultima_semana['Jornadas']))
                else:
                    st.info("Sin datos de semanas calculadas")
            else:
                st.info("Sin jornadas registradas aún")

# ============= FOOTER =============
st.divider()
st.caption("🐾 TopRedesValencia - Sistema de Registro de Jornada | v3.0 | Limpio y Funcional")
