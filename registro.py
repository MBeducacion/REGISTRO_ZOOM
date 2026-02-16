import streamlit as st
from sqlalchemy import text
import time
import os
from sqlalchemy import create_engine
from sqlalchemy import create_engine, text
import pandas as pd

# --- Al inicio, después de los imports ---
from streamlit_javascript import st_javascript

# Intentamos leer una marca en el almacenamiento local del navegador (LocalStorage)
# Esto sobrevive aunque cierren la pestaña o apaguen el PC
registro_previo = st_javascript("localStorage.getItem('mbeducacion_registro');")

if registro_previo == "true":
    st.success("✨ ¡Bienvenido de nuevo! Ya te encuentras registrado en el Curso Sincronico Reforma Raboral para Instituciones Educativas Privadas .")
    st.info("Haz clic en el botón de abajo para ingresar directamente a la sala de Zoom.")
    
    link_zoom = "https://us06web.zoom.us/j/83795391348?pwd=blBqaiYliv3OamaJJGv0SPBYMcoNVa.1"
    
    # Usamos un link real estilizado como botón para evitar bloqueos del navegador
    st.markdown(f"""
        <a href="{link_zoom}" target="_blank" style="
            text-decoration: none;
            background-color: #2D8CFF;
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            font-weight: bold;
            display: inline-block;
            text-align: center;
            width: 100%;
        ">🚀 INGRESAR A LA REUNIÓN DE ZOOM</a>
    """, unsafe_allow_html=True)
    
    if st.button("No soy yo / Registrar nuevos datos"):
        st_javascript("localStorage.removeItem('mbeducacion_registro');")
        st.rerun()
    st.stop()
# 1. Cargar credenciales desde los Secrets de Streamlit
creds = st.secrets["db_credentials"]
DB_USER = creds["user"]
DB_PASS = creds["pass"]
DB_HOST = creds["host"]
DB_NAME = creds["name"]

# 2. Crear el motor de conexión
# Agregamos pool_pre_ping para que la conexión no se caiga durante el evento
engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}",
    pool_pre_ping=True
)

# from tu_archivo_principal import engine 

st.title("Registro de Asistencia y Tratamiento de Datos")
st.subheader("Bienvenido al Curso Sincronico Reforma Raboral para Instituciones Educativas Privadas MB Educación")

