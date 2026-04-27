from flask import Flask, render_template, request, redirect, url_for,session,flash
from tareas import GestorTareas

app = Flask(__name__)
app.secret_key = 'OODA'
gestor = GestorTareas()

gestor.crear_usuario("David","davidelguapo123@gmail.com","password123")

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        contraseña = request.form.get("contraseña")
        confirmarcontra = request.form.get("confirmarcontra")

        if contraseña != confirmarcontra:
            flash("Las contraseñas no coinciden", "error")
            return render_template("registro.html")

        usuario_id = gestor.crear_usuario(nombre, email, contraseña)

        if usuario_id:
            flash('Registro exitoso. Por favor, inicia sesión.', 'success')
            return redirect(url_for('login'))
        else:
            flash('El correo ya está registrado o hubo un error.', 'danger')
            
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        contraseña = request.form.get('contraseña')

        usuario = gestor.validar_credenciales(email, contraseña)

        if usuario:
            session['logueado'] = True
            session['usuario_id'] = usuario['_id']
            session['nombre'] = usuario['nombre']
            flash(f"¡Bienvenido de nuevo, {usuario['nombre']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Correo o contraseña incorrectos", "danger")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() 
    flash("Has cerrado sesión correctamente", "info")
    return redirect(url_for('login'))

@app.route('/editar_usuario', methods=['GET', 'POST'])
def editar_usuario():
    usuario= gestor.obtener_usuario(session['usuario_id'])
    if request.method == 'POST':
        nuevo_nombre = request.form.get('nombre')
        nueva_email = request.form.get('email')
        
        if nuevo_nombre:
            usuario['nombre'] = nuevo_nombre
        if nueva_email:
            usuario['email'] = nueva_email
        
        gestor.actualizar_usuario(session['usuario_id'], usuario)
        session['nombre'] = usuario['nombre']
        session['email'] = usuario['email']
        flash('Perfil actualizado correctamente', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('editar.html', usuario=usuario)

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
        gestor.actualizar_estado_tarea(tarea_id, "completada")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)