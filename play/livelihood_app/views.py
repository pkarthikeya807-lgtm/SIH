"""
Views and REST API endpoints for PM-AJAY NSQF Livelihood Platform.
Handles Bauhaus template rendering, STT speech capture, conversational interviewer,
NSQF recommendation calculation, and pop-out widget proxying.
"""

import json
import uuid
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import NSQFTrade, SkillCenter, Beneficiary, VoiceLog
from .utils.stt_engine import STTEngine, LANGUAGE_MAP
from .utils.tts_engine import TTSEngine, SURVEY_PROMPTS
from .utils.nsqf_matcher import NSQFMatcher


# -------------------------------------------------------------
# Template Views
# -------------------------------------------------------------

def index_view(request):
    """Landing Page: Bauhaus portal, 7-dimension overview, NSQF Trade Explorer."""
    trades = NSQFTrade.objects.all()
    centers = SkillCenter.objects.all()
    sectors = list(set(trades.values_list('sector', flat=True)))
    context = {
        'trades': trades,
        'centers': centers,
        'sectors': sectors,
        'total_trades': trades.count(),
        'total_centers': centers.count(),
        'languages': Beneficiary.LANGUAGE_CHOICES
    }
    return render(request, 'index.html', context)


def interview_view(request):
    """Voice Assistant Studio: Real-time conversational 7-dimension mapper."""
    session_id = request.GET.get('session_id', str(uuid.uuid4())[:8])
    lang = request.GET.get('lang', 'hi')
    initial_prompt = TTSEngine.get_prompt_for_step(1, lang)
    context = {
        'session_id': session_id,
        'selected_lang': lang,
        'initial_prompt': initial_prompt,
        'survey_prompts_json': json.dumps(SURVEY_PROMPTS),
        'languages': Beneficiary.LANGUAGE_CHOICES
    }
    return render(request, 'interview.html', context)


def dashboard_view(request):
    """NSQF Recommendations & Beneficiary Mapping Dashboard."""
    beneficiary_id = request.GET.get('beneficiary_id')
    trades = NSQFTrade.objects.all()
    centers = SkillCenter.objects.all()

    beneficiary = None
    if beneficiary_id:
        try:
            beneficiary = Beneficiary.objects.get(id=beneficiary_id)
        except (Beneficiary.DoesNotExist, ValueError):
            beneficiary = None

    if not beneficiary:
        # Provide sample default beneficiary for instant preview
        beneficiary = Beneficiary.objects.first()
        if not beneficiary:
            # Create a mock beneficiary on the fly
            beneficiary = Beneficiary(
                name="Ramesh Kumar",
                age=22,
                gender="M",
                district="Varanasi",
                state="Uttar Pradesh",
                preferred_language="hi",
                education_level="10th Pass",
                family_occupation="Handloom & Textiles",
                current_livelihood="Daily Wage Helper",
                primary_skills=["Basic Wiring", "Handloom Weaving"],
                mobility_constraint="Within District HQ",
                employment_preference="Self-Employed / Micro-Enterprise",
                district_economy="Rural Agri-Textile Hub"
            )

    recommendations = NSQFMatcher.evaluate_beneficiary(beneficiary)

    context = {
        'beneficiary': beneficiary,
        'recommendations': recommendations,
        'top_recommendation': recommendations[0] if recommendations else None,
        'other_recommendations': recommendations[1:5] if len(recommendations) > 1 else [],
        'centers': centers,
        'all_trades': trades,
    }
    return render(request, 'dashboard.html', context)


# -------------------------------------------------------------
# REST API Endpoints
# -------------------------------------------------------------

class STTTranscribeAPIView(APIView):
    """
    POST /api/stt/transcribe/
    Accepts audio payload / file and returns transcribed text & extracted 7D entities.
    """
    def post(self, request, *args, **kwargs):
        language = request.data.get('language', 'hi')
        audio_file = request.FILES.get('audio')

        if audio_file:
            transcription = STTEngine.transcribe_audio(
                audio_bytes_or_file=audio_file,
                language=language,
                content_type=audio_file.content_type
            )
        else:
            # Check raw audio data or text fallback
            raw_text = request.data.get('text', '')
            if raw_text:
                entities = STTEngine.extract_dimension_entities(raw_text, language)
                transcription = {
                    'text': raw_text,
                    'language': language,
                    'confidence': 0.98,
                    'engine': 'Direct Input',
                    'extracted_entities': entities
                }
            else:
                transcription = STTEngine.transcribe_audio(
                    audio_bytes_or_file=b"",
                    language=language
                )

        return Response({
            'success': True,
            'data': transcription
        }, status=status.HTTP_200_OK)


class VoiceInterviewChatAPIView(APIView):
    """
    POST /api/interview/chat/
    Manages conversational turn-taking, extracts 7D profile entities,
    and returns next prompt + speech synthesis payload.
    """
    def post(self, request, *args, **kwargs):
        session_id = request.data.get('session_id', str(uuid.uuid4())[:8])
        step = int(request.data.get('step', 1))
        language = request.data.get('language', 'hi')
        user_text = request.data.get('text', '').strip()
        beneficiary_id = request.data.get('beneficiary_id')
        name = request.data.get('name', 'Beneficiary')
        district = request.data.get('district', 'Varanasi')
        state = request.data.get('state', 'Uttar Pradesh')

        # Retrieve or create Beneficiary
        beneficiary = None
        if beneficiary_id:
            try:
                beneficiary = Beneficiary.objects.get(id=beneficiary_id)
            except Beneficiary.DoesNotExist:
                beneficiary = None

        if not beneficiary:
            beneficiary = Beneficiary.objects.create(
                name=name,
                district=district,
                state=state,
                preferred_language=language
            )

        # Parse entities from current turn
        extracted = STTEngine.extract_dimension_entities(user_text, language)

        # Map current step to attribute
        dim_map = {
            1: ('education_level', '8th Pass'),
            2: ('family_occupation', 'Traditional Craft'),
            3: ('current_livelihood', 'Daily Wage'),
            4: ('primary_skills', []),
            5: ('mobility_constraint', 'Within District HQ'),
            6: ('employment_preference', 'Self-Employed / Micro-Enterprise'),
            7: ('district_economy', 'Local Market Hub'),
        }

        curr_attr, default_val = dim_map.get(step, ('education_level', '8th Pass'))

        if curr_attr == 'primary_skills':
            skills = extracted.get('primary_skills', [])
            if not skills and user_text:
                skills = [user_text[:60]]
            beneficiary.primary_skills = skills
        else:
            val = extracted.get(curr_attr, user_text if user_text else default_val)
            setattr(beneficiary, curr_attr, val)

        # Determine next step
        next_step = step + 1
        is_completed = next_step > 7

        if is_completed:
            beneficiary.survey_completed = True
            beneficiary.save()

            # Compute recommendations
            recs = NSQFMatcher.evaluate_beneficiary(beneficiary)
            top_rec = recs[0] if recs else None

            completion_msgs = {
                'hi': f"धन्यवाद! आपका 7-आयामी सर्वेक्षण पूरा हो गया है। आपके लिए सर्वश्रेष्ठ एनएसक्यूएफ ट्रेड '{top_rec['trade_name'] if top_rec else 'सोलर इंस्टॉलर'}' अनुशंसित किया गया है।",
                'ta': f"நன்றி! உங்கள் கணக்கெடுப்பு முடிந்தது. உங்களுக்கான சிறந்த பரிந்துரை: '{top_rec['trade_name'] if top_rec else 'Solar Technician'}'.",
                'te': f"ధన్యవాదాలు! మీ సర్వే పూర్తయింది. మీ నైపుణ్యాలకు తగిన ట్రేడ్: '{top_rec['trade_name'] if top_rec else 'Solar Technician'}'.",
                'mr': f"धन्यवाद! आपले सर्वेक्षण पूर्ण झाले आहे. आपल्यासाठी सर्वोत्तम शिफारस: '{top_rec['trade_name'] if top_rec else 'Solar Installer'}'.",
                'or': f"ଧନ୍ୟବାଦ! ଆପଣଙ୍କ ସର୍ଭେ ସମ୍ପୂର୍ଣ୍ଣ ହୋଇଛି। ଆପଣଙ୍କ ପାଇଁ ସୁପାରିଶ: '{top_rec['trade_name'] if top_rec else 'Solar Installer'}'.",
                'bn': f"ধন্যবাদ! আপনার জরিপ সম্পূর্ণ হয়েছে। আপনার জন্য সেরা ট্রেড: '{top_rec['trade_name'] if top_rec else 'Solar Installer'}'.",
                'en': f"Thank you! Your 7-dimension mapping is complete. Your top recommended NSQF qualification pack is '{top_rec['trade_name'] if top_rec else 'Solar PV Installer'}'.",
            }
            resp_text = completion_msgs.get(language, completion_msgs['hi'])
            next_prompt_data = {
                'step': next_step,
                'dimension': 'completed',
                'title': 'Mapping Completed',
                'text': resp_text,
                'is_last_step': True
            }
        else:
            beneficiary.save()
            next_prompt_data = TTSEngine.get_prompt_for_step(next_step, language)
            resp_text = next_prompt_data['text']

        # Log conversation step
        VoiceLog.objects.create(
            session_id=session_id,
            beneficiary=beneficiary,
            transcribed_text=user_text,
            response_text=resp_text,
            detected_language=language,
            step_number=step,
            extracted_dimension=extracted
        )

        tts_payload = TTSEngine.synthesize_speech_payload(resp_text, language)

        return Response({
            'success': True,
            'session_id': session_id,
            'beneficiary_id': str(beneficiary.id),
            'current_step': step,
            'next_step': next_step,
            'is_completed': is_completed,
            'next_prompt': next_prompt_data,
            'tts': tts_payload,
            'beneficiary_profile': {
                'name': beneficiary.name,
                'district': beneficiary.district,
                'education_level': beneficiary.education_level,
                'family_occupation': beneficiary.family_occupation,
                'current_livelihood': beneficiary.current_livelihood,
                'primary_skills': beneficiary.primary_skills,
                'mobility_constraint': beneficiary.mobility_constraint,
                'employment_preference': beneficiary.employment_preference,
                'district_economy': beneficiary.district_economy,
            }
        }, status=status.HTTP_200_OK)


class NSQFRecommendationAPIView(APIView):
    """
    POST /api/recommend/
    Calculates NSQF trade matches given a beneficiary payload or ID.
    """
    def post(self, request, *args, **kwargs):
        beneficiary_id = request.data.get('beneficiary_id')
        beneficiary_data = request.data.get('beneficiary_data')

        if beneficiary_id:
            try:
                beneficiary = Beneficiary.objects.get(id=beneficiary_id)
            except Beneficiary.DoesNotExist:
                return Response({'error': 'Beneficiary not found'}, status=status.HTTP_404_NOT_FOUND)
        elif beneficiary_data:
            beneficiary = Beneficiary(
                name=beneficiary_data.get('name', 'Applicant'),
                education_level=beneficiary_data.get('education_level', '8th Pass'),
                family_occupation=beneficiary_data.get('family_occupation', 'Traditional Craft'),
                current_livelihood=beneficiary_data.get('current_livelihood', 'Daily Wage'),
                primary_skills=beneficiary_data.get('primary_skills', []),
                mobility_constraint=beneficiary_data.get('mobility_constraint', 'Within District HQ'),
                employment_preference=beneficiary_data.get('employment_preference', 'Self-Employed / Micro-Enterprise'),
                district_economy=beneficiary_data.get('district_economy', 'Rural Agri-Textile Hub'),
                district=beneficiary_data.get('district', 'Varanasi'),
                state=beneficiary_data.get('state', 'Uttar Pradesh')
            )
        else:
            beneficiary = Beneficiary.objects.first()

        recommendations = NSQFMatcher.evaluate_beneficiary(beneficiary)

        return Response({
            'success': True,
            'total_matches': len(recommendations),
            'recommendations': recommendations
        }, status=status.HTTP_200_OK)


class NSQFTradeListAPIView(APIView):
    """
    GET /api/trades/
    Returns list of NSQF Trades with optional sector & search filters.
    """
    def get(self, request, *args, **kwargs):
        sector = request.GET.get('sector')
        query = request.GET.get('q')

        trades = NSQFTrade.objects.all()
        if sector and sector != 'ALL':
            trades = trades.filter(sector__icontains=sector)
        if query:
            trades = trades.filter(name__icontains=query) | trades.filter(description__icontains=query)

        data = [
            {
                'id': t.id,
                'qp_code': t.qp_code,
                'name': t.name,
                'sector': t.sector,
                'nsqf_level': t.nsqf_level,
                'min_education': t.min_education,
                'wage_vs_self_score': t.wage_vs_self_score,
                'avg_monthly_income_inr': t.avg_monthly_income_inr,
                'duration_hours': t.duration_hours,
                'description': t.description,
                'key_modules': t.key_modules
            } for t in trades
        ]
        return Response({'success': True, 'count': len(data), 'trades': data})


class SkillCenterListAPIView(APIView):
    """
    GET /api/centers/
    Returns list of PM-AJAY skill training centers.
    """
    def get(self, request, *args, **kwargs):
        state = request.GET.get('state')
        district = request.GET.get('district')

        centers = SkillCenter.objects.all()
        if state:
            centers = centers.filter(state__icontains=state)
        if district:
            centers = centers.filter(district__icontains=district)

        data = [
            {
                'id': c.center_id,
                'name': c.name,
                'state': c.state,
                'district': c.district,
                'address': c.address,
                'contact_person': c.contact_person,
                'contact_phone': c.contact_phone,
                'contact_email': c.contact_email,
                'latitude': c.latitude,
                'longitude': c.longitude,
                'hostel_available': c.hostel_available,
                'pm_ajay_funded': c.pm_ajay_funded,
                'trades': [t.name for t in c.trades_offered.all()]
            } for c in centers
        ]
        return Response({'success': True, 'count': len(data), 'centers': data})


class WidgetTTSAPIView(APIView):
    """
    POST /api/widget/tts/
    Endpoint supporting the pop-out screen reader widget with regional speech metadata.
    """
    def post(self, request, *args, **kwargs):
        text = request.data.get('text', '')
        language = request.data.get('language', 'hi')
        payload = TTSEngine.synthesize_speech_payload(text, language)
        return Response({'success': True, 'tts': payload})
