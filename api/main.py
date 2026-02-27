from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "Bienvenue sur l'API Web Page Quality Analyzer",
        "status": "success"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "Web Page Quality Analyzer API"
    })

@app.route('/test')
def test():
    return jsonify({
        "message": "Test endpoint fonctionne!",
        "data": {
            "version": "1.0.0",
            "framework": "Flask"
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
