# ⚡ Guía Rápida: Streamlit Cloud en 5 Pasos

## 🎯 Resumen Ultra-Rápido

Tu app estará **online y gratuita** en 20 minutos.

---

## PASO 1: Google Cloud (3 min)

1. Ve a https://console.cloud.google.com/
2. Crea proyecto llamado "TopRedesValencia"
3. Activa:
   - Google Sheets API
   - Google Drive API
4. Crea Cuenta de Servicio
5. Descarga JSON

📌 **Guarda este JSON en un lugar seguro**

---

## PASO 2: GitHub (5 min)

1. Ve a https://github.com/new
2. Crea repo: `mi-jornada-topRedes`
3. Copia estos archivos:
   ```
   ✅ app_jornada_cloud.py  → renombra a: app.py
   ✅ requirements_cloud.txt → renombra a: requirements.txt
   ✅ .gitignore
   ✅ .streamlit/config.toml (crea carpeta .streamlit)
   ```
4. Haz push:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

---

## PASO 3: Streamlit Cloud (2 min)

1. Ve a https://streamlit.io/cloud
2. Click "Sign in with GitHub"
3. Selecciona repo: `mi-jornada-topRedes`
4. File: `app.py`
5. Click "Deploy"

⏳ **Espera 2-3 minutos**

---

## PASO 4: Agregar Credenciales (2 min)

1. Abre el **JSON descargado** en editor
2. Cópialo (todo el contenido)
3. En tu app Streamlit Cloud → **Settings** → **Secrets**
4. Pega exactamente:
   ```
   google_sheets_credentials = {
     "type": "service_account",
     ...JSON completo aquí...
   }
   ```
5. Click "Save"

---

## PASO 5: ¡LISTO! (0 min)

Tu URL es:
```
https://share.streamlit.io/TU-USUARIO/mi-jornada-topRedes/main/app.py
```

**Comparte este link** - ¡La app funciona!

---

## ✅ Características que tienes

- ✅ Registro de entrada/salida desde cualquier lugar
- ✅ Datos sincronizados en Google Sheets
- ✅ Edición de horas
- ✅ Exportar a Excel
- ✅ Estadísticas y gráficos
- ✅ Acceso desde móvil
- ✅ Totalmente gratis
- ✅ Disponible 24/7

---

## 🆘 Problemas Comunes

| Problema | Solución |
|----------|----------|
| "Credentials not configured" | Ve a Secrets y verifica el JSON |
| "Module not found" | Revisa requirements.txt en repo |
| App tarda en cargar | Es normal la primera vez (10 seg) |
| "Permission denied" | Verifica Google Cloud credentials |

---

## 📞 Contacto

Cualquier duda:
- **TopRedesValencia**
- 📱 683 597 759
- 🌐 topredesvalencia.com

---

**¡Disfruta tu app online! 🎉**
