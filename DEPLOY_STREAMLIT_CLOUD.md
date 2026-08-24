# 🌐 Desplegar en Streamlit Cloud - Guía Completa

Tu aplicación de **Mi Jornada** ahora está lista para desplegar **GRATIS** en Streamlit Cloud.

---

## 📋 Lo que necesitas

- Cuenta **GitHub** (gratuita)
- Cuenta **Google Cloud** (gratuita)
- Cuenta **Streamlit Cloud** (gratuita)

**Tiempo total:** ~20 minutos

---

## PASO 1: Preparar Google Sheets y Credenciales

### 1.1 Crear Google Cloud Project

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Haz clic en "Seleccionar un proyecto" (arriba a la izquierda)
3. Click en "NUEVO PROYECTO"
4. Nombre: `TopRedesValencia`
5. Click "Crear"
6. Espera a que se cree (2-3 segundos)

### 1.2 Activar Google Sheets API

1. En la barra de búsqueda, escribe `Sheets API`
2. Haz clic en "Google Sheets API"
3. Click en **ACTIVAR**

### 1.3 Activar Google Drive API

1. En la barra de búsqueda, escribe `Drive API`
2. Haz clic en "Google Drive API"
3. Click en **ACTIVAR**

### 1.4 Crear Cuenta de Servicio

1. Ve a **APIs y servicios** → **Credenciales**
2. Click en **+ CREAR CREDENCIALES**
3. Selecciona **Cuenta de servicio**

**En el formulario:**
- Nombre de cuenta de servicio: `mi-jornada-app`
- Click **Crear y continuar**
- Click **Continuar** (pasos opcionales)
- Click **Finalizar**

### 1.5 Descargar Clave JSON

1. Haz clic en la cuenta de servicio que acabas de crear
2. Ve a la pestaña **CLAVES**
3. Click **Agregar clave** → **Crear clave nueva**
4. Selecciona **JSON**
5. Click **Crear**

📌 **Se descargará un archivo JSON** - Guárdalo en un lugar seguro

---

## PASO 2: Preparar Repositorio GitHub

### 2.1 Crear Repositorio

1. Ve a [GitHub](https://github.com/new)
2. Nombre: `mi-jornada-topRedes`
3. Descripción: `App para registro de jornada laboral`
4. Visibilidad: **Público** (Streamlit Cloud necesita verlo)
5. Click **Create repository**

### 2.2 Agregar Archivos al Repositorio

Copia estos archivos a tu repositorio:

**Archivos necesarios:**
```
mi-jornada-topRedes/
├── app_jornada_cloud.py    (renombra como: app.py)
├── requirements.txt        (usa: requirements_cloud.txt)
├── .streamlit/
│   └── config.toml        (renombra: .streamlit_config.toml)
└── .gitignore
```

**Pasos:**
1. Clona el repo en tu computadora
2. Copia los archivos al mismo nivel que `app.py`
3. Renombra `app_jornada_cloud.py` a `app.py`
4. Renombra `requirements_cloud.txt` a `requirements.txt`
5. Crea carpeta `.streamlit/` y mueve `config.toml` dentro

### 2.3 Hacer Push a GitHub

```bash
git add .
git commit -m "Initial commit: Mi Jornada app"
git push origin main
```

---

## PASO 3: Configurar Streamlit Cloud

### 3.1 Conectar GitHub a Streamlit Cloud

1. Ve a [Streamlit Cloud](https://streamlit.io/cloud)
2. Click en **Sign in with GitHub** (o crea cuenta)
3. Autoriza Streamlit para acceder a tus repositorios

### 3.2 Crear Nueva App

1. Click **Create app**
2. Selecciona:
   - Repository: `tu-usuario/mi-jornada-topRedes`
   - Branch: `main`
   - Main file path: `app.py`
3. Click **Deploy**

⏳ **Espera 2-3 minutos mientras se despliega**

---

## PASO 4: Agregar Credenciales Google a Streamlit Cloud

### 4.1 Obtener las Credenciales

1. Abre el archivo JSON que descargaste de Google Cloud
2. Selecciona TODO el contenido
3. Cópialo (Ctrl+C o Cmd+C)

### 4.2 Agregar a Streamlit Cloud

1. En tu app en Streamlit Cloud, haz clic en **☰** (menú arriba a la derecha)
2. Selecciona **Settings**
3. Ve a **Secrets**
4. Pega el JSON descargado **EXACTAMENTE COMO ESTÁ**
5. Click **Save**

📌 Debe quedar así:
```
google_sheets_credentials = {
  "type": "service_account",
  "project_id": "...",
  ...
}
```

---

## ✅ ¡LISTO! Tu app está en línea

### URL de acceso:
```
https://share.streamlit.io/tu-usuario/mi-jornada-topRedes/main/app.py
```

Copia este link y **comparte con quien necesites** 📱

---

## 🔧 Solución de Problemas

### "Error: Google Sheets credentials not configured"

✅ **Solución:**
1. Ve a Settings → Secrets
2. Verifica que el JSON está completo
3. Click Save
4. Espera 5 segundos y recarga la app

### "ModuleNotFoundError: No module named 'gspread'"

✅ **Solución:**
1. Verifica que `requirements.txt` esté en la raíz
2. Contiene: `gspread==5.10.0`
3. Haz push: `git add . && git commit -m "Fix requirements" && git push`
4. Streamlit redeployará automáticamente

### "Permission denied" en Google Sheets

✅ **Solución:**
1. La app intenta crear automáticamente una hoja
2. Asegúrate de que la cuenta de servicio tiene permisos
3. O crea manualmente una hoja llamada "Mi Jornada"
4. Comparte la hoja con el email de la cuenta de servicio

### La app es muy lenta

✅ **Soluciones:**
- La primera carga tarda ~5-10 segundos (es normal)
- Elimina datos antiguos de Google Sheets
- Usa Streamlit Cloud con plan pagado si necesitas más recursos

---

## 📱 Compartir tu App

### Con amigos/colegas:
```
Abre esta URL en tu navegador:
https://share.streamlit.io/tu-usuario/mi-jornada-topRedes/main/app.py
```

### Con equipos:
- Usa el link público
- No necesitan instalar nada
- Funciona en móvil también

### Privada (solo tú):
1. En GitHub, cambia el repo a **Privado**
2. En Streamlit Cloud, requiere login de Streamlit

---

## 📊 Datos en Google Sheets

Tu data se guarda **automáticamente** en:
- **Google Sheets:** Llamado "Mi Jornada"
- **Ubicación:** Tu Google Drive
- **Sincronización:** En tiempo real
- **Respaldo:** Google lo guarda automáticamente

### Para acceder directamente:
1. Ve a [Google Drive](https://drive.google.com)
2. Busca "Mi Jornada"
3. Abre la hoja
4. Edita los datos manualmente si necesitas

---

## 🚀 Actualizaciones Futuras

Para cambiar la app:

1. **Modifica los archivos** en tu computadora
2. **Haz push a GitHub:**
```bash
git add .
git commit -m "Descripción del cambio"
git push origin main
```
3. **Streamlit se redespliega automáticamente** (1-2 minutos)

---

## 💰 Costos

✅ **TOTALMENTE GRATUITO:**
- Streamlit Cloud: Gratis (hasta 3 apps)
- Google Cloud: Gratis (credencial de servicio sin costo)
- GitHub: Gratis

💡 **No hay límites de usuarios ni de datos en el plan gratuito**

---

## 🎯 Checklist Final

- [ ] GitHub account creada
- [ ] Google Cloud Project creado
- [ ] Sheets API activada
- [ ] Drive API activada
- [ ] Cuenta de servicio creada
- [ ] JSON descargado y guardado
- [ ] Repositorio GitHub creado
- [ ] Archivos pusheados a GitHub
- [ ] App deplorada en Streamlit Cloud
- [ ] Credenciales agregadas a Secrets
- [ ] URL funciona en el navegador

---

## 📞 Soporte

Si algo no funciona:

1. **Error en deploy:** Ve a "Logs" en Streamlit Cloud (arriba a la derecha)
2. **Problema con Google:** Revisa Google Cloud Console
3. **Duda técnica:** Revisa la documentación oficial:
   - [Streamlit Cloud Docs](https://docs.streamlit.io/deploy/streamlit-community-cloud)
   - [Google Sheets API](https://developers.google.com/sheets/api)

---

## 🎉 ¡FELICIDADES!

Tu app **Mi Jornada** está ahora en línea, disponible 24/7, con datos sincronizados en tiempo real con Google Sheets.

**TopRedesValencia**
- 📱 683 597 759
- 🌐 topredesvalencia.com
