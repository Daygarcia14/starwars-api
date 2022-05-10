"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import requests
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
from datetime import timedelta
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY']=os.environ.get('FLASK_APP_KEY')
app.config["JWT_ACCESS_TOKEN_EXPIRES"]= timedelta(minutes=50)
jwt= JWTManager(app)
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

URL_BASE = "https://swapi.dev/api"
@app.route('/population/planets', methods=['POST'])
def handle_planets():
    response = requests.get(f"{URL_BASE}/{'planets'}/")
    response = response.json()
    all_results = []

    for result in response['results']:
        detail = requests.get(result['url'])
        detail = detail.json()
        all_results.append(detail)
    
    instances = []  

    for planet in all_results:
        instance = Planet.create(planet)
        instances.append(instance)
    return jsonify(list(map(lambda inst: inst.serialize(), instances))), 200
    

URL_BASE = "https://swapi.dev/api"
@app.route('/population/characters', methods=['POST'])
def handle_characters():
    response = requests.get(f"{URL_BASE}/{'people'}/")
    response = response.json()
    all_results = []

    for result in response['results']:
        detail = requests.get(result['url'])
        detail = detail.json()
        all_results.append(detail)
    
    instances = []  

    for character in all_results:
        instance = Character.create(character)
        instances.append(instance)
    return jsonify(list(map(lambda inst: inst.serialize(), instances))), 200
    
######### USERS ############
 
@app.route('/users', methods=['GET'])
@jwt_required()
def getUsers():
    users = User.query.all()
    request = list(map(lambda user:user.serialize(),users))    
    return jsonify(request), 200

@app.route('/users', methods=['POST'])
def createUser():
    body = request.get_json()
    if not body.get("email", "password", ):
        return jsonify({
            "msg":"Something happen, try again"
        }), 400
    user = User(email=body["email"], password=body["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify("New user has been created"),200

@app.route('/users', methods=["DELETE"])
@jwt_required()
def deleteUser():
    curent_user= get_jwt_identity()
    print(curent_user)
    user = User.query.get(curent_user)
    if user is None:
        return jsonify({
            "msg":"Something happen, try again"
        }), 400
    else:
        db.session.delete(user)
        db.session.commit()
        return jsonify("User has been deleted"), 200

@app.route("/register", methods=["POST"])
def register_user():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if email is None:
        return jsonify("Please provide a valid email."), 400
    if password is None:
        return jsonify("Please provide a valid password."), 400
    
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        return jsonify("User already exists."), 401
    else:
        newuser = User()
        newuser.email = email
        newuser.password = password

        db.session.add(newuser)
        db.session.commit()
        return jsonify({"msg": "User account was successfully created."}), 200

@app.route('/login', methods=["POST"])
def handle_login():
    email= request.json.get("email", None)
    password= request.json.get("password", None)
    if email is not None and password is not None:
        user = User.query.filter_by(email=email, password=password).one_or_none()
        if user is not None:
            create_token= create_access_token(identity=user.id)
            return jsonify({
                "token": create_token,
                "user_id": user.id,
                "email": user.email
            }), 200        
        else:
            return jsonify({
            "msg": "Not found"
            }), 404
    else:
        return jsonify({
        "msg": "something happen, try again"
        }), 400  

######### CHARACTERS ############

@app.route('/characters', methods=['GET'])
def getCharacter():
    characters = Character.query.all()
    request = list(map(lambda character:character.serialize(),characters))    
    return jsonify(request), 200

@app.route('/characters/<int:id>', methods=['GET'])
def getCharacter_id(id):
    character = Character.query.filter_by(id=id).first()
    if character  is None:
        return jsonify({
            "msg":"Something happen, try again"
        }), 400
    else:
        return jsonify(character), 200

@app.route('/characters', methods=['POST'])
def createCharacter():
    name = request.json.get("name", None)
    hair_color = request.json.get("hair_color", None)
    eye_color = request.json.get("eye_color", None)
    gender = request.json.get("gender", None)
    if name is None:
        return jsonify({"msg": "Introduce a valid name"}), 400
    if hair_color is None:
        return jsonify({"msg": "Introduce a valid hair color"}), 400
    if hair_color is None:
        return jsonify({"msg": "Introduce a valid eye color"}), 400
    if gender is None:
        return jsonify({"msg": "Introduce a valid eye color"}), 400
    
    character = Character.query.filter_by(name=name).first()
    if character:
        return jsonify({"msg": "Character already exists."}), 401
    else:
        newCharacter = Character()
        newCharacter.name = name
        newCharacter.hair_color = hair_color
        newCharacter.eye_color = eye_color
        newCharacter.gender = gender
        db.session.add(newCharacter)
        db.session.commit()
        return jsonify({"msg": "Character was successfully created."}),200


@app.route('/characters/<int:id>', methods=['DELETE'])
def deleteCharacter(id):
    character = Character.query.filter_by(id=id).first()
    if character is None:
        return "Not Found", 401
    else:
        db.session.delete(character)
        db.session.commit()
        return jsonify("Character has been deleted"),200

######### PLANETS ############

@app.route('/planets', methods=['GET'])
def getPlanets():
    planets = Planet.query.all()
    request = list(map(lambda planet:planet.serialize(),planets))    
    return jsonify(request), 200

@app.route('/planets/<int:id>', methods=['GET'])
def getPlanet_id(id):
    planet = Planet.query.filter_by(id=id).first()
    if planet is None:
        return jsonify({
            "msg":"Something happen, try again"
        }), 400
    else:
        return jsonify(planet), 200

@app.route('/planets', methods=['POST'])
def createPlanet():
    name = request.json.get("name", None)
    population = request.json.get("population", None)
    climate = request.json.get("climate", None)
    terrain = request.json.get("terrain", None)
    diameter = request.json.get("diameter", None)
    planet = Planet.query.filter_by(name=name).first()
    if planet:
        return jsonify({"msg": "Planet already exists."}), 401
    else:
        newPlanet = Planet()
        newPlanet.name = name
        newPlanet.population = population
        newPlanet.climate = climate
        newPlanet.terrain = terrain
        newPlanet.diameter = diameter
        db.session.add(newPlanet)
        db.session.commit()
        return jsonify({"msg": "Planet was successfully created."}),200

@app.route('/planets/<int:id>', methods=['DELETE'])
def deletePlanet(id):
    planet = Planet.query.filter_by(id=id).first()
    if planet is None:
        return "Not Found", 401
    else:
        db.session.delete(planet)
        db.session.commit()
        return jsonify("Planet has been deleted"),200

######### FAVORITES ############

@app.route('/users/favorites', methods=['GET'])
@jwt_required()
def getFavorite():
    user_id= get_jwt_identity()
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    favorite = list(map(lambda favorite:favorite.serialize(),favorites))   
    return jsonify(favorite), 200
    
@app.route('/favorites/character/<int:nature_id>', methods=['POST'])
@jwt_required()
def createFavorite(nature_id):
    body = request.json
    if nature_id is None:
        return jsonify("No valid character"), 400
    character = Favorite.query.filter_by(nature_id=nature_id, nature="character").first()
    if character is not None:
        return jsonify({"msg": "Character is already in Favorites"}), 400
    else:
        user_id= get_jwt_identity()
        favorite= Favorite(
            name = body["name"],
            nature = "character",
            nature_id = body["nature_id"],
            user_id = user_id
        )

        db.session.add(favorite)
        db.session.commit()
        return jsonify("New favorite has been added"), 200

@app.route('/favorites/character/<int:nature_id>', methods=['DELETE'])
@jwt_required()
def deleteFav(nature_id):
    if nature_id is None:
        return jsonify("Not valid character"),400
    user_id=get_jwt_identity()
    character = Favorite.query.filter_by(nature_id=nature_id, user_id=user_id, nature="character").first()
    if character is None:
        return jsonify("The character is not in Favorite"), 400
    else:
        db.session.delete(character)
        db.session.commit()
        return jsonify("Favorite has been deleted"),200

@app.route('/favorites/planet/<int:nature_id>', methods=['POST'])
@jwt_required()
def createFavoritePlanet(nature_id): 
    body = request.json
    if nature_id is None:
        return jsonify("No valid planet"), 400
    planet = Favorite.query.filter_by(nature_id=nature_id, nature="planet").first()
    if planet is not None:
        return jsonify({"msg": "Planet is already in Favorites"}), 400
    else:
        user_id= get_jwt_identity()
        favorite= Favorite(
            name = body["name"],
            nature = "planet",
            nature_id = body["nature_id"],
            user_id = user_id
        )

        db.session.add(favorite)
        db.session.commit()
        return jsonify("New favorite has been added"), 200

@app.route('/favorites/planet/<int:nature_id>', methods=['DELETE'])
@jwt_required()
def deleteFavPlanet(nature_id):
    if nature_id is None:
        return jsonify("Not valid planet"),400
    user_id = get_jwt_identity()
    planet = Favorite.query.filter_by(nature_id=nature_id, user_id=user_id, nature="planet").first()
    if planet is None:
        return jsonify("The planet is not in Favorite"), 400
    else:
        db.session.delete(planet)
        db.session.commit()
        return jsonify("Favorite has been deleted"),200

# this only runs if `$ python src/main.py` is executed

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
