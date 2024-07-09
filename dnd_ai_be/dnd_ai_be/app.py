# these three lines swap the stdlib sqlite3 lib with the pysqlite3 package
import sys
import os
if os.getenv('ENVIRONMENT', 'production') == 'production':
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from flask_cors import CORS
from flask import Flask
from dnd_ai_be.src.api_util import query_blueprint


app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": [
#     "http://127.0.0.1:8080",
#     "http://localhost:8080",
#     "http://localhost:5000",
#     ]}})  # whitelisted origins

CORS(app)


SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'
# swaggerui_blueprint = get_swaggerui_blueprint(
#     SWAGGER_URL,
#     API_URL,
#     config={
#         'app_name': "DnD AI API"
#     }
# )

app.register_blueprint(query_blueprint)
# app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))

    if os.getenv('ENVIRONMENT', 'production') == 'development':
        app.run(debug=True,)
    else:
        app.run(debug=True,
                host='0.0.0.0',
                port=port,
                )
