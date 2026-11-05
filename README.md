# 🏛️ Ask the Landmark (Explore Local)

> **AI-Powered Local Tourism & Interactive Monument Companion**  
> *Built for Hackathons • Theme: "Explore Local"*

**Ask the Landmark** transforms every physical monument and heritage site into an interactive, voice-enabled local guide. Simply snap or upload a photo of any architectural landmark to receive its verified ~100-word history, secret "Did You Know?" trivia, authentic insider tips, and real-time open/closed status. 

It connects travelers with nearby hidden gems, builds time-optimized mini visit trails, answers visitor follow-up questions via **Google Gemini Flash**, awards **Explorer Badges**, and narrate stories aloud in **English, Hindi (हिंदी), and Tamil (தமிழ்)**.

---

## 🌟 Key Features

### 1. Multimodal AI Landmark Recognition (`POST /story`)
- **Multilingual Vision**: Powered by Google's latest **Gemini Flash** model via the official `google-genai` SDK.
- **Strict Anti-Hallucination**: If an image is not a recognizable heritage monument or landmark, Gemini flags it with low confidence and honest feedback rather than inventing facts.
- **Rich Story Cards**: Generates:
  - Landmark Name & Confidence Badge (`✓ High`, `⚡ Medium`, `⚠️ Low / Unsure`)
  - Concise ~100-word engaging historical narrative
  - 💡 **Did You Know?** trivia fact
  - 📍 **Local Insider Tip** (e.g., best photo angle, nearby delicacy)
  - ⏰ **Best Time to Visit** chip

### 2. Verified Real-Time Timing Engine (`gems.json`)
- **Zero Hallucination Hours**: Opening hours, closing hours, and closed days are strictly derived from curated, verified local records in `gems.json`—never invented by AI.
- **Dynamic Status Badges**:
  - 🟢 **Open**: `Open · closes 5:30 PM`
  - 🟠 **Closing Soon**: `Closing soon · closes 5:30 PM (35m left)` *(under 45 minutes remaining)*
  - 🔴 **Closed**: `Closed · opens 8:30 AM tomorrow` / `Closed · opens 9:00 AM today`

### 3. Smart "Plan My Visit" Trail Optimizer
- Pick your available time: **1 Hour** (Quick Tour), **2 Hours** (Explorer), or **Half Day** (4 Hours).
- Computes real-time open gems, calculates distances using the **Haversine formula**, and sequences stops starting from the nearest.
- Automatically factors in a **10-minute travel buffer** per leg plus average on-site duration (`avg_visit_minutes`).
- Outputs a timeline with exact **Arrival Time**, **Visit Duration**, **Leg Distance**, and **Crowd Level** (Low / Medium / High).

### 4. Interactive Heritage Experience
- 🔊 **Voice Narration (Listen)**: Built-in narration using the browser `SpeechSynthesis` API with play/pause and matching language voice models.
- 💬 **Ask a Follow-up**: In-context conversational guide (`POST /ask`) answering questions like *"Is it good for kids?"*, *"What should I wear?"*, and *"Best photography spots?"*.
- ❤️ **My Trail & Offline Favorites**: Save landmarks to `localStorage` with a persistent "My Trail" drawer and direct Google Maps navigation links.
- 🎖️ **Explorer XP & Badges**: Earn +50 XP per scan, +20 XP per question, and unlock badges (*First Discovery*, *Audio Tourist*, *Curious Historian*, *Trail Blazer*, *Hidden Gem Hunter*, *Itinerary Master*, *Polyglot Nomad*) with particle confetti celebrations.
- 📤 **Web Share API**: One-tap sharing to WhatsApp or social apps, with automatic clipboard copy fallback.
- 🌓 **Dark / Light Mode**: Seamless theme toggle with CSS variable transitions and mobile-first touch optimization.

---

## 📁 Folder Structure

```
hacksprint/
├── app.py                  # Flask backend with /story, /ask, and /api/gems endpoints
├── gems.json               # Hand-crafted database of 5 Bengaluru local hidden gems
├── requirements.txt        # Python library dependencies (google-genai, Flask, etc.)
├── .env.example            # Sample environment variables template
├── .env                    # Local environment file containing your GEMINI_API_KEY
├── templates/
│   └── index.html          # Mobile-friendly single HTML file (CSS + Vanilla JS)
├── static/
│   └── readme.txt          # Static assets directory
└── README.md               # Complete documentation and setup instructions
```

---

## 📍 Sample `gems.json` (Bengaluru, India)

The app comes pre-loaded with 5 authentic, hand-curated landmarks and hidden gems in Bengaluru:
1. **Bangalore Palace** (Tudor-style royal heritage)
2. **Tipu Sultan's Summer Palace** (1791 teakwood marvel, closed Mondays)
3. **Lalbagh Botanical Garden & Glass House** (1760 royal gardens & 1889 cast-iron pavilion)
4. **Bugle Rock & Dodda Basavana Gudi** (3,000-million-year-old rock & monolithic Nandi)
5. **Malleshwaram 8th Cross & Kadu Malleshwara** (Vibrant flower market & 17th-century shrine)

---

## 🚀 Exact Steps to Run Locally

### Prerequisites
- Python 3.10+ installed
- A Google Gemini API key from [Google AI Studio](https://aistudio.google.com/) *(Free tier works great!)*

### Step 1: Clone or Navigate to the Project Directory
```powershell
cd c:\Users\HP\Desktop\projects\hacksprint
```

### Step 2: Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Configure Your Gemini API Key
Create a `.env` file in the project root:
```powershell
Copy-Item .env.example .env
```
Open `.env` in any editor and insert your Gemini API Key:
```env
GEMINI_API_KEY=AIzaSyYourActualGeminiApiKeyHere
PORT=5000
```
*(Alternatively, set it in your terminal session: `$env:GEMINI_API_KEY="AIzaSy..."`)*

> **Note for Instant Demos**: If you run without an API key, the app automatically runs in **Smart Demo Mode** with pre-configured high-fidelity landmark cards so you can test all features, voices, and itineraries right away!

### Step 4: Run the Flask Server
```powershell
python app.py
```

### Step 5: Open in Your Browser
Visit:
```
http://localhost:5000
```
Open Chrome or Edge DevTools (`F12`) and toggle the **Mobile Device Toolbar** (`Ctrl + Shift + M` / iPhone 14 Pro view) for the best mobile experience.

---

## 🎯 Quick 90-Second Hackathon Demo Script

1. **Open the App**: Notice the theme toggle (🌙 / ☀️) and the live XP points counter (`⭐ 50 XP · City Explorer`).
2. **Instant Demo Scan**: Tap **"🏰 Bangalore Palace"** under *Quick Demo Landmarks* (or snap/upload your own monument photo).
3. **Watch the AI Scan**: Observe the radar scan animation while Gemini processes the architectural features.
4. **Inspect the Story Card**:
   - Check the **Confidence Badge** (`✓ High Confidence`).
   - Read the punchy ~100-word history.
   - Note the **"Did You Know?"** fact and **"Local Insider Tip"**.
5. **Audio Narration**: Click **"🔊 Listen to Story"** to hear the browser speak the story aloud.
6. **Ask Gemini a Follow-up**:
   - Tap one of the prompt chips (e.g. `👶 Good for kids?` or `👗 What should I wear?`).
   - Watch Gemini answer directly in 2-3 warm, practical sentences.
7. **Nearest Hidden Gem**:
   - Scroll down to the **Next Recommended Stop** card showing the nearest gem, distance in kilometers, live `Open · closes 5:30 PM` badge, and **"Open in Maps"** button.
8. **Plan My Visit**:
   - Click **"🗺️ Plan My Visit"** and select **"2 hrs"**.
   - Watch the trail builder dynamically generate stops with arrival times, crowd levels, and 10-minute travel buffers.
9. **Multilingual Test**: Switch the language dropdown to **हिंदी (Hindi)** or **தமிழ் (Tamil)** to see the interface, story, and speech adapt instantly!

