from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from flask import Flask
from dnd_ai_be.src.api_util import query_blueprint


app = Flask(__name__)
CORS(app, resources={r"/query": {"origins": [
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "http://127.0.0.1:5000",
    "http://localhost:5000",
    ]}})  # whitelisted origins

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "DnD AI API"
    }
)

app.register_blueprint(query_blueprint)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    app.run(debug=True)
