import json
from datetime import datetime
from models import db


class Creature(db.Model):
    __tablename__ = 'creatures'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    generation = db.Column(db.Integer, default=1)
    fitness = db.Column(db.Float, default=0.0)

    speed = db.Column(db.Integer, default=50)
    strength = db.Column(db.Integer, default=50)
    intelligence = db.Column(db.Integer, default=50)
    agility = db.Column(db.Integer, default=50)
    stamina = db.Column(db.Integer, default=50)

    color = db.Column(db.String(20), default='#4A90E2')
    parent_id = db.Column(db.Integer, db.ForeignKey('creatures.id'), nullable=True)
    history = db.Column(db.Text, default='[]')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    children = db.relationship(
        'Creature',
        backref=db.backref('parent', remote_side=[id]),
        lazy=True
    )

    @property
    def traits(self):
        return {
            'speed': self.speed,
            'strength': self.strength,
            'intelligence': self.intelligence,
            'agility': self.agility,
            'stamina': self.stamina
        }

    @property
    def total_power(self):
        return self.speed + self.strength + self.intelligence + self.agility + self.stamina

    def compute_fitness(self):
        return round(
            self.speed * 0.20 +
            self.strength * 0.25 +
            self.intelligence * 0.25 +
            self.agility * 0.15 +
            self.stamina * 0.15,
            2
        )

    def get_history(self):
        try:
            return json.loads(self.history or '[]')
        except (ValueError, TypeError):
            return []

    def add_history(self, record):
        h = self.get_history()
        h.append(record)
        self.history = json.dumps(h)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'generation': self.generation,
            'fitness': self.fitness,
            'traits': self.traits,
            'total_power': self.total_power,
            'color': self.color,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Creature {self.name} Gen{self.generation}>'