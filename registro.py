import streamlit as st
from sqlalchemy import text
import time
import os
from sqlalchemy import create_engine
import pandas as pd
from streamlit_javascript import st_javascript

# --- CONFIGURACIÓN DEL EVENTO ACTUAL ---
ID_REUNION = "webinar-Debido Proceso"  # Cambia esto en cada curso
CUPO_MAXIMO = 100
LINK_ZOOM = "https://us06web.zoom.us/j/89038853644?pwd=nF7qRs4SrzdyxhMB2JgCShyxgkhBIw.1"
LINK_YOUTUBE = "https://youtube.com/live/..." # Tu link de respaldo
NOMBRE_EVENTO = "Webinar-Debido Proceso"

# --- CONFIGURACIÓN DE BASE DE DATOS (DEBE IR AL INICIO) ---
try:
    creds = st.secrets["db_credentials"]
    engine = create_engine(
        f"mysql+pymysql://{creds['user']}:{creds['pass']}@{creds['host']}/{creds['name']}",
        pool_pre_ping=True
    )
except Exception as e:
    st.error(f"Error de conexión a BD: {e}")
    st.stop()

# --- CONSULTAR CUPO ACTUAL (SIEMPRE SE HACE) ---
try:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM directorio_tratamiento 
            WHERE canal_autorizacion LIKE :filtro
        """), {"filtro": f"%{ID_REUNION}%"})
        conteo_actual = result.scalar()
except Exception as e:
    conteo_actual = 0
    st.warning(f"No se pudo consultar cupo: {e}")

# --- DETERMINAR LINK DE DESTINO SEGÚN CUPO ---
# ESTO ES CRÍTICO: Se decide ANTES de cualquier verificación de registro
if conteo_actual >= CUPO_MAXIMO:
    link_destino = LINK_YOUTUBE
    mensaje_cupo = "⚠️ ¡Sala de Zoom llena! Serás redirigido a YouTube."
    tipo_sala = "YouTube (transmisión)"
else:
    link_destino = LINK_ZOOM
    mensaje_cupo = "✨ Tienes cupo en Zoom."
    tipo_sala = "Zoom (interactivo)"

# --- VERIFICAR REGISTRO PREVIO EN NAVEGADOR ---
try:
    registro_previo = st_javascript(f"localStorage.getItem('mbeducacion_registro_{ID_REUNION}');")
except:
    registro_previo = None

# --- SI YA SE REGISTRÓ: ACCESO DIRECTO (PERO CON EL LINK CORRECTO SEGÚN CUPO) ---
if registro_previo == "true":
    st.title(NOMBRE_EVENTO)
    st.success("✨ ¡Bienvenido de nuevo! Ya estás registrado.")
    
    # MOSTRAR INFORMACIÓN SEGÚN EL ESTADO DEL CUPO
    if conteo_actual >= CUPO_MAXIMO:
        st.warning("📺 La sala de Zoom está llena. Accederás a la transmisión por YouTube.")
    else:
        st.info("🎥 Accederás a la sala interactiva de Zoom.")
    
    # BOTÓN DE ACCESO CON EL LINK CORRECTO (YouTube si cupo lleno, Zoom si hay espacio)
    st.markdown(f"""
        <a href="{link_destino}" target="_blank" style="
            text-decoration: none; background-color: #2D8CFF; color: white;
            padding: 15px 25px; border-radius: 10px; font-weight: bold;
            display: inline-block; text-align: center; width: 100%;
        ">🚀 INGRESAR A LA TRANSMISIÓN ({tipo_sala})</a>
    """, unsafe_allow_html=True)
    
    # Opción para resetear
    if st.button("No soy yo / Registrar nuevos datos"):
        st_javascript(f"localStorage.removeItem('mbeducacion_registro_{ID_REUNION}');")
        st.rerun()
    st.stop()

# --- NUEVO REGISTRO (FORMULARIO) ---
st.title("Registro de Asistencia y Tratamiento de Datos")
st.subheader(f"Bienvenido al {NOMBRE_EVENTO}, MB Educación")

# Mostrar advertencia de cupo ANTES del formulario
if conteo_actual >= CUPO_MAXIMO:
    st.warning("⚠️ **Importante:** El cupo de Zoom (100 personas) ya está completo. Al registrarte, accederás a la transmisión en vivo por YouTube.")
else:
    st.info(f"📊 **Cupos disponibles:** {CUPO_MAXIMO - conteo_actual} de {CUPO_MAXIMO} en Zoom")

with st.form("registro_publico", clear_on_submit=True):
    # [Tu formulario existente aquí...]
    nombre = st.text_input("Nombre Completo *")
    col1, col2 = st.columns([1, 2])
    with col1:
        tipo_doc = st.selectbox("Tipo de Documento *", ["C.C.", "NIT", "C.E.", "Pasaporte", "T.I.", "Otro"])
    with col2:
        doc_identidad = st.text_input("Número de Documento *")
    institucion = st.text_input("Institución Educativa / Empresa / Asociación *")
    rol_cargo = st.text_input("Cargo en la Institución *")
    email = st.text_input("Correo Electrónico *")
    
    st.markdown("---")
    st.write("🔒 **Autorización de Tratamiento de Datos**")
    with st.expander("Leer Autorización de Tratamiento de Datos Personales"):
        st.markdown("""
        ### MB EDUCACIÓN - AUTORIZACIÓN PARA EL TRATAMIENTO DE DATOS PERSONALES
        
        De conformidad con la legislación legal vigente y la Política de Tratamiento de Datos Personales de MB Educación, el tratamiento de los datos que se reportan en este Formulario se regirá por las siguientes condiciones:
        a) Yo, al diligenciar este Formulario, concedo autorización previa, expresa e informada a MB Educación, para el tratamiento de los datos que suministro, sabiendo que he sido informado que la finalidad de dichos datos es adquirir un producto o solicitar un servicio que ella ofrece ahora o en el futuro, de tal manera que puedan tramitar mi solicitud adecuadamente, contactarme en caso de que se requiera y adelantar todas las acciones para el logro del particular.
        b) Conozco y acepto que esta información será tratada de acuerdo con la Política de Tratamiento de Datos Personales de MB Educación disponible en su página Web, que declaro haber leído y conocer, en especial en lo referente a mis derechos y a los procedimientos con que la Entidad cuenta, para hacerlos efectivos ante sus autoridades.
        c) Se que los siguientes son los derechos básicos que tengo como titular de los datos que se han diligenciado en este Formulario: 1) Todos los datos registrados en este Formulario sólo serán empleados por MB Educación para cumplir la finalidad expuesta en el punto (a) del presente Aviso; 2) En cualquier momento, puedo solicitar una consulta de la información con que MB Educación cuenta sobre mí, dirigiéndome al Oficial de Protección de Datos Personales de la Entidad; 3) MB Educación velará por la confidencialidad y privacidad de los datos personales de los titulares que están siendo reportados, según las disposiciones legales vigentes; 4) En cualquier momento puedo solicitar una prueba de esta autorización.
        d) El Oficial de Protección de Datos Personales de la Entidad, ante quien puedo ejercer mis derechos, de forma gratuita, lo contactar en la siguiente dirección electrónica: usodedatos@mbeducacion.com.co 

        """)
    
    acepta = st.checkbox("He leído y autorizo el tratamiento de mis datos personales *")
    acepta_promos = st.checkbox("Acepto que MB Educación me envíe información de sus servicios o productos")
    
    boton_registro = st.form_submit_button("REGISTRARME E INGRESAR")

# --- PROCESAR REGISTRO ---
if boton_registro:
    # Validaciones
    errores = []
    if not nombre: errores.append("Nombre Completo")
    if not doc_identidad: errores.append("Número de Documento")
    if not institucion: errores.append("Institución")
    if not email: errores.append("Correo Electrónico")
    if not acepta: errores.append("Aceptación de Tratamiento de Datos")

    if not errores:
        try:
            # GUARDAR EN BASE DE DATOS
            with engine.begin() as conn:
                query = text("""
                    INSERT INTO directorio_tratamiento 
                    (contacto_nombre, tipo_documento, documento_identidad, institucion, rol_cargo, email, habeas_data, autoriza_env_info, canal_autorizacion) 
                    VALUES (:nom, :tdoc, :doc, :inst, :rol, :mail, :hab, :env_info, :cnal)
                """)
                conn.execute(query, {
                    "nom": nombre, 
                    "tdoc": tipo_doc,
                    "doc": doc_identidad,                    
                    "inst": institucion,
                    "rol": rol_cargo,
                    "mail": email,
                    "hab": 1,
                    "env_info": 1 if acepta_promos else 0,
                    "cnal": f"Registro Zoom - {ID_REUNION} - {time.strftime('%d/%m/%Y %H:%M')}"
                })
            
            # GUARDAR EN LOCALSTORAGE
            st_javascript(f"localStorage.setItem('mbeducacion_registro_{ID_REUNION}', 'true');")
            
            # MENSAJE DE ÉXITO CON INFORMACIÓN DE DESTINO
            st.success("✅ ¡Registro exitoso!")
	    	            
            if conteo_actual >= CUPO_MAXIMO:
                st.info("📺 Serás redirigido a YouTube (la sala de Zoom está llena)")
            else:
                st.info("🎥 Serás redirigido a Zoom")
            
            # REDIRECCIÓN (SIEMPRE AL LINK DETERMINADO POR CUPO)
            time.sleep(3)
            st.markdown(f'<meta http-equiv="refresh" content="0; url={link_destino}">', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")
    else:
        st.error("Completa los campos obligatorios:")
        for error in errores:
            st.write(f"- {error}")
