from flask import Flask
from flask_cors import CORS
from database import db
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from routes.report_routes import report_bp
from middlewares.error_handler import register_error_handlers
from config.settings import SECRET_KEY, DEBUG, DATABASE_URL, SQLALCHEMY_TRACK_MODIFICATIONS, HOST, PORT
from datetime import datetime, timezone

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SECRET_KEY'] = SECRET_KEY

CORS(app)
db.init_app(app)

register_error_handlers(app)

app.register_blueprint(task_bp)
app.register_blueprint(user_bp)
app.register_blueprint(report_bp)


@app.route('/health')
def health():
    return {'status': 'ok', 'timestamp': str(datetime.now(timezone.utc))}


@app.route('/')
def index():
    return {'message': 'Task Manager API', 'version': '1.0'}


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=DEBUG, host=HOST, port=PORT)
