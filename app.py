import os
import io
import json
from datetime import datetime

from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    session,
)
from PIL import Image

# Gemini SDK imports (keeps your original logic)
from google import genai
from google.genai import types

# MongoDB & security
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from werkzeug.security import generate_password_hash, check_password_hash

# --- Flask Setup ---
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24).hex())

# --- Gemini API Setup (unchanged logic) ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", " ")
try:
    client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
    if client:
        print("Gemini Client initialized successfully.")
    else:
        print("Gemini Client not initialized: GEMINI_API_KEY missing.")
except Exception as e:
    print(f"ERROR: Could not initialize Gemini Client. Error: {e}")
    client = None

# --- MongoDB Setup ---
# Provide MONGO_URI like:
# export MONGO_URI="mongodb://localhost:27017"
# export MONGO_DB_NAME="derm_app" (optional; default used if not provided)
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "derm_app")

try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Optional: test server selection (will raise if cannot connect)
    mongo_client.server_info()
    db = mongo_client[MONGO_DB_NAME]
    users_col = db.get_collection("users")
    users_col.create_index([("username", ASCENDING)], unique=True)
    # Optional separate history collection for scale (not required; we keep history inside user doc)
    print(f"Connected to MongoDB at {MONGO_URI}, DB: {MONGO_DB_NAME}")
except Exception as e:
    # If DB fails, set users_col to None — routes will show errors
    print(f"WARNING: Could not connect to MongoDB: {e}")
    mongo_client = None
    db = None
    users_col = None


# --- Gemini Schema and Prediction Logic (unchanged) ---
DIAGNOSIS_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "disease": types.Schema(
            type=types.Type.STRING,
            description="The most probable dermatological condition. If unclear, use 'Unknown Dermatosis (Consult a specialist)'"
        ),
        "causes": types.Schema(
            type=types.Type.STRING,
            description="A brief summary of the primary causes."
        ),
        "precautions": types.Schema(
            type=types.Type.STRING,
            description="Key protective and preventative measures."
        ),
        "tablets": types.Schema(
            type=types.Type.STRING,
            description="Examples of prescription or oral treatments (for triage awareness)."
        ),
        "creams": types.Schema(
            type=types.Type.STRING,
            description="Examples of topical treatments/creams (for triage awareness)."
        ),
    },
    required=["disease", "causes", "precautions", "tablets", "creams"]
)


def predict_disease_gemini(image):
    if client is None:
        return {"error": "Analysis Error: Gemini Client not initialized (API Key missing)."}

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()

    prompt = (
        "You are an expert dermatological triage assistant. Analyze the visible skin condition in the provided image. "
        "Based on the image, identify the most probable condition and provide concise, accurate information for the "
        "causes, precautions, and recommended treatments (tablets/creams). "
        "Ensure your output strictly adheres to the required JSON schema. "
        "If the image is not a skin condition, is not clearly visible, or is non-diagnostic, set the 'disease' field to "
        "'Unknown Dermatosis (Consult a specialist)' and fill other fields with 'Not determinable from image.'"
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, types.Part.from_bytes(data=img_bytes, mime_type='image/png')],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DIAGNOSIS_SCHEMA,
                temperature=0.0
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini API call failed: {e}")
        return {"error": f"Analysis Error: API call failed or returned invalid data. Details: {e}"}


# --- MongoDB helper functions (users & history) ---
def create_user(username: str, password: str) -> dict:
    if users_col is None:
        raise RuntimeError("Database not configured.")
    hashed = generate_password_hash(password)
    user_doc = {"username": username, "password": hashed, "history": []}
    try:
        res = users_col.insert_one(user_doc)
        user_doc["_id"] = res.inserted_id
        return user_doc
    except DuplicateKeyError:
        raise
    except PyMongoError as e:
        raise RuntimeError(str(e))


def get_user(username: str):
    if users_col is None:
        return None
    return users_col.find_one({"username": username})


def check_user_password(username: str, password: str) -> bool:
    user = get_user(username)
    if not user:
        return False
    return check_password_hash(user.get("password", ""), password)


def add_history_entry(username: str, disease: str, precautions: str, timestamp: str = None):
    if users_col is None:
        raise RuntimeError("Database not configured.")
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {"timestamp": timestamp, "disease": disease, "precautions": precautions}
    users_col.update_one(
        {"username": username},
        {"$push": {"history": {"$each": [entry], "$position": 0}}}
    )


def get_history(username: str, limit: int = 100):
    user = get_user(username)
    if not user:
        return []
    history = user.get("history", [])
    return history[:limit]


# ===================== Flask Routes =====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_user_password(username, password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('home'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html', message=request.args.get('message'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if get_user(username):
            return render_template(
                'register.html',
                error="Username already exists. Please choose a different one."
            )
        try:
            create_user(username, password)
        except DuplicateKeyError:
            return render_template('register.html', error="Username already exists. Please choose a different one.")
        except Exception as e:
            return render_template('register.html', error=f"Registration error: {e}")
        return redirect(url_for('login', message="Account created successfully! Please log in."))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/')
def home():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    username = session['username']
    history = get_history(username)
    return render_template('main_app.html', history=history)


@app.route('/analyze', methods=['POST'])
def analyze():
    if 'logged_in' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    if 'image' not in request.files:
        return jsonify({"error": "No image file found"}), 400

    file = request.files['image']
    try:
        file_data = file.read()
        img = Image.open(io.BytesIO(file_data)).convert("RGB")
    except Exception:
        return jsonify({"error": "Invalid image file"}), 400

    diagnosis_data = predict_disease_gemini(img)
    if "error" in diagnosis_data:
        return jsonify(diagnosis_data), 500

    if 'logged_in' in session and session['username'] and users_col is not None:
        username = session['username']
        try:
            add_history_entry(
                username=username,
                disease=diagnosis_data.get("disease", "Unknown"),
                precautions=diagnosis_data.get("precautions", "No precautions provided."),
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        except Exception as e:
            # Log but continue returning result to user
            print(f"Warning: failed to save history: {e}")

    return jsonify({
        "disease": diagnosis_data.get("disease", "Unknown"),
        "causes": diagnosis_data.get("causes", "AI analysis unavailable."),
        "precautions": diagnosis_data.get("precautions", "AI analysis unavailable."),
        "tablets": diagnosis_data.get("tablets", "AI analysis unavailable."),
        "creams": diagnosis_data.get("creams", "AI analysis unavailable."),
    })


@app.route('/user_history', methods=['GET'])
def user_history():
    if 'logged_in' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    username = session['username']
    history = get_history(username)
    return jsonify({"history": history})


if __name__ == '__main__':
    # Helpful local warning if DB missing
    if users_col is None:
        print("Warning: MongoDB not configured or unreachable. Please set MONGO_URI and MONGO_DB_NAME appropriately.")
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
