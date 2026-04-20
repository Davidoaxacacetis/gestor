from flask import Flask, render_template, request, redirect, url_for,session,flash
from tareas import GestorTareas

app = Flask(__name__)
app.secret_key = 'OODA'
gestor = GestorTareas()

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        contraseña = request.form.get("contraseña")
        confirmarcontra = request.form.get("confirmarcontra")

        if contraseña != confirmarcontra:
            flash("Las contraseñas no coinciden", "error")
            return render_template("registro.html", **request.form)
        else:
            usuario_id = gestor.crear_usuario(contraseña, email)

        if usuario_id:
            flash('Registro exitoso. Por favor, inicia sesión.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Error al registrar. Intenta nuevamente.', 'danger')
            
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        usuario = gestor.obtener_usuario(password, email)

        if usuario:
            session['usuario_id'] = str(usuario['_id'])
            session['nombre'] = usuario['nombre']
            session["logueado"] = True 
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas. Intenta nuevamente.', 'danger')

    return render_template('login.html')

@app.route('/recuperar_password', methods=['GET', 'POST'])
def recuperar_password():
    return render_template('recuperar.html')

@app.route('/')
def dashboard():
    
    if 'usuario_id' not in session:
        flash('Por favor, inicia sesión para acceder al dashboard.', 'warning')
        return redirect(url_for('login'))
    
    tareas= gestor.obtener_tareas_usuario(session['usuario_id'])
    
    pendientes=[t for t in tareas if t ['estado'] != 'completada']
    completadas=[t for t in tareas if t ['estado'] == 'completada']
    
    return render_template('dashboard.html', nombre=session['nombre'], pendientes=pendientes, completadas=completadas)

@app.route('/crear_tarea', methods=['POST'])
def crear_tarea():
    if 'usuario_id'  in session:
        
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        gestor.crear_tarea(session['usuario_id'], titulo, descripcion)
    return redirect(url_for('dashboard'))

@app.route('/completar_tarea/<tarea_id>')
def completar_tarea(tarea_id):
    if 'usuario_id' in session:
        gestor.completar_tarea(tarea_id,"completada")
    return redirect(url_for('dashboard'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)