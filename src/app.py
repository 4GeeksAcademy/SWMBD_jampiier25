"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Vehicle, Favorite, FavoriteType
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Usuario simulado (no hay login aún)
CURRENT_USER_ID = 1

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#usuarios
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    serialized_users = [user.serialize() for user in users]
    return jsonify(serialized_users), 200

#agregar usuario
@app.route('/users', methods=['POST'])
def create_user():
    # Obtenemos los datos del cuerpo de la solicitud
    data = request.get_json()

    # Validamos los datos
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    is_active = data.get('is_active', True)

    if not username or not email or not password:
        return jsonify({"msg": "Faltan campos requeridos"}), 400

    # Verificamos si el usuario ya existe
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"msg": "El usuario ya existe"}), 409

    # Creamos el nuevo usuario
    new_user = User(username=username, email=email, password=password,is_active=is_active,
        first_name=first_name,
        last_name=last_name, )
    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.serialize()), 201


#usersfavorites
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    favorites = Favorite.query.filter_by(user_id=CURRENT_USER_ID).all()
    serialized_favorites = [fav.serialize() for fav in favorites]
    return jsonify(serialized_favorites), 200

#people
@app.route('/people', methods=['GET']) 
def get_people():
    characters = Character.query.all()
    serialized_characters = [char.serialize() for char in characters]
    return jsonify(serialized_characters), 200

@app.route("/people/<int:id>", methods=['GET'])
def get_single_character(id):
    character = Character.query.get(id)
    if not character:
        return jsonify({"msg": "Character not found"}), 404
    return jsonify(character.serialize()), 200

# Agregar personaje (POST)
@app.route('/people', methods=['POST'])
def create_character():
    data = request.get_json()
    name = data.get('name')
    gender = data.get('gender')
    birth_year = data.get('birth_year')
    
    if not name:
        return jsonify({"msg": "Name is required"}), 400

    character = Character(name=name, gender=gender, birth_year=birth_year)
    db.session.add(character)
    db.session.commit()
    return jsonify(character.serialize()), 201

# Modificar personaje (PUT)
@app.route('/people/<int:id>', methods=['PUT'])
def update_character(id):
    character = Character.query.get(id)
    if not character:
        return jsonify({"msg": "Character not found"}), 404

    data = request.get_json()
    character.name = data.get('name', character.name)
    character.gender = data.get('gender', character.gender)
    character.birth_year = data.get('birth_year', character.birth_year)

    db.session.commit()
    return jsonify(character.serialize()), 200

# Eliminar personaje (DELETE)
@app.route('/people/<int:id>', methods=['DELETE'])
def delete_character(id):
    character = Character.query.get(id)
    if not character:
        return jsonify({"msg": "Character not found"}), 404

    db.session.delete(character)
    db.session.commit()
    return jsonify({"msg": "Character deleted"}), 200

#planets
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    serialized_planets = [planet.serialize() for planet in planets]
    return jsonify(serialized_planets), 200

@app.route("/planets/<int:id>", methods=['GET'])
def get_single_planet(id):
    planet = Planet.query.get(id)
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

# Crear un nuevo planeta (POST)
@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.get_json()
    name = data.get('name')
    climate = data.get('climate')
    terrain = data.get('terrain')

    if not name:
        return jsonify({"msg": "Name is required"}), 400

    planet = Planet(name=name, climate=climate, terrain=terrain)
    db.session.add(planet)
    db.session.commit()
    return jsonify(planet.serialize()), 201

# Modificar planeta (PUT)
@app.route('/planets/<int:id>', methods=['PUT'])
def update_planet(id):
    planet = Planet.query.get(id)
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404

    data = request.get_json()
    planet.name = data.get('name', planet.name)
    planet.climate = data.get('climate', planet.climate)
    planet.terrain = data.get('terrain', planet.terrain)

    db.session.commit()
    return jsonify(planet.serialize()), 200

# Eliminar planeta (DELETE)
@app.route('/planets/<int:id>', methods=['DELETE'])
def delete_planet(id):
    planet = Planet.query.get(id)
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404

    db.session.delete(planet)
    db.session.commit()
    return jsonify({"msg": "Planet deleted"}), 200

#vehicles
@app.route('/vehicles', methods=['GET'])
def get_vehicles():
    vehicles = Vehicle.query.all()
    serialized_vehicles = [vehicle.serialize() for vehicle in vehicles]
    return jsonify(serialized_vehicles), 200

@app.route("/vehicles/<int:id>", methods=['GET'])
def get_single_vehicle(id):
    vehicle = Vehicle.query.get(id)
    if not vehicle:
        return jsonify({"msg": "Vehicle not found"}), 404
    return jsonify(vehicle.serialize()), 200

@app.route('/vehicles', methods=['POST'])
def create_vehicle():
    data = request.get_json()
    name = data.get('name')
    model = data.get('model')

    if not name:
        return jsonify({"msg": "Name is required"}), 400

    vehicle = Vehicle(name=name, model=model)
    db.session.add(vehicle)
    db.session.commit()
    return jsonify(vehicle.serialize()), 201

@app.route('/vehicles/<int:id>', methods=['PUT'])
def update_vehicle(id):
    vehicle = Vehicle.query.get(id)
    if not vehicle:
        return jsonify({"msg": "Vehicle not found"}), 404

    data = request.get_json()
    vehicle.name = data.get('name', vehicle.name)
    vehicle.model = data.get('model', vehicle.model)

    db.session.commit()
    return jsonify(vehicle.serialize()), 200

@app.route('/vehicles/<int:id>', methods=['DELETE'])
def delete_vehicle(id):
    vehicle = Vehicle.query.get(id)
    if not vehicle:
        return jsonify({"msg": "Vehicle not found"}), 404

    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({"msg": "Vehicle deleted"}), 200




#Añadirfavorito
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_planet_favorite(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404
    
    if CURRENT_USER_ID is None:  # Verifica si el usuario está autenticado
        return jsonify({"msg": "User not authenticated"}), 401  # Devuelve error si no está autenticado

    favorite = Favorite(user_id=CURRENT_USER_ID, planet_id=planet_id, favorite_type=FavoriteType.planet)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_people_favorite(people_id):
    if not people_id:
        return jsonify({"msg": "Invalid people_id"}), 400

    character = Character.query.get(people_id)
    if not character:
        return jsonify({"msg": "Character not found"}), 404
    
    if CURRENT_USER_ID is None:  # Verifica si el usuario está autenticado
        return jsonify({"msg": "User not authenticated"}), 401  # Devuelve error si no está autenticado

    favorite = Favorite(
        user_id=CURRENT_USER_ID,
        character_id=people_id,
        favorite_type=FavoriteType.character
    )

    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201

@app.route('/favorite/vehicle/<int:vehicle_id>', methods=['POST'])
def add_vehicle_favorite(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({"msg": "Vehicle not found"}), 404
    
    if CURRENT_USER_ID is None:  # Verifica si el usuario está autenticado
        return jsonify({"msg": "User not authenticated"}), 401  # Devuelve error si no está autenticado

    favorite = Favorite(user_id=CURRENT_USER_ID, vehicle_id=vehicle_id, favorite_type=FavoriteType.vehicle)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201

#eliminarfavorito
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet_favorite(planet_id):
    favorite = Favorite.query.filter_by(user_id=CURRENT_USER_ID, planet_id=planet_id).first()
    if not favorite:
        return jsonify({"msg": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_people_favorite(people_id):
    favorite = Favorite.query.filter_by(user_id=CURRENT_USER_ID, character_id=people_id).first()
    if not favorite:
        return jsonify({"msg": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 200

@app.route('/favorite/vehicle/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle_favorite(vehicle_id):
    favorite = Favorite.query.filter_by(user_id=CURRENT_USER_ID, vehicle_id=vehicle_id).first()
    if not favorite:
        return jsonify({"msg": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
