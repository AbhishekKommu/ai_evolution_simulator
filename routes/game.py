from functools import wraps
from flask import (
    Blueprint, render_template, request, redirect, url_for, session, flash
)
from models import db
from models.user import User
from models.creature import Creature
from ai.evolution import EvolutionEngine

game_bp = Blueprint('game', __name__)


def current_user():
    uid = session.get('user_id')
    return User.query.get(uid) if uid else None


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper


@game_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('game.dashboard'))
    return render_template('index.html')


@game_bp.route('/dashboard')
@login_required
def dashboard():
    user = current_user()
    creatures = Creature.query.filter_by(user_id=user.id) \
                              .order_by(Creature.created_at.desc()).all()
    return render_template('dashboard.html', user=user, creatures=creatures)


@game_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_creature():
    user = current_user()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        color = request.form.get('color', '#4A90E2')

        if not name:
            flash('Creature name is required.', 'error')
            return render_template('create_creature.html')

        try:
            traits = {
                'speed': int(request.form.get('speed', 50)),
                'strength': int(request.form.get('strength', 50)),
                'intelligence': int(request.form.get('intelligence', 50)),
                'agility': int(request.form.get('agility', 50)),
                'stamina': int(request.form.get('stamina', 50)),
            }
        except ValueError:
            flash('Invalid trait values.', 'error')
            return render_template('create_creature.html')

        if sum(traits.values()) > 300:
            flash('Total traits cannot exceed 300 points.', 'error')
            return render_template('create_creature.html')

        for k in traits:
            traits[k] = max(1, min(100, traits[k]))

        creature = Creature(name=name, user_id=user.id, color=color, **traits)
        creature.fitness = creature.compute_fitness()
        creature.add_history({
            'generation': 1,
            'fitness': creature.fitness,
            'traits': creature.traits,
            'note': 'Initial creation'
        })
        db.session.add(creature)
        db.session.commit()

        flash(f'Creature "{name}" created successfully!', 'success')
        return redirect(url_for('game.dashboard'))

    return render_template('create_creature.html')


@game_bp.route('/creature/<int:creature_id>')
@login_required
def view_creature(creature_id):
    user = current_user()
    creature = Creature.query.filter_by(id=creature_id, user_id=user.id).first_or_404()
    return render_template('evolution.html', creature=creature, history=creature.get_history())


@game_bp.route('/evolve/<int:creature_id>', methods=['POST'])
@login_required
def evolve(creature_id):
    user = current_user()
    parent = Creature.query.filter_by(id=creature_id, user_id=user.id).first_or_404()

    old_traits = parent.traits
    new_traits = EvolutionEngine.evolve(old_traits)
    changes = EvolutionEngine.describe_mutation(old_traits, new_traits)

    child = Creature(
        name=parent.name,
        user_id=user.id,
        generation=parent.generation + 1,
        color=parent.color,
        parent_id=parent.id,
        **new_traits
    )
    child.fitness = EvolutionEngine.simulate_environment(new_traits)

    # Copy past history then append current generation
    for h in parent.get_history():
        child.add_history(h)
    child.add_history({
        'generation': child.generation,
        'fitness': child.fitness,
        'traits': child.traits,
        'changes': changes
    })

    db.session.add(child)
    db.session.commit()

    return render_template('result.html', parent=parent, child=child, changes=changes)


@game_bp.route('/delete/<int:creature_id>', methods=['POST'])
@login_required
def delete_creature(creature_id):
    user = current_user()
    creature = Creature.query.filter_by(id=creature_id, user_id=user.id).first_or_404()
    db.session.delete(creature)
    db.session.commit()
    flash('Creature deleted.', 'success')
    return redirect(url_for('game.dashboard'))