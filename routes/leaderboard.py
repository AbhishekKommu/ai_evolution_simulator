from flask import Blueprint, render_template
from models.creature import Creature
from models.user import User

leaderboard_bp = Blueprint('leaderboard', __name__)


@leaderboard_bp.route('/leaderboard')
def leaderboard():
    top = Creature.query.order_by(Creature.fitness.desc()).limit(50).all()

    entries = []
    for rank, c in enumerate(top, start=1):
        owner = User.query.get(c.user_id)
        entries.append({
            'rank': rank,
            'creature': c,
            'owner': owner.username if owner else 'Unknown'
        })

    return render_template('leaderboard.html', entries=entries)