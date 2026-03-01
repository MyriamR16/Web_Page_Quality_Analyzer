from flask import Flask, jsonify
from dotenv import load_dotenv
from routes.analyse import analyse_bp
from routes.generate import generate_bp

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Register blueprints
app.register_blueprint(analyse_bp)
app.register_blueprint(generate_bp)

if __name__ == '__main__':
    app.run(debug=True)