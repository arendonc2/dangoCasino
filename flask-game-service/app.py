from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route('/api/v2/play', methods=['POST'])
def play():
    try:
        data = request.get_json()
        bet = data.get('bet', 0)

        if bet <= 0:
            return jsonify({"error": "Invalid bet"}), 400

        result = random.random()

        if result > 0.5:
            winnings = bet * 2
            return jsonify({
                "result": "win",
                "winnings": winnings
            }), 200
        else:
            return jsonify({
                "result": "lose",
                "winnings": 0
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)