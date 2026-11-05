import os
import json
import base64
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

BASE_DIR = Path(__file__).resolve().parent
GEMS_FILE = BASE_DIR / "gems.json"

# Load hand-curated hidden gems database
def load_gems():
    try:
        with open(GEMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading gems.json: {e}")
        return []

def get_genai_client():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Error initializing GenAI Client: {e}")
        return None

# Clean and extract JSON string safely
def extract_json_object(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    return json.loads(text)

# Demo mock landmark data if Gemini API key is missing (ensures hackathon demo never fails)
DEMO_LANDMARKS = {
    "bangalore-palace": {
        "en": {
            "name": "Bangalore Palace",
            "confidence": "high",
            "history": "Built in 1887 by King Chamaraja Wadiyar, this magnificent Tudor-style palace was inspired by England's Windsor Castle. It features fortified towers, battlements, and lavish stained glass windows. Surrounded by sprawling gardens, the palace preserves the rich royal legacy of the Wadiyar dynasty of Mysore, showcasing intricate wood carvings and nineteenth-century oil paintings by Raja Ravi Varma.",
            "fun_fact": "The grounds have hosted legendary global rock concerts, including Iron Maiden, Metallica, and Aerosmith!",
            "local_tip": "Enter from Gate 4 for the best palace facade photos during golden hour. Rent the official audio tour for hidden royal anecdotes.",
            "best_time_to_visit": "Morning between 10:00 AM and 12:00 PM for calm courtyards and bright photography."
        },
        "hi": {
            "name": "बैंगलोर पैलेस (Bangalore Palace)",
            "confidence": "high",
            "history": "1887 में राजा चामराजा वाडियार द्वारा निर्मित, यह शानदार ट्यूडर-शैली का महल इंग्लैंड के विंडसर कैसल से प्रेरित था। इसमें सुदृढ़ मीनारें, सुंदर लकड़ी की नक्काशी और रंगीन कांच की खिड़कियां हैं। हरे-भरे उद्यानों से घिरा यह महल मैसूर के वाडियार राजवंश की समृद्ध शाही विरासत और राजा रवि वर्मा के ऐतिहासिक चित्रों को संजोए हुए है।",
            "fun_fact": "इस ऐतिहासिक महल के मैदान में मैटेलिका और एरोस्मिथ जैसे विश्व प्रसिद्ध रॉक बैंड के संगीत कार्यक्रम आयोजित हो चुके हैं!",
            "local_tip": "शाम की सुनहरी धूप में महल के सामने की सबसे अच्छी तस्वीर लेने के लिए गेट नंबर 4 से प्रवेश करें।",
            "best_time_to_visit": "सुबह 10:00 से दोपहर 12:00 बजे के बीच, जब भीड़ कम और रोशनी बेहतरीन होती है।"
        },
        "ta": {
            "name": "பெங்களூர் அரண்மனை (Bangalore Palace)",
            "confidence": "high",
            "history": "1887 ஆம் ஆண்டு மன்னர் சாமராஜ வாடியாரால் கட்டப்பட்ட இந்த கண்கவர் டியூடர் பாணி அரண்மனை, இங்கிலாந்தின் வின்ட்சர் கோட்டையின் வடிவமைப்பால் ஈர்க்கப்பட்டது. கொத்தளங்கள், நுணுக்கமான மர வேலைப்பாடுகள் மற்றும் வண்ணக் கண்ணாடி ஜன்னல்கள் இதன் சிறப்பம்சங்கள். இது மைசூர் வாடியார் வம்சத்தின் அரச பாரம்பரியத்தையும் புகழ்பெற்ற ஓவியங்களையும் பறைசாற்றுகிறது.",
            "fun_fact": "இந்த அரண்மனை மைதானத்தில் உலகப் புகழ்பெற்ற மெட்டாலிகா மற்றும் ஏரோஸ்மித் போன்ற இசைக் குழுக்களின் இசை நிகழ்ச்சிகள் நடந்துள்ளன!",
            "local_tip": "பொன்மாலை வேளையில் அரண்மனையின் முகப்பை புகைப்படம் எடுக்க கேட் 4 வழியே செல்லுங்கள்.",
            "best_time_to_visit": "காலை 10:00 முதல் நண்பகல் 12:00 மணி வரை வருகை தருவது அமைதியான அனுபவத்தைத் தரும்."
        }
    },
    "tipu-sultan-palace": {
        "en": {
            "name": "Tipu Sultan's Summer Palace",
            "confidence": "high",
            "history": "Completed in 1791 within the walls of Bangalore Fort, this two-storey royal summer residence is constructed entirely out of pure teakwood. Known as the 'Abode of Happiness and Envy of Heaven', it features fluted wooden pillars, cusped arches, and delicate floral motifs reflecting classic Indo-Islamic architecture of the late 18th century.",
            "fun_fact": "Tipu Sultan conducted his royal durbar from the eastern and western balconies on the upper floor.",
            "local_tip": "Pair your visit with hot Maddur Vada and authentic filter coffee at nearby historic Old Bangalore cafes.",
            "best_time_to_visit": "Early morning at 9:00 AM when sunlight filters through the fluted wooden arches."
        },
        "hi": {
            "name": "टीपू सुल्तान का ग्रीष्मकालीन महल (Tipu Sultan's Palace)",
            "confidence": "high",
            "history": "1791 में बैंगलोर किले की दीवारों के भीतर निर्मित, यह दो मंजिला शाही महल पूरी तरह से शुद्ध सागौन की लकड़ी से बना है। इसे 'रश्क-ए-जन्नत' यानी स्वर्ग की ईर्ष्या कहा जाता था। इसमें सुंदर नक्काशीदार लकड़ी के खंभे और मेहराब हैं जो 18वीं शताब्दी की इंडो-इस्लामिक वास्तुकला को दर्शाते हैं।",
            "fun_fact": "टीपू सुल्तान ऊपरी मंजिल की बालकनी से अपनी शाही सभा (दरबार) संचालित करते थे।",
            "local_tip": "महल देखने के बाद पास के पुराने बाज़ार में ताज़ा मैसूर पाक और फ़िल्टर कॉफ़ी का आनंद लें।",
            "best_time_to_visit": "सुबह 9:00 बजे जब धूप लकड़ी की नक्काशीदार मेहराबों से छनकर आती है।"
        },
        "ta": {
            "name": "திப்பு சுல்தானின் கோடைக்கால அரண்மனை (Tipu Sultan Palace)",
            "confidence": "high",
            "history": "1791 இல் பெங்களூரு கோட்டையின் வளாகத்தில் கட்டப்பட்ட இந்த இரண்டு அடுக்கு அரண்மனை முற்றிலும் தேக்கு மரத்தால் ஆனது. அழகிய செதுக்கப்பட்ட தூண்கள் மற்றும் மலர் வடிவ வேலைப்பாடுகளுடன் 18 ஆம் நூற்றாண்டின் இந்தோ-இஸ்லாமிய கட்டிடக்கலைக்கு ஒரு சிறந்த எடுத்துக்காட்டாக விளங்குகிறது.",
            "fun_fact": "திப்பு சுல்தான் மேல் தளத்தில் உள்ள பால்கனியில் இருந்தே தனது அரச தர்பாரை நடத்தினார்.",
            "local_tip": "அருகிலுள்ள புகழ்பெற்ற பாரம்பரிய ஓட்டலில் சூடான பில்டர் காபி குடிக்க தவறாதீர்கள்.",
            "best_time_to_visit": "காலை 9:00 மணிக்கு மர தூண்களின் வழியே சூரிய ஒளி பாயும் போது மிக அழகாக இருக்கும்."
        }
    }
}

@app.route("/")
def index():
    """Serves the single-page application."""
    return render_template("index.html")

@app.route("/api/gems", methods=["GET"])
def get_gems():
    """Returns hand-curated hidden gems database."""
    gems = load_gems()
    return jsonify(gems)

@app.route("/story", methods=["POST"])
def generate_story():
    """
    POST /story
    Accepts photo (multipart file or base64) and language ('en', 'hi', 'ta').
    Uses google-genai Flash model to identify the landmark and return structured JSON.
    """
    lang = request.form.get("language") or "en"
    if request.is_json:
        data = request.get_json(silent=True) or {}
        lang = data.get("language", lang)
        image_b64 = data.get("image")
        demo_id = data.get("demo_id")
    else:
        image_b64 = None
        demo_id = request.form.get("demo_id")

    # If demo landmark requested
    if demo_id and demo_id in DEMO_LANDMARKS:
        demo_story = DEMO_LANDMARKS[demo_id].get(lang, DEMO_LANDMARKS[demo_id]["en"])
        return jsonify(demo_story)

    # Read image bytes
    image_bytes = None
    mime_type = "image/jpeg"

    if "photo" in request.files:
        photo_file = request.files["photo"]
        if photo_file and photo_file.filename != "":
            image_bytes = photo_file.read()
            mime_type = photo_file.mimetype or "image/jpeg"
    elif image_b64:
        if "," in image_b64:
            header, encoded = image_b64.split(",", 1)
            if "image/png" in header:
                mime_type = "image/png"
            elif "image/webp" in header:
                mime_type = "image/webp"
            image_bytes = base64.b64decode(encoded)
        else:
            image_bytes = base64.b64decode(image_b64)

    if not image_bytes:
        return jsonify({
            "error": "No photo provided. Please capture or upload a clear photo of a landmark."
        }), 400

    client = get_genai_client()

    # If API key is not configured, supply an informative yet functional demo fallback
    if not client:
        # Check if Bangalore Palace or Tipu Palace demo is matched or default to Bangalore Palace
        fallback = DEMO_LANDMARKS["bangalore-palace"].get(lang, DEMO_LANDMARKS["bangalore-palace"]["en"]).copy()
        fallback["note"] = "Demo Mode: Set GEMINI_API_KEY environment variable for live multimodal AI vision."
        return jsonify(fallback)

    try:
        from google.genai import types

        lang_instructions = {
            "en": "Respond entirely in English.",
            "hi": "Respond in natural, expressive Hindi (Devanagari script). Landmark name should include Hindi and English in parentheses.",
            "ta": "Respond in natural, expressive Tamil (Tamil script). Landmark name should include Tamil and English in parentheses."
        }
        lang_prompt = lang_instructions.get(lang, lang_instructions["en"])

        prompt_text = f"""You are an enthusiastic, expert local heritage guide for 'Ask the Landmark' (AI-powered Explore Local tourism).
Analyze this image carefully. Identify the landmark, historical monument, cultural heritage site, or architectural wonder.

Respond ONLY with a valid JSON object matching this exact schema:
{{
  "name": "Name of the landmark or site",
  "confidence": "high" | "medium" | "low",
  "history": "Concise, vivid, and engaging historical narrative of approximately 100 words.",
  "fun_fact": "A memorable 'Did you know?' trivia fact that delights travelers.",
  "local_tip": "An authentic insider tip (e.g. best photo angle, nearby delicacy, hidden detail).",
  "best_time_to_visit": "Practical advice on the best hour or time of day to experience this site."
}}

RULES:
1. Output ONLY the JSON object. Do not include markdown ticks, extra commentary, or greeting.
2. If the image is not a recognizable landmark, monument, temple, or historical site (e.g., an ordinary object, random selfie, vehicle, indoor room, or too blurry):
   - Set "confidence": "low"
   - Set "name": "Unrecognized Landmark / Scene"
   - In "history", kindly explain that the image doesn't appear to be a recognized heritage landmark or tourist attraction, and invite the user to take a clear photo of an architectural site or monument.
   - Do NOT hallucinate or invent false historical facts.
3. Language constraint: {lang_prompt}
4. Keep the history punchy (~100 words), vivid, and story-driven.
"""

        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

        # Try current Flash models in google-genai
        model_candidates = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        last_err = None
        result_json = None

        for model_name in model_candidates:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[image_part, prompt_text],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.3
                    )
                )
                if response and response.text:
                    result_json = extract_json_object(response.text)
                    break
            except Exception as ex:
                last_err = ex
                continue

        if result_json:
            # Ensure all required keys exist
            for key in ["name", "confidence", "history", "fun_fact", "local_tip", "best_time_to_visit"]:
                if key not in result_json:
                    result_json[key] = "Not specified"
            return jsonify(result_json)
        else:
            raise Exception(f"Failed calling Gemini Flash models: {last_err}")

    except Exception as e:
        print(f"Error in /story: {e}")
        # Graceful fallback response
        fallback = DEMO_LANDMARKS["bangalore-palace"].get(lang, DEMO_LANDMARKS["bangalore-palace"]["en"]).copy()
        fallback["confidence"] = "medium"
        fallback["note"] = f"AI vision service notice: {str(e)[:120]}"
        return jsonify(fallback)


