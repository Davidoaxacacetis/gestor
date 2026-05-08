from flask import Flask, render_template, request, redirect, url_for, session, flash
from tareas import GestorTareas
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'Ruby'
gestor = GestorTareas()


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        contraseña = request.form.get("contraseña")
        confirmarcontra = request.form.get("confirmarcontra")

        if contraseña != confirmarcontra:
            flash("Las contraseñas no coinciden", "danger")
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

@app.route('/recuperar_password', methods=['GET', 'POST'])
def recuperar_password():
    return render_template('recuperar.html')


@app.route('/editar_usuario', methods=['GET', 'POST'])
def editar_usuario():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    
    if request.method == 'POST':
        datos_nuevos = {
            'nombre': request.form.get('nombre'),
            'email': request.form.get('email')
        }
        
        datos_nuevos = {k: v for k, v in datos_nuevos.items() if v}

        if gestor.actualizar_usuario(usuario_id, datos_nuevos):
            if 'nombre' in datos_nuevos: session['nombre'] = datos_nuevos['nombre']
            if 'email' in datos_nuevos: session['email'] = datos_nuevos['email']
            
            flash('Perfil actualizado correctamente', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('No se realizaron cambios o el email ya existe', 'warning')

    usuario = gestor.obtener_usuario(usuario_id)
    return render_template('editar.html', usuario=usuario)

@app.route('/logout')
def logout():
    session.clear() 
    flash("Has cerrado sesión correctamente", "info")
    return redirect(url_for('login'))

@app.route('/perfil')
def perfil():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario = gestor.obtener_usuario(session['usuario_id'])
    return render_template('perfil.html', usuario=usuario)


@app.route('/')
def dashboard():
    if 'usuario_id' not in session:
        flash('Por favor, inicia sesión para acceder.', 'warning')
        return redirect(url_for('login'))
    
    todas = gestor.obtener_tareas_usuario(session['usuario_id'])
    
    pendientes = [t for t in todas if t['estado'] in ['pendiente', 'en_progreso']]
    completadas = [t for t in todas if t['estado'] == 'completada']
    canceladas = [t for t in todas if t['estado'] == 'cancelada']
    
    return render_template('dashboard.html', 
                            nombre=session['nombre'], 
                            pendientes=pendientes, 
                            completadas=completadas,
                            canceladas=canceladas)

@app.route('/crear_tarea', methods=['POST'])
def crear_tarea():
    if 'usuario_id' in session:
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        gestor.crear_tarea(session['usuario_id'], titulo, descripcion)
        flash("Tarea creada con éxito", "success")
    return redirect(url_for('dashboard'))

@app.route('/empezar_tarea/<tarea_id>')
def empezar_tarea(tarea_id):
    if 'usuario_id' in session:
        gestor.actualizar_tarea(tarea_id, {"estado": "en_progreso"})
    return redirect(url_for('dashboard'))

@app.route('/completar_tarea/<tarea_id>')
def completar_tarea(tarea_id):
    if 'usuario_id' in session:
        gestor.actualizar_tarea(tarea_id, {"estado": "completada"})
        flash("¡Tarea completada! Buen trabajo.", "success")
    return redirect(url_for('dashboard'))

@app.route('/cancelar_tarea/<tarea_id>', methods=['POST'])
def cancelar_tarea(tarea_id):
    if 'usuario_id' in session:
        motivo = request.form.get('motivo')
        datos = {
            "estado": "cancelada",
            "motivo_cancelacion": motivo
        }
        gestor.actualizar_tarea(tarea_id, datos)
        flash("Tarea cancelada.", "info")
    return redirect(url_for('dashboard'))

@app.route('/reabrir_tarea/<tarea_id>')
def reabrir_tarea(tarea_id):
    if 'usuario_id' in session:
        datos = {
            "estado": "pendiente",
            "motivo_cancelacion": None 
        }
        gestor.actualizar_tarea(tarea_id, datos)
        flash("Tarea movida a pendientes.", "info")
    return redirect(url_for('dashboard'))

@app.route('/editar_tarea/<tarea_id>', methods=['POST'])
def editar_tarea(tarea_id):
    if 'usuario_id' in session:
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        
        datos_actualizados = {
            "titulo": titulo,
            "descripcion": descripcion
        }
        
        gestor.actualizar_tarea(tarea_id, datos_actualizados)
        flash("Tarea actualizada correctamente", "success")
        
    return redirect(url_for('dashboard'))

@app.route('/eliminar_tarea/<tarea_id>')
def eliminar_tarea(tarea_id):
    if 'usuario_id' in session:
        gestor.eliminar_tarea(tarea_id)
        flash("La tarea ha sido eliminada", "danger")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)