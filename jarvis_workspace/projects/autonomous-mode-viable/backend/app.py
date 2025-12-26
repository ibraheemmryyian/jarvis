from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/decision', methods=['POST'])
def get_decision():
    data = request.get_json()
    decision = data['decision']
    
    if decision == 'Route to CHAT':
        result = "Routing to CHAT"
    elif decision == 'Route to CODER':
        result = "Routing to CODER"
    else:
        result = "Unknown decision"

    return jsonify(result=result)

if __name__ == '__main__':
    app.run(debug=True)