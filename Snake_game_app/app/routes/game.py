from flask import Blueprint, render_template

game_bp = Blueprint('game', __name__)

@game_bp.route('/game', methods=['GET'])
def play():
    return render_template('game.html')