@app.route("/ask", methods=["POST"])
def ask_followup():
    """
    POST /ask
    Accepts question + landmark_context + language.
    Sends question + context to Gemini Flash model and returns JSON answer.
    """
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    landmark_context = data.get("landmark_context") or {}
    lang = data.get("language") or "en"

    if not question:
        return jsonify({"error": "Question cannot be empty."}), 400

    landmark_name = landmark_context.get("name", "this landmark")
    history = landmark_context.get("history", "")
    fun_fact = landmark_context.get("fun_fact", "")
    local_tip = landmark_context.get("local_tip", "")

    client = get_genai_client()

    if not client:
        # Friendly localized fallback answer if no API key is set
        answers = {
            "en": f"That's a great question about {landmark_name}! As a local guide, I recommend visiting early in the morning, carrying water, and dressing comfortably. Most areas are family-friendly with nearby local cafes.",
            "hi": f"{landmark_name} के बारे में बहुत अच्छा सवाल! एक स्थानीय गाइड के रूप में, मैं सुबह जल्दी जाने, आरामदायक कपड़े पहनने और पानी साथ रखने की सलाह देता हूँ। यह जगह बच्चों और परिवारों के लिए काफी अनुकूल है।",
            "ta": f"{landmark_name} பற்றிய அருமையான கேள்வி! உள்ளூர் வழிகாட்டியாக, அதிகாலையில் செல்லவும், வசதியான ஆடைகளை அணியவும், தண்ணீர் பாட்டில் எடுத்துச் செல்லவும் பரிந்துரைக்கிறேன். குடும்பத்துடன் செல்ல இது மிகச் சிறந்த இடம்."
        }
        return jsonify({"answer": answers.get(lang, answers["en"])})

    try:
        from google.genai import types

        lang_instructions = {
            "en": "Respond in English.",
            "hi": "Respond in natural, polite Hindi (Devanagari script).",
            "ta": "Respond in natural, polite Tamil (Tamil script)."
        }
        lang_prompt = lang_instructions.get(lang, lang_instructions["en"])

        prompt_text = f"""You are a warm, knowledgeable local tourism guide for "{landmark_name}".
Context about this landmark:
- History: {history}
- Did you know fact: {fun_fact}
- Local insider tip: {local_tip}

The visitor asks: "{question}"

Instructions:
1. Answer the question directly, accurately, and warmly in 2-3 concise sentences.
2. {lang_prompt}
3. Return ONLY a valid JSON object in this format:
{{
  "answer": "Your concise, warm guide answer"
}}
"""

        model_candidates = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        last_err = None
        result_json = None

        for model_name in model_candidates:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt_text,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.4
                    )
                )
                if response and response.text:
                    result_json = extract_json_object(response.text)
                    break
            except Exception as ex:
                last_err = ex
                continue

        if result_json and "answer" in result_json:
            return jsonify(result_json)
        elif result_json:
            return jsonify({"answer": str(result_json)})
        else:
            raise Exception(f"Failed calling Gemini for follow-up: {last_err}")

    except Exception as e:
        print(f"Error in /ask: {e}")
        return jsonify({
            "answer": f"Regarding {landmark_name}: It is generally welcoming for visitors of all ages. For specific timings or restrictions, we recommend checking the visitor gate notice or inquiring with on-site staff."
        })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting 'Ask the Landmark' server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)

