#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = [hero.to_dict_basic() for hero in Hero.query.all()]
    response = jsonify(heroes), 200
    return response

@app.route('/heroes/<int:hero_id>', methods=['GET'])
def get_hero_by_id(hero_id):
    hero = Hero.query.filter_by(id=hero_id).first()
    if not hero:
        return jsonify({'error': 'Hero not found.'}), 404
    
    return jsonify(hero.to_dict_with_powers()), 200

@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    powers_data = [power.to_dict() for power in powers]
    return jsonify(powers_data), 200


from flask import jsonify, request

# GET route to retrieve a power by its ID
@app.route('/powers/<int:id>', methods=['GET'])
def get_power_by_id(id):
    power = Power.query.filter_by(id=id).first()
    
    if power:
        return jsonify(power.to_dict()), 200
    else:
        return jsonify({"error": "Power not found"}), 404

# PATCH route to update a power by its ID
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power_by_id(id):
    power = Power.query.filter_by(id=id).first()
    
    if not power:
        return jsonify({"error": "Power not found"}), 404
    
    data = request.json
    
    if 'description' in data:
        new_description = data['description']
        
        if not new_description or len(new_description) < 20:
            return jsonify({"errors": ["validation errors"]}), 400

        power.description = new_description
    
    db.session.commit()
    
    return jsonify(power.to_dict()), 200

@app.route('/hero_powers', methods=['POST'])
def add_hero_power():
    hero_id = request.json.get('hero_id')
    power_id = request.json.get('power_id')
    strength = request.json.get('strength')

    if not all([hero_id, power_id]):
        return jsonify({"error": "Missing field(s)"}), 400
    
    hero = Hero.query.filter_by(id=hero_id).first()
    power = Power.query.filter_by(id=power_id).first()

    if not hero or not power:
        return jsonify({"error": "Invalid hero or power id."}), 404
    
    valid_strengths =['Weak','Average','Strong']
    if strength not in valid_strengths:
        return jsonify( {"errors": ["validation errors"]}),  400

    hero_power = HeroPower(hero=hero, power=power, strength=strength)

    db.session.add(hero_power)
    db.session.commit()

    return jsonify({
        "id": hero_power.id,
        "hero_id": hero_power.hero_id,
        "power_id": hero_power.power_id,
        "strength": hero_power.strength,
        "hero": hero.to_dict(),
        "power": power.to_dict()
    })



if __name__ == '__main__':
    app.run(port=5555, debug=True)