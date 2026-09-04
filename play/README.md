# PM-AJAY NSQF Livelihood & Voice-to-Voice AI Platform

A production-ready, accessible vocational skilling and livelihood platform for the **Pradhan Mantri Anusuchit Jaati Abhyuday Yojana (PM-AJAY)** initiative by the Government of India. 

The platform features an empathetic **7-Dimensional Voice-to-Voice Conversational Interviewer**, an **NSQF Trade Recommendation Engine**, a strict **Bauhaus Design System**, and a standalone **Pop-Out Screen Reader Widget (`widget.js`)**.

---

## 🏛 1. High-Fidelity Bauhaus UI/UX Design System

The visual system strictly follows Bauhaus principles (*"Form follows function"*, geometric compositions, heavy structural grid lines, flat 2D graphic design):

- **Color Palette:**
  - **Background:** Cream (`#F5F2EB` / `#FFFFFF`)
  - **Borders / Structural Lines / Text:** Stark Black (`#111111`)
  - **Primary Accent 1:** Bauhaus Navy Blue (`#06038D`)
  - **Primary Accent 2:** Deep Saffron (`#FF671F` / `#FF9933`)
  - **Supporting Accents:** Geometric Yellow (`#FFD700`), Crimson Red (`#D32F2F`), Forest Green (`#007A3D`)
- **Typography:** Bold sans-serif (`Inter`, `Helvetica Neue`, `Arial`, system-ui) with extreme size contrasts.
- **Styling Rules:** Flat color blocks, solid thick borders (`2.5px` to `4px` black), **zero box-shadows**, **zero gradients**, tactile button press states.

---

## 🧠 2. Core Architecture & Modules

```
pmajay_livelihood_platform/
├── manage.py
├── requirements.txt
├── README.md
├── pmajay_core/                  # Core Django Configuration
│   ├── __init__.py
│   ├── settings.py              # SQLite, DRF, CORS, Static settings
│   ├── urls.py                  # Root URL dispatcher
│   └── wsgi.py
├── livelihood_app/               # Application Business Logic
│   ├── models.py                # SQL Models: Beneficiary, NSQFTrade, SkillCenter, VoiceLog
│   ├── views.py                 # Views & REST API Endpoints
│   ├── urls.py                  # Application routing
│   ├── admin.py                 # Django Admin configuration
│   ├── management/
│   │   └── commands/
│   │       └── seed_nsqf_data.py # Seeds 10+ NSQF QPs & 7 PM-AJAY Training Centers
│   ├── utils/
│   │   ├── stt_engine.py        # Speech-to-Text (Whisper / Bhashini ASR pipeline)
│   │   ├── tts_engine.py        # Speech Synthesis (Indic-TTS + Browser Web Speech API)
│   │   └── nsqf_matcher.py      # 7-Dimension Vector Scoring & Skill Gap Algorithm
│   └── templates/
│       ├── base.html            # Master Bauhaus Layout Shell
│       ├── index.html           # Portal Landing Page & NSQF Explorer
│       ├── interview.html       # Voice-to-Voice AI Interviewer & Live Visualizer
│       └── dashboard.html       # NSQF Recommendations & PM-AJAY Centers Dashboard
└── static/
    ├── css/
    │   └── bauhaus.css          # Strict Bauhaus CSS design system
    └── js/
        ├── recorder.js          # Web Audio API recording & live spectrum canvas
        └── widget.js            # Standalone Pop-Out Screen Reader Script
```

---

## 🎙 3. Feature Breakdown

### 1. Multi-Lingual Speech-to-Text (Voice Capture)
- Browser `MediaRecorder` captures audio streams via Web Audio API.
- Live Bauhaus canvas waveform visualizer displaying frequency bars in Navy Blue and Saffron.
- Multi-lingual transcription supporting **Hindi, Tamil, Telugu, Marathi, Odia, Bengali, and English**.
- Integrated with Whisper & Bhashini ASR pipelines with local contextual fallback.

### 2. Real-Time 7-Dimension Conversational Interviewer
Conducts an empathetic beneficiary interview across 7 core dimensions:
1. **Educational Background:** Primary, 8th, 10th, 12th, ITI, or Graduate verification.
2. **Traditional Family Occupation:** Lineage heritage crafts (Weaving, Carpentry, Blacksmithing, Pottery, Masonry) unlocking **Recognition of Prior Learning (RPL)** bonuses.
3. **Current Livelihood:** Baseline wage helper, street vendor, farm worker.
4. **Skills & Interests:** Solar PV, electrical, tailoring, automotive/EV repair, digital tools.
5. **Physical / Mobility Constraints:** Village/Home-based, District HQ, or State-level mobility.
6. **Self vs. Wage Employment Preference:** Micro-enterprise / SHG group vs regular monthly job.
7. **Local District Economic Realities:** ODOP clusters, rural agri-tech, industrial corridors.

### 3. NSQF Skill Recommendation & Match Engine
- **Weighted Compatibility Algorithm:** Evaluates candidate vector against official Qualification Packs (QPs).
- **Skill Gap Analysis:** Highlights prerequisite gaps, safety bridge modules, and estimated training hours.
- **Economic Upside Projection:** Calculates estimated monthly income (INR) post-certification.
- **PM-AJAY Training Centers:** Links beneficiary directly to nearest district training centers with hostel and stipend info.

### 4. Injectable Screen Reader Widget (`widget.js`)
- Standalone zero-dependency JavaScript widget.
- Injects a floating Bauhaus action pill: `[ 🔊 PM-AJAY Audio ]`.
- **Text Selection Mode:** Instantly reads out any highlighted paragraph or section.
- **Full DOM Reader Mode:** Cycles through headings and cards with a high-contrast yellow/saffron highlighting outline.
- **Language Selector:** Supports multi-lingual Indic TTS voices with pause, resume, pitch, and rate controls.

---

## 🚀 4. Setup & Execution Guide

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)

### Installation
```bash
# 1. Create and activate a virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
python manage.py makemigrations
python manage.py migrate

# 4. Seed official NSQF Qualification Packs and PM-AJAY Skill Centers
python manage.py seed_nsqf_data

# 5. Create superuser for Django Admin (optional)
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

Open your browser at `http://127.0.0.1:8000/` to access the platform.

---

## 📡 5. REST API Specifications

| Method | Endpoint | Description | Payload |
|---|---|---|---|
| `POST` | `/api/stt/transcribe/` | Transcribes audio and extracts 7D entities | `audio` (file) or `text`, `language` |
| `POST` | `/api/interview/chat/` | Next conversational step & 7D vector update | `session_id`, `step`, `text`, `language` |
| `POST` | `/api/recommend/` | Computes NSQF recommendations for beneficiary | `beneficiary_id` or `beneficiary_data` |
| `GET` | `/api/trades/` | Lists NSQF Trades with sector/search filter | Query params: `?sector=Green+Jobs&q=solar` |
| `GET` | `/api/centers/` | Lists PM-AJAY Skill Centers | Query params: `?state=Uttar+Pradesh` |
| `POST` | `/api/widget/tts/` | Pop-out screen reader synthesis metadata | `text`, `language` |

---

## 📦 6. How to Embed `widget.js` on External Portals

Include the widget script in any HTML page to instantly enable Bauhaus-styled screen reader accessibility:

```html
<!-- Inject PM-AJAY Screen Reader Widget -->
<script src="http://127.0.0.1:8000/static/js/widget.js"></script>
```