with st.form("registro_publico", clear_on_submit=True):
    nombre = st.text_input("Nombre Completo *")
    # --- NUEVA SECCIÓN: TIPO Y NÚMERO DE DOCUMENTO ---
    col1, col2 = st.columns([1, 2]) # Dividimos en dos columnas para que se vea mejor
    
    with col1:
        tipo_doc = st.selectbox(
            "Tipo de Documento *",
            ["C.C.", "NIT", "C.E.", "Pasaporte", "T.I.", "Otro"],
            index=0 # Por defecto selecciona C.C.
        )
        
    with col2:
        doc_identidad = st.text_input("Número de Documento *")

    institucion = st.text_input("Institución Educativa /Empresa /Asociacion *")
    rol_cargo = st.text_input(" Cargo en la Institución Educativa /Empresa /Asociacion*")
    email = st.text_input("Correo Electrónico")
    
    st.markdown("---")
    st.write("🔒 **Política de Tratamiento de Datos**")
    # --- MÉTODO 2: VENTANA DESPLEGABLE ---
    with st.expander("Leer Política completa de Tratamiento de Datos (Habeas Data)"):
        st.markdown("""
        ### MB EDUCACIÓN - AUTORIZACIÓN PARA EL TRATAMIENTO DE DATOS PERSONALES
        
        De conformidad con la legislación legal vigente y la Política de Tratamiento de Datos Personales de MB Educación, el tratamiento de los datos que se reportan en este Formulario se regirá por las siguientes condiciones:
        a) Yo, al diligenciar este Formulario, concedo autorización previa, expresa e informada a MB Educación, para el tratamiento de los datos que suministro, sabiendo que he sido informado que la finalidad de dichos datos es adquirir un producto o solicitar un servicio que ella ofrece ahora o en el futuro, de tal manera que puedan tramitar mi solicitud adecuadamente, contactarme en caso de que se requiera y adelantar todas las acciones para el logro del particular.
        b) Conozco y acepto que esta información será tratada de acuerdo con la Política de Tratamiento de Datos Personales de MB Educación disponible en su página Web, que declaro haber leído y conocer, en especial en lo referente a mis derechos y a los procedimientos con que la Entidad cuenta, para hacerlos efectivos ante sus autoridades.
        c) Se que los siguientes son los derechos básicos que tengo como titular de los datos que se han diligenciado en este Formulario: 1) Todos los datos registrados en este Formulario sólo serán empleados por MB Educación para cumplir la finalidad expuesta en el punto (a) del presente Aviso; 2) En cualquier momento, puedo solicitar una consulta de la información con que MB Educación cuenta sobre mí, dirigiéndome al Oficial de Protección de Datos Personales de la Entidad; 3) MB Educación velará por la confidencialidad y privacidad de los datos personales de los titulares que están siendo reportados, según las disposiciones legales vigentes; 4) En cualquier momento puedo solicitar una prueba de esta autorización.
        d) El Oficial de Protección de Datos Personales de la Entidad, ante quien puedo ejercer mis derechos, de forma gratuita, lo contactar en la siguiente dirección electrónica: usodedatos@mbeducacion.com.co 

        """)

    st.caption("Al marcar la casilla, autoriza a MB Educación a utilizar sus datos según los términos expuestos anteriormente.")
    acepta = st.checkbox("He leído y autorizo el tratamiento de mis datos personales")
    acepta_promos = st.checkbox("Acepto que MB Educación me envíe información de sus servicios o productos (Cursos y promociones)")    
    
    boton_registro = st.form_submit_button("REGISTRARME E INGRESAR A ZOOM")

# --- LÓGICA DE VALIDACIÓN ---
if boton_registro:
    # 1. Verificación estricta de campos obligatorios y casillas
    errores = []
    if not nombre: errores.append("Nombre Completo")
    if not doc_identidad: errores.append("Número de Documento")
    if not institucion: errores.append("Institución")
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
                    "tdoc": tipo_doc,    # <--- Guardamos el tipo (C.C., C.E., etc.)
                    "doc": doc_identidad,                    
                    "inst": institucion, 
                    "mail": email,
                    "rol": rol_cargo,
                    "hab": 1,
                    "env_info": 1 if acepta_promos else 0,
                    "cnal": "Registro Zoom, Curso Reforma Tributria" + time.strftime("%d/%m/%Y"),
                    
                })

           # SOLO SI EL GUARDADO ES EXITOSO, SE EJECUTA LA REDIRECCIÓN
            st.success("¡Registro exitoso! Guardando preferencia...")
            
            # Guardamos la marca en el navegador
            st_javascript("localStorage.setItem('mbeducacion_registro', 'true');")
            
            st.balloons()
            
            # Link de Zoom
            link_zoom = "https://us04web.zoom.us/j/75494309875?pwd=OOGKbP8tHZrZa6rKjoxYbDsP11FSPg.1"
            
            # Redirección con un mensaje claro
            st.info("Redirigiendo a Zoom en 2 segundos... Si no carga, haz clic en el botón de arriba.")
            time.sleep(2)
            st.markdown(f'<meta http-equiv="refresh" content="0; url={link_zoom}">', unsafe_allow_html=True)
                        
        except Exception as e:
            st.error(f"Error técnico al guardar: {e}")
    else:
        # SI HAY ERRORES, MOSTRAMOS ADVERTENCIA Y NO REDIRIGIMOS
        st.error("### ⚠️ No se puede ingresar")
        st.write("Debes completar los siguientes puntos obligatorios:")
        for error in errores:
            st.write(f"- {error}")
        st.warning("Por favor, marca la casilla de aceptación y completa tus datos para poder acceder a la reunión.")








