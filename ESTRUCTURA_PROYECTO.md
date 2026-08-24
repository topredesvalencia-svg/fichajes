# 📁 Estructura de Proyecto para GitHub

Así debe verse tu repositorio:

```
mi-jornada-topRedes/
│
├── 📄 app.py                    (renombra de: app_jornada_cloud.py)
├── 📄 requirements.txt          (renombra de: requirements_cloud.txt)
├── 📄 .gitignore
├── 📄 README.md                 (crea este archivo)
│
├── 📁 .streamlit/
│   └── 📄 config.toml          (renombra de: .streamlit_config.toml)
│
├── 📁 .git/                    (se crea automáticamente)
└── 📁 __pycache__/             (se crea automáticamente)
```

---

## 📝 Crear README.md

Crea un archivo `README.md` en la raíz con:

```markdown
# 📋 Mi Jornada - TopRedesValencia

Aplicación web para registrar y gestionar horas laborales con sincronización en tiempo real.

## 🚀 Demo Online

https://share.streamlit.io/tu-usuario/mi-jornada-topRedes/main/app.py

## ✨ Características

- 📝 Registro rápido de entrada/salida
- 📊 Historial editable
- 📥 Exportar a Excel
- 📈 Estadísticas y gráficos
- ☁️ Datos en Google Sheets (sincronización en tiempo real)
- 📱 Funciona en móvil

## 🛠️ Tecnología

- **Frontend:** Streamlit
- **Backend:** Python
- **Base de datos:** Google Sheets
- **Hosting:** Streamlit Cloud

## 📋 Requisitos de Desarrollo

```bash
pip install -r requirements.txt
```

## ▶️ Ejecutar Localmente

```bash
streamlit run app.py
```

## 🌐 Desplegar en Streamlit Cloud

1. Haz fork/clon de este repo
2. Ve a https://streamlit.io/cloud
3. Conecta tu GitHub
4. Selecciona este repo
5. Configura secrets con credenciales de Google
6. ¡Listo!

## 📖 Guías

- [Guía de Despliegue Completa](DEPLOY_STREAMLIT_CLOUD.md)
- [Guía Rápida](GUIA_RAPIDA_CLOUD.md)

## 📞 Contacto

**TopRedesValencia**
- 📱 683 597 759
- 🌐 topredesvalencia.com

## 📄 Licencia

Uso interno TopRedesValencia © 2024
```

---

## 📝 Crear .streamlit/config.toml

Crea una carpeta `.streamlit` y dentro un archivo `config.toml`:

```toml
[theme]
primaryColor = "#E01B7D"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = false
toolbarMode = "minimal"

[server]
port = 8501
maxUploadSize = 200
enableXsrfProtection = true

[logger]
level = "info"
```

---

## 📝 Archivo requirements.txt

```
streamlit==1.28.1
pandas==2.0.3
openpyxl==3.1.2
gspread==5.10.0
oauth2client==4.1.3
google-auth-httplib2==0.2.0
google-auth-oauthlib==1.1.0
```

---

## 📝 Archivo .gitignore

```
# Credenciales (NUNCA subas esto a GitHub)
credentials.json
.streamlit/secrets.toml
.env

# Datos locales
jornada_data.xlsx
*.xlsx

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Streamlit
.cache/
```

---

## 🚀 Pasos para Publicar

### 1. Clona o crea tu repo

```bash
# Si es nuevo:
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/tu-usuario/mi-jornada-topRedes.git
git push -u origin main

# Si es existente:
git add .
git commit -m "Tu mensaje"
git push origin main
```

### 2. Verifica que está todo

En GitHub, abre tu repo y verifica:
- ✅ `app.py` existe
- ✅ `requirements.txt` existe
- ✅ `.gitignore` existe
- ✅ Carpeta `.streamlit/config.toml` existe
- ✅ No hay archivos como `credentials.json` o `.xlsx`

### 3. Despliega en Streamlit Cloud

1. Ve a https://streamlit.io/cloud
2. Click "Sign in with GitHub"
3. Click "Create app"
4. Selecciona repo
5. Main file: `app.py`
6. Click "Deploy"

### 4. Agrega credenciales

1. En tu app, click ☰ → Settings → Secrets
2. Pega tu JSON de Google Cloud
3. Click Save
4. Espera a que se redeploy automáticamente

---

## 📊 Sincronización de Datos

La app crea automáticamente una hoja de Google Sheets llamada **"Mi Jornada"** en tu Google Drive.

### Acceder directamente:
1. Ve a https://drive.google.com
2. Busca "Mi Jornada"
3. Abre la hoja
4. Edita datos manualmente si lo necesitas

### Estructura de datos:
```
Fecha       | Entrada | Salida | Horas
2024-01-15  | 09:00   | 18:00  | 8.5
2024-01-16  | 08:30   | 17:30  | 9.0
```

---

## 🔄 Actualizar la App

Cada vez que hagas cambios:

```bash
# 1. Edita los archivos en tu IDE
# 2. Guarda los cambios
# 3. Haz push:
git add .
git commit -m "Descripción de cambios"
git push origin main

# 4. Streamlit se redeploy automáticamente (1-2 minutos)
```

---

## ⚙️ Variables de Entorno

Para desarrollo local, crea archivo `.streamlit/secrets.toml`:

```toml
[google_sheets_credentials]
type = "service_account"
project_id = "..."
private_key_id = "..."
...
```

⚠️ **NUNCA commits esto a GitHub** - ya está en `.gitignore`

---

## 🎯 URL Final

Tu app estará disponible en:

```
https://share.streamlit.io/tu-usuario/mi-jornada-topRedes/main/app.py
```

Puedes compartir este link con:
- Colegas
- Clientes
- En redes sociales
- En tu web

---

## 📞 Soporte

Cualquier problema en el despliegue:

1. **Ver logs:** En Streamlit Cloud, click ☰ → Logs
2. **Revisar errores:** Google Cloud Console
3. **Documentación:** https://docs.streamlit.io

---

**¡Tu app está lista para el mundo! 🌍**
