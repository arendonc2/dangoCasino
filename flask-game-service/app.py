from flask import Flask, request, jsonify
import random

app = Flask(__name__)

RED_NUMBERS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19,
               21, 23, 25, 27, 30, 32, 34, 36]
BLACK_NUMBERS = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20,
                 22, 24, 26, 28, 29, 31, 33, 35]


def spin_wheel():
    return random.randint(0, 36)


def check_win(bet_type, bet_value, winning_number):
    if bet_type == "number":
        return str(winning_number) == str(bet_value)

    if bet_type == "color":
        if bet_value == "red":
            return winning_number in RED_NUMBERS
        if bet_value == "black":
            return winning_number in BLACK_NUMBERS
        return False

    if bet_type == "odd_even":
        if bet_value == "odd":
            return winning_number != 0 and winning_number % 2 == 1
        if bet_value == "even":
            return winning_number != 0 and winning_number % 2 == 0
        return False

    return False


def calculate_payout(bet_type, amount):
    if bet_type == "number":
        return amount * 35
    if bet_type in ("color", "odd_even"):
        return amount * 2
    return 0


def number_color(winning_number):
    if winning_number in RED_NUMBERS:
        return "red"
    if winning_number in BLACK_NUMBERS:
        return "black"
    return "green"


@app.route('/health/flask/', methods=['GET'])
def health_flask():
    return jsonify({"status": "ok", "service": "flask-roulette"}), 200


@app.route('/api/v2/roulette/play', methods=['POST'])
def roulette_play():
    payload = request.get_json(silent=True) or {}

    player_id = payload.get("player_id")
    bet_type = payload.get("bet_type")
    bet_value = payload.get("bet_value")
    amount = payload.get("amount")

    if player_id is None:
        return jsonify({
            "service": "flask-roulette",
            "status": "error",
            "message": "player_id is required",
        }), 400

    if not bet_type:
        return jsonify({
            "service": "flask-roulette",
            "status": "error",
            "message": "bet_type is required",
        }), 400

    if bet_type not in ("number", "color", "odd_even"):
        return jsonify({
            "service": "flask-roulette",
            "status": "error",
            "message": "Unsupported bet_type",
        }), 400

    if bet_value is None or str(bet_value).strip() == "":
        return jsonify({
            "service": "flask-roulette",
            "status": "error",
            "message": "bet_value is required",
        }), 400

    bet_value = str(bet_value).strip().lower()

    if bet_type == "number":
        try:
            number_value = int(bet_value)
        except (TypeError, ValueError):
            return jsonify({
                "service": "flask-roulette",
                "status": "error",
                "message": "Invalid number bet",
            }), 400

        if number_value < 0 or number_value > 36:
            return jsonify({
                "service": "flask-roulette",
                "status": "error",
                "message": "Number bet must be between 0 and 36",
            }), 400

        bet_value = str(number_value)

    elif bet_type == "color" and bet_value not in ("red", "black"):
        return jsonify({
            "service": "flask-roulette",
            "status": "error",
            "message": "Color bet must be red or black",
        }), 400

    elif bet_type == "odd_even" and bet_value not in ("odd", "even"):
        return jsonify({
            "service": "flask-roulette",
            "status": "error",
            "message": "Odd/even bet must be odd or even",
        }), 400

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({
            "service": "flask-roulette",
            "status": "error",
            "message": "Invalid bet amount",
        }), 400

    if amount <= 0:
        return jsonify({
            "service": "flask-roulette",
            "status": "error",
            "message": "Invalid bet amount",
        }), 400

    winning_number = spin_wheel()
    color = number_color(winning_number)
    is_winner = check_win(bet_type, bet_value, winning_number)
    payout = calculate_payout(bet_type, amount) if is_winner else 0

    return jsonify({
        "service": "flask-roulette",
        "status": "success",
        "player_id": player_id,
        "bet_type": bet_type,
        "bet_value": bet_value,
        "amount": amount,
        "winning_number": winning_number,
        "color": color,
        "is_winner": is_winner,
        "payout": payout,
        "message": "Roulette play processed by Flask service",
    }), 200


@app.route('/api/v2/play', methods=['POST'])
def play():
    # Backward-compatible alias.
    return roulette_play()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)