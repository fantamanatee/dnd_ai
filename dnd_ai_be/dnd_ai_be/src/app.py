from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/query": {"origins": [
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    ]}})  # Adjust to your frontend URL

@app.route('/query', methods=['POST'])
def handle_query():
    data = request.json
    user_input = data.get('userInput', '')
    response_message = f"Hello World, {user_input}!"

    print('Response message:', response_message)  # Print the response message

    return jsonify({'message': response_message})


SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "DnD AI API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    app.run(debug=True)
