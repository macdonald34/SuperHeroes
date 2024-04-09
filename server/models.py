from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    # add relationship
    hero_powers = relationship('HeroPower', back_populates='hero')

    # add serialization rules
    serialize_rules = ("-hero_powers",)
    
    def to_dict_basic(self):
        return{
            "id": self.id,
            "name": self.name, 
            "super_name": self.super_name
        }
    
    def to_dict_with_powers(self):
        return{
            "id": self.id,
            "name": self.name,
            "super_name": self.super_name,
            "hero_powers": [hero_power.to_dict() for hero_power in self.hero_powers]

        }
        
    def __repr__(self):
        return f'<Hero {self.id}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    # add relationship
    hero_powers = relationship('HeroPower', back_populates='power')

    # add serialization rules
    serialize_rules = ("-hero_powers",)

    # add validation
    @validates('description')
    def validate_description(self, key, value):
        if len(value or "") <  20:
            raise ValueError("Description must be at least 20 characters long")
        return value

    def __repr__(self):
        return f'<Power {self.id}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    # add relationships
    power_id = db.Column(db .ForeignKey('powers.id'), nullable=False)
    hero_id = db.Column(db.ForeignKey('heroes.id'), nullable=False)

    power = relationship("Power", foreign_keys=[power_id], back_populates='hero_powers', cascade=('all, delete'))
    hero = relationship("Hero", foreign_keys=[hero_id], back_populates="hero_powers", cascade=('all, delete'))

    # add serialization rules
    serialize_rules = ("-hero", "-power",)

    # add validation
    @validates('strength')
    def validate_strength(self, key, value):
        valid_strengths = ['Strong', 'Weak', 'Average']
        if not value in valid_strengths:
            raise ValueError("Strength must be one of the following values: 'Strong', 'Weak', 'Average'")
        return value

    def __repr__(self):
        return f'<HeroPower {self.id}>'