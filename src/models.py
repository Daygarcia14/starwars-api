from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    favorites = db.relationship("Favorite", backref="user")

    def __repr__(self):
        return '<User %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
        }

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    nature = db.Column(db.String(40), nullable=False)
    nature_id = db.Column(db.Integer, nullable=False)
    __table_args__ = (db.UniqueConstraint(
    'user_id',
    'name',
    name="para no permitir favoritos duplicados"
    ),)
    
    def __repr__(self):
        return f"<Favorite object> f{self.id}"

    def serialize(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "nature": self.nature,
            "nature_id": self.nature_id
        }

class Character(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    hair_color = db.Column(db.String(20), nullable=False)
    eye_color = db.Column(db.String(10), nullable=False)
    gender = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"<Character object> f{self.name}"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "hair_color": self.hair_color, 
            "eye_color": self.eye_color,  
            "gender": self.gender, 
        }

    def __init__(self, *args, **kwargs):

        for (key, value) in kwargs.items():
            if hasattr(self, key):
                attr_type = getattr(self.__class__, key).type

                try:
                    attr_type.python_type(value)
                    setattr(self, key, value)
                except Exception as error:
                    print(f"ignore the other values: {error.args}")

    @classmethod
    def create(cls, data):
        instance = cls(**data)
        if (not isinstance(instance, cls)):
            print("Something failed")
            return None
        db.session.add(instance)
        try:
            db.session.commit()
            print(f"Created: {instance.name}")
            return instance
        except Exception as error:
            db.session.rollback()
            print(error.args)

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    population = db.Column(db.String(100))
    climate = db.Column(db.String(80), unique=False, nullable=False)
    terrain = db.Column(db.String(80), unique=False, nullable=False)
    diameter = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Planet object> f{self.name}"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population, 
            "climate": self.climate,  
            "terrain": self.terrain, 
            "diameter": self.diameter, 
        }
    
    def __init__(self, *args, **kwargs):

        for (key, value) in kwargs.items():
            if hasattr(self, key):
                attr_type = getattr(self.__class__, key).type

                try:
                    attr_type.python_type(value)
                    setattr(self, key, value)
                except Exception as error:
                    print(f"ignore the other values: {error.args}")

    @classmethod
    def create(cls, data):
        instance = cls(**data)
        if (not isinstance(instance, cls)):
            print("Something failed")
            return None
        db.session.add(instance)
        try:
            db.session.commit()
            print(f"Created: {instance.name}")
            return instance
        except Exception as error:
            db.session.rollback()
            print(error.args)

