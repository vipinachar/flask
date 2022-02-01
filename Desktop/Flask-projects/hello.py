import logging
from flask import Flask
from flask import jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column
from sqlalchemy import Integer 
from sqlalchemy import String 
from sqlalchemy import Float
import os
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token
from flask_mail import Mail
from flask_mail import Message


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
app.config['JWT_SECRET_KEY'] = "supersecretapi"
app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = "00423c59c94d66"
app.config['MAIL_PASSWORD'] = "3ef778c7660f4d"
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
mail = Mail(app)



@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database has been created successfully!')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database has been dropped successfully')

@app.cli.command('db_seed')
def db_seed():
    Mercury = Planet(
            planet_name='Mercury',
            planet_type='Class D',
            home_star='Sol',
            mass=3.258e23,
            radius=1516,
            distance=35.98e6,        
    )

    Earth = Planet(
            planet_name='Earth',
            planet_type='Class M',
            home_star='Sol',
            mass=5.972e24,
            radius=3959,
            distance=92.96e6,        
    )


    Venus = Planet(
            planet_name='Venus',
            planet_type='Class D',
            home_star='Sol',
            mass=4.867e24,
            radius=3760,
            distance=67.24e6,        
    )


    db.session.add(Mercury)
    db.session.add(Venus)
    db.session.add(Earth)

    test_user = User(
        first_name='William',
        last_name='Hershal',
        email='William1998@gmail.com',
        password='P@ssw0rd'
    )

    db.session.add(test_user)
    db.session.commit()
    print('Database seed completed successfully')

@app.route("/")
def hello_world():
    return "Hello world"


@app.route("/super_simple")
def super_simple():
    return jsonify(message="Hello from planetary"), 200


@app.route("/not_found")
def not_found():
    return jsonify(message="The requested resource couldn't be found!"), 400


@app.route('/age_filter')
def age_filter():
    name = request.args.get('name')
    age = request.args.get('age', type=int)
    if age < 18:
        return jsonify(message=f"Sorry {name} , you are not old enough!"), 401
    else:
        return jsonify(message=f"Welcome {name} , you are old enough!"), 200


@app.route('/url_variables/<string:name>/<int:age>')
def url_varibales(name:str, age:int):
    if age < 18:
        return jsonify(message=f"Sorry {name} , you are not old enough!"), 401
    else:
        return jsonify(message=f"Welcome {name} , you are old enough!"), 200


@app.route('/planets', methods=['GET'])
def planets():
    planets_list = Planet.query.all()
    result = planets_schema.dump(planets_list)
    return jsonify(result)    


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='Email already exists'), 409
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        
        user = User(first_name=first_name, last_name=last_name, email=email, password=password)

        db.session.add(user)
        db.session.commit()
        
        return jsonify(message="User created successfully."), 201


@app.route('/login', methods=['POST'])
def login():
    
    email = request.json['email']
    password = request.json['password']
    
    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login succeeded!", access_token=access_token), 200
    else:
        return jsonify(message="Unauthorized user"), 401


@app.route('/forgot_password/<string:email>')
def forgot_password(email:str):

    user = User.query.filter_by(email=email).first() 
    if user:
        print('hi')
        msg = Message("you planetary API password is "+user.password,
        sender="admin@planetary-api.com",
        recipients=[email],
        )
        mail.send(msg)
        return jsonify(message="Password sent to "+email)
    else:
        return jsonify(message="Email doesn't exist!"), 400

@app.route('/planet/<int:planet_id>', methods=['GET'])
def planet_details(planet_id):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    print('hi')
    if planet:
        result = planet_schema.dump(planet)
        return jsonify(result)
    else:
        return jsonify(message="No record found"), 400
# DataBase Models

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

class Planet(db.Model):
    __tablename__ = 'planets'
    planet_id = Column(Integer, primary_key=True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id','first_name','last_name','email', 'passsword')
     

class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planet_id','planet_name','planet_type','home_star','mass','radius','distance')
        

user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)



if __name__ == "__main__":
    app.run(debug=True)