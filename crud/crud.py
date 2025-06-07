from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import os, logging
from functools import wraps
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash
from cryptography.fernet import Fernet
import paho.mqtt.client as mqtt
import ssl, certifi

logging.basicConfig(format='%(asctime)s - CRUD - %(levelname)s - %(message)s', level=logging.INFO)

app = Flask(__name__)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

app.secret_key = os.environ["FLASK_SECRET_KEY"]
app.config["MYSQL_USER"] = os.environ["MYSQL_USER"]
app.config["MYSQL_PASSWORD"] = os.environ["MYSQL_PASSWORD"]
app.config["MYSQL_DB"] = os.environ["MYSQL_DB"]
app.config["MYSQL_HOST"] = os.environ["MYSQL_HOST"]
app.config['PERMANENT_SESSION_LIFETIME']=180
mysql = MySQL(app)

# rutas

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    """Registrar usuario"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("usuario"):
            return "El campo usuario es obligatorio."

        # Ensure password was submitted
        elif not request.form.get("password"):
            return "El campo usuario es obligatorio."

        passhash=generate_password_hash(request.form.get("password"), method='scrypt', salt_length=16)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios (usuario, hash) VALUES (%s,%s)", (request.form.get("usuario"), passhash[17:]))
        if mysql.connection.affected_rows():
            flash('Se agregó un usuario')  # usa sesión
            logging.info("Se agregó un usuario")
        mysql.connection.commit()
        return redirect(url_for('index'))

    return render_template('registrar.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("usuario"):
            return "El campo usuario es obligatorio."
        # Ensure password was submitted
        elif not request.form.get("password"):
            return "El campo usuario es obligatorio."

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE usuario LIKE %s", (request.form.get("usuario"),))
        rows=cur.fetchone()
        if(rows):
            if (check_password_hash('scrypt:32768:8:1$' + rows[2],request.form.get("password"))):
                session.permanent = True
                session["user_id"]=request.form.get("usuario")
                logging.info("se autenticó correctamente")
                return redirect(url_for('index'))
            else:
                flash('Usuario o contraseña incorrecto')
                return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/')
@require_login
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM nodos")
    datos = cur.fetchall()
    cur.close()
    return render_template('index.html', nodos = datos)


@app.route('/add_nodo', methods=['POST'])
@require_login
def add_nodo():
    if request.method == 'POST':
        nodo = request.form['nodo']
        servidor = request.form['servidor']
        mqtt_usr = request.form['mqtt_usr']
        mqtt_pass = request.form['mqtt_pass']
        mqtt_puerto = request.form['mqtt_puerto']

        # Cargar la clave Fernet desde el env
        fernet_key = os.environ["FERNET_KEY"]
        # Crear instancia de Fernet
        fernet = Fernet(fernet_key.encode())
        # Cifrar la contraseña
        encrypted_pass = fernet.encrypt(mqtt_pass.encode()).decode()

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO nodos (nodo, servidor, mqtt_usr, mqtt_pass, mqtt_puerto)
            VALUES (%s, %s, %s, %s, %s)
        """, (nodo, servidor, mqtt_usr, encrypted_pass, mqtt_puerto))

        if mysql.connection.affected_rows():
            flash('Se agregó un nodo')
            logging.info("Se agregó un nodo")
            mysql.connection.commit()
    return redirect(url_for('index'))


@app.route('/borrar_nodo/<string:id>', methods=['GET'])
@require_login
def borrar_nodo(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM nodos WHERE id = %s', (id,))
    if mysql.connection.affected_rows():
        flash('Se eliminó un nodo')
        logging.info("Se eliminó un nodo")
        mysql.connection.commit()
    return redirect(url_for('index'))


@app.route('/editar_nodo/<id>', methods=['GET'])
@require_login
def conseguir_nodo(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM nodos WHERE id = %s', (id,))
    datos = cur.fetchone()
    logging.info(datos)
    return render_template('editar-nodo.html', nodo=datos)

@app.route('/actualizar_nodo/<id>', methods=['POST'])
@require_login
def actualizar_nodo(id):
    if request.method == 'POST':
        nodo = request.form['nodo']
        servidor = request.form['servidor']
        mqtt_usr = request.form['mqtt_usr']
        mqtt_pass = request.form['mqtt_pass']
        mqtt_puerto = request.form['mqtt_puerto']

        # Cargar la clave Fernet desde el env
        fernet_key = os.environ["FERNET_KEY"]
        # Crear instancia de Fernet
        fernet = Fernet(fernet_key.encode())
        # Cifrar la contraseña
        encrypted_pass = fernet.encrypt(mqtt_pass.encode()).decode()

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE nodos
            SET nodo=%s, servidor=%s, mqtt_usr=%s, mqtt_pass=%s, mqtt_puerto=%s
            WHERE id=%s
        """, (nodo, servidor, mqtt_usr, encrypted_pass, mqtt_puerto, id))
    if mysql.connection.affected_rows():
        flash('Se actualizó el nodo')
        logging.info("Se actualizó el nodo")
        mysql.connection.commit()
    return redirect(url_for('index'))


@app.route("/logout")
@require_login
def logout():
    session.clear()
    logging.info("el usuario {} cerró su sesión".format(session.get("user_id")))
    return redirect(url_for('index'))


#Maneja la conexión y la publicación hacia el servidor MQTT
@app.route('/publicar', methods=['GET', 'POST'])
@require_login
def publicar():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nodo FROM nodos")
    nodos = cur.fetchall()

    if request.method == 'POST':
        nodo_id = request.form['nodo']
        accion = request.form['accion']
        #Procesamos el tópico por si viene con espacios o una barra al final
        topic_base = request.form.get('topic_base', '').strip().rstrip('/')
        topic_base = topic_base.replace(" ", "_")

        cur.execute("SELECT * FROM nodos WHERE id = %s", (nodo_id,))
        nodo_data = cur.fetchone()

        if nodo_data:
            servidor = nodo_data[2]
            usuario = nodo_data[3]
            encrypted_pass = nodo_data[4]
            puerto = nodo_data[5]

            # Desencriptar contraseña
            fernet_key = os.environ["FERNET_KEY"]
            fernet = Fernet(fernet_key.encode())
            mqtt_pass = fernet.decrypt(encrypted_pass.encode()).decode()

            tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            tls_context.verify_mode = ssl.CERT_REQUIRED
            tls_context.check_hostname = True
            tls_context.load_default_certs()

            client = mqtt.Client()
            client.tls_set_context(tls_context)
            if usuario and mqtt_pass:
                client.username_pw_set(usuario, mqtt_pass)
            client.connect(servidor, int(puerto), 60)

            if accion == 'destello':
                topic = f"{topic_base}/destello" if topic_base else "Default/destello"
                client.publish(topic, "destello")
                flash(f"Comando 'destello' enviado al tópico '{topic}'")

            elif accion == 'setpoint':
                setpoint = request.form.get("setpoint")
                if setpoint and setpoint.isdigit():
                    topic = f"{topic_base}/setpoint" if topic_base else "Default/setpoint"
                    client.publish(topic, setpoint)
                    flash(f"Setpoint enviado al tópico '{topic}': {setpoint}")
                else:
                    flash("Setpoint inválido.", "danger")

            client.disconnect()
        else:
            flash("Nodo no encontrado.", "danger")
        
        return redirect(url_for('publicar', selected_id=nodo_id))

    selected_id = request.args.get('selected_id', type=int)
    return render_template('publicar.html', nodos=nodos, selected_id=selected_id)
