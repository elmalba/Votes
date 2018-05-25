from flask import Flask, request,redirect
from flask_restful import Resource, Api
import random 
app = Flask(__name__)
api = Api(app)

todos = {}


from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost/votaciones"
db = SQLAlchemy(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


class Votes(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	hash_id   = db.Column(db.Text, unique=True)
	opcion = db.Column(db.Text)
	code   = db.Column(db.Text)
	ip        = db.Column(db.Text)
	timestamp  = db.Column(db.DateTime)

class Available(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	hash_id   = db.Column(db.Text)
	token     = db.Column(db.Text,unique=True)
	timestamp = db.Column(db.DateTime)



from base64 import b64encode
def code(vote,token):

	token=vote
	fecha = vote.timestamp

	


def EjecutarVoto(hash_id,token,opcion):
	user = Available.query.filter_by(hash_id=hash_id,token=token).first()
	if user != None:
		vote = Votes.query.filter_by(hash_id=hash_id).first()
		if vote == None:
			vote=Votes()
			vote.hash_id=hash_id
			vote.opcion=opcion
			vote.timestamp=datetime.now()
			vote.ip=request.headers.get('cf-connecting-ip')
			vote.code=str(random.getrandbits(36))
			db.session.add(vote)
			db.session.commit()
			notification(hash_id,token,vote.code)

			return {'message':'Voto emitido validamente','codigo':vote.code}
		return {'message':'Tu voto ya fue emitido','codigo':vote.code}

	return {'message':'No intentes hacer algo que no puedes hacer'}



class Votar(Resource):
	def post(self):
		hash_id=  str(request.json['hash_id'] )
		opcion =  str(request.json['opcion']  )
		token  =  str(request.json['token']  )
		print opcion
		accept1 = False
		accept2 = True
		if len(hash_id)==24:
			accept1 = True
		if opcion  == "Toma":
			accept2 = True
		elif opcion =="Paro":
			accept2 = True
		elif opcion =="No":
			accept2= True
		elif opcion =="Blanco":
			accept2= True
		elif opcion =="Nulo":
			accept2= True
		if accept1 and accept1:
			print "ACA2"
			return  EjecutarVoto(hash_id,token,opcion)
		print "aca"

		return {'message':'No intentes hacer algo que no puedes hacer'}


class Register(Resource):
    def post(self):
		try:
			print request.form
			hash_id= request.form['hash_id']
			token = request.form['token']
			print hash_id
			Ava =Available()
			Ava.hash_id=hash_id
			Ava.timestamp=datetime.now()
			Ava.token=token
			db.session.add(Ava)
			db.session.commit()
			return {'message':'ok'}
		except:
			return {'message':'error'}

import requests

import threading

def notification(hash_id,token,scode):
	threads = list()
	t = threading.Thread(target=notification_url, args=(hash_id,token,scode,))
	threads.append(t)
	t.start()

def notification_url(hash_id,token,scode):


	url = "https://api.udpcursos.com/Register_vote"
	payload = "hash="+hash_id+"&token="+token+"&code="+scode
	headers = {
	    'cache-control': "no-cache",
	    'postman-token': "ed6c75c9-98fd-eea4-b8fe-456a13f3f547",
	    'content-type': "application/x-www-form-urlencoded"
	    }

	response = requests.request("POST", url, data=payload, headers=headers)

	print(response.text)


api.add_resource(Votar, '/Votar')
api.add_resource(Register, '/Register_udpCursos')
@app.errorhandler(404)
def page_not_found(e):
    return redirect("https://udpcursos.com")

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=80)
