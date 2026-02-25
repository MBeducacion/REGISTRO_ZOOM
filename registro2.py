import streamlit as st
from sqlalchemy import create_engine, text
import time
import pandas as pd
from streamlit_javascript import st_javascript

# --- CONFIGURACIÓN DEL EVENTO ACTUAL ---
ID_REUNION = "Webinar-Debido Proceso"  # Cambia esto en cada curso
CUPO_MAXIMO = 100
LINK_ZOOM = "https://us06web.zoom.us/j/89038853644?pwd=nF7qRs4SrzdyxhMB2JgCShyxgkhBIw.1"  # Usé el link que tenías en el código
LINK_YOUTUBE = "https://youtube.com/live/..." # Tu link de respaldo
NOMBRE_EVENTO = "Webinar - Debido Proceso"

# --- CONFIGURACIÓN DE LA BASE DE DATOS (DEBE IR ANTES DE USAR 'engine') ---
# 1. Cargar credenciales desde los Secrets de Streamlit
try:
    creds = st.secrets["db_credentials"]
    DB_USER = creds["user"]
    DB_PASS = creds["pass"]
    DB_HOST = creds["host"]
    DB_NAME = creds["name"]

    # 2. Crear el motor de conexión
    engine = create_engine(
        f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}",
        pool_pre_ping=True
    )
    conexion_db_exitosa = True
except Exception as e:
    st.error(f"Error de configuración de base de datos: {e}")
    conexion_db_exitosa = False
    engine = None

# 1. Verificar registro previo en el navegador (usando el ID_REUNION)
try:
    registro_previo = st_javascript(f"localStorage.getItem('mbeducacion_registro_{ID_REUNION}');")
except Exception as e:
    registro_previo = None
    st.warning("No se pudo verificar el registro previo en el navegador")

# 2. Consultar cuántos van registrados en la base de datos para este evento
conteo_actual = 0
if conexion_db_exitosa and engine:
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) FROM directorio_tratamiento 
                WHERE canal_autorizacion LIKE :filtro
            """), {"filtro": f"%{ID_REUNION}%"})
            conteo_actual = result.scalar()
    except Exception as e:
        st.warning(f"No se pudo consultar el conteo de registros: {e}")
        conteo_actual = 0

# DETERMINAR LINK DE DESTINO
if conteo_actual >= CUPO_MAXIMO:
    link_destino = LINK_YOUTUBE
    mensaje_cupo = "⚠️ ¡Sala de Zoom llena! Podrás ver la transmisión en vivo por YouTube."
else:
    link_destino = LINK_ZOOM
    mensaje_cupo = "✨ Tienes un cupo reservado en la sala de Zoom."

# --- VISTA PARA USUARIOS YA REGISTRADOS ---
if registro_previo == "true":
    st.title(NOMBRE_EVENTO)
    st.success("✨ ¡Bienvenido de nuevo! Ya te encuentras registrado al Webinar.")
    st.info("Haz clic en el botón de abajo para ingresar directamente a la transmisión.")
    st.info(mensaje_cupo)
    
    st.markdown(f"""
        <a href="{link_destino}" target="_blank" style="
            text-decoration: none; background-color: #2D8CFF; color: white;
            padding: 15px 25px; border-radius: 10px; font-weight: bold;
            display: inline-block; text-align: center; width: 100%;
        ">🚀 INGRESAR A LA TRANSMISIÓN</a>
    """, unsafe_allow_html=True)
    
    if st.button("No soy yo / Registrar nuevos datos"):
        st_javascript(f"localStorage.removeItem('mbeducacion_registro_{ID_REUNION}');")
        st.rerun()
    st.stop()

# --- FORMULARIO DE REGISTRO ---
st.title("Registro de Asistencia y Tratamiento de Datos")
st.subheader(f"Bienvenido al {NOMBRE_EVENTO}, MB Educación")

# Mostrar advertencia si no hay conexión a BD
if not conexion_db_exitosa:
    st.error("⚠️ Error de conexión con la base de datos. Por favor, contacta al administrador.")
    st.stop()

with st.form("registro_publico", clear_on_submit=True):
    nombre = st.text_input("Nombre Completo *")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        tipo_doc = st.selectbox(
            "Tipo de Documento *",
            ["C.C.", "NIT", "C.E.", "Pasaporte", "T.I.", "Otro"],
            index=0
        )
    with col2:
        doc_identidad = st.text_input("Número de Documento *")

    institucion = st.text_input("Institución Educativa / Empresa / Asociación *")
    rol_cargo = st.text_input("Cargo en la Institución Educativa / Empresa / Asociación *")
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

    st.caption("Al marcar la casilla, autoriza a MB Educación a utilizar sus datos según los términos expuestos anteriormente.")
    acepta = st.checkbox("He leído y autorizo el tratamiento de mis datos personales *")
    acepta_promos = st.checkbox("Acepto que MB Educación me envíe información de sus servicios o productos (Cursos y promociones)")    
    
    boton_registro = st.form_submit_button("REGISTRARME E INGRESAR A ZOOM")

# --- LÓGICA DE VALIDACIÓN ---
if boton_registro:
    # 1. Verificación estricta de campos obligatorios y casillas
    errores = []
    if not nombre: errores.append("Nombre Completo")
    if not doc_identidad: errores.append("Número de Documento")
    if not institucion: errores.append("Institución")
    if not rol_cargo: errores.append("Cargo")  # Este campo también parece obligatorio
    if not email: errores.append("Correo Electrónico")
    if not acepta: errores.append("Aceptación de Tratamiento de Datos (Casilla obligatoria)")

    if not errores:
        # SI TODO ESTÁ BIEN, PROCEDEMOS AL GUARDADO
        try:
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
                    "cnal": f"Registro Zoom - {ID_REUNION} - {time.strftime('%d/%m/%Y')}"
                })

            # SOLO SI EL GUARDADO ES EXITOSO, SE EJECUTA LA REDIRECCIÓN
            st.success("✅ ¡Registro exitoso! Guardando preferencia...")
            
            # Guardamos la marca en el navegador
            st_javascript(f"localStorage.setItem('mbeducacion_registro_{ID_REUNION}', 'true');")
            
            # Mostrar mensaje de cupo y redirección
            st.info(f"🔄 {mensaje_cupo}")
            st.info("Serás redirigido en unos segundos...")
            
            # Redirección con un mensaje claro
            time.sleep(3)
            st.markdown(f'<meta http-equiv="refresh" content="0; url={link_destino}">', unsafe_allow_html=True)
                        
        except Exception as e:
            st.error(f"❌ Error técnico al guardar en la base de datos: {e}")
            st.warning("Por favor, intenta nuevamente o contacta al administrador.")
    else:
        # SI HAY ERRORES, MOSTRAMOS ADVERTENCIA Y NO REDIRIGIMOS
        st.error("### ⚠️ No se puede completar el registro")
        st.write("Debes completar los siguientes puntos obligatorios:")
        for error in errores:
            st.write(f"- {error}")
        st.warning("Por favor, completa todos los campos obligatorios para poder acceder a la reunión.")
