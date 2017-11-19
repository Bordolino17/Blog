from flask import Flask,render_template
from flask import request,redirect,url_for
from flask import session as session_login
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base,Blog,User
import hashlib
import random, string
import datetime

def crear_semilla():
	return ''.join(random.choice(
			string.ascii_uppercase+string.digits) for x in range(32)) #crea el largo de la semilal de 32
			
def hashear(name,pw,semilla=None):
	if not semilla:
		semilla=crear_semilla()
	h=hashlib.sha256((name+pw+semilla).encode('utf-8')).hexdigest()
	return '%s,%s' % (semilla,h)

def validar_pw(name,password,h):
	semilla=h.split(',')[0]
	return h==hashear(name,password,semilla)

#def hashear(nombre,passw,semilla):
	#semilla=random(letras y numeros
	#devuelvo semilla y hash
	
#para dehashear paso nombre passw y con la semilla separada por , vuelvo a hashear 
error=""
app=Flask(__name__)

engine=create_engine("sqlite:///blog.db")
Base.metadata.bind=engine
DBSession=sessionmaker(bind=engine)
session=DBSession()

@app.route('/',methods=['GET','POST']) #blog.columna
def showMain():
	#activar=False
	user=""
	if "username" in session_login:
		user=session_login["username"]
	if request.method=='POST':
		if request.form.get('agregar'):
			return redirect(url_for('agregar'))
		elif request.form.get('eliminar'):
			id=request.form["id"]
			return redirect(url_for('eliminar',id=id))
		elif request.form.get('login'):
			return redirect(url_for("login"))
		elif request.form.get("editar"):
			id=request.form["id"]
			return redirect(url_for("editar",id=id))
	
	bloglist=session.query(Blog).all()
	
	
	return render_template('index2.html',bloglist=bloglist,user=user)
	
@app.route('/agregar',methods=["GET","POST"])
def agregar():
	user=""
	#codigo apra agregar base de datos
	if request.method=='POST':
		titulo=request.form["titulo"]
		contenido=request.form["message"]
		if "username" in session_login:
			user=session_login["username"]
		blog=Blog()
		blog.titulo=titulo
		blog.contenido=contenido
		blog.creador=user
		blog.fecha_creacion=datetime.datetime.now()
		session.add(blog)
		session.commit()
		return redirect(url_for("showMain"))

	return render_template('add.html')
	
@app.route('/eliminar',methods=["GET","POST"])
def eliminar():
	error=False
#codigo para eliminar
	if not "username" in session_login:
		return redirect(url_for("showMain"))
	id=request.args.get('id')
	res=session.query(Blog).filter_by(id=id).one()

	if request.method=="POST" :
		if (session_login["username"]==res.creador or session_login["username"]=="admin"):
			session.delete(res)
			session.commit()
			error=False
		else:
			error=True

	if request.method=="POST" and (session_login["username"]==res.creador or session_login["username"]=="admin") :
		session.delete(res)
		session.commit()
		error=True
		return redirect(url_for("showMain"))
	else:
		error=True


	return render_template('del.html',id=id,bloglist=res,error=error)

@app.route('/login',methods=["GET","POST"])
def login():
	error=""
	if request.method=="POST":
		if request.form.get("ingresar"):
			res=session.query(User).filter_by(username=request.form["usuario"]).first()
			
			if res and validar_pw(request.form["usuario"],request.form["contrasena"],res.password):
                                
				session_login["username"]=request.form["usuario"]
				return redirect(url_for("showMain"))
			else:
				error="usuario no registrado"
		elif request.form.get('registrarse'):
			return redirect(url_for('registrar'))
	
	return render_template('login.html',error=error)
	
	
@app.route("/registrarse",methods=["GET","POST"])
def registrar():
	if request.method=="POST":
		nuevousuario= User(
			username=request.form["usuario"],
			password=hashear(request.form["usuario"],request.form["pass"]),
			email=request.form["mail"])
		session.add(nuevousuario)
		session.commit()
		session_login['username']=request.form["usuario"]
		return redirect(url_for('showMain',user=session_login["username"]))
		
	
	return render_template('registrarse.html')
	
@app.route("/logout",methods=["GET","POST"])
def logout():
	del session_login["username"]
	return redirect(url_for("showMain"))

	
@app.route("/editar",methods=["GET","POST"])
def editar():
	if not "username" in session_login:
		return redirect(url_for("showMain"))
	id=request.args.get('id')
	res=session.query(Blog).filter_by(id=id).one()
	if request.method=="POST":
		if (session_login["username"]==res.creador or session_login["username"]=="admin"):
			res.titulo=request.form["titulo"]
			res.contenido=request.form["message"]
			session.commit()
			return redirect(url_for("showMain"))
		else:
			return redirect(url_for('showMain'))
	return render_template("editar.html",res=res)
	
if __name__ == '__main__':
	app.secret_key="secret key"
	app.debug=True
	app.run(host='0.0.0.0', port=8080)
