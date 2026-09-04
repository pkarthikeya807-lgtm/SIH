"""
Text-to-Speech (TTS) & Voice-to-Voice Translation Integration Module.
Implements integration hooks for Bhashini NMT / Indic-TTS / Meta SeamlessM4T endpoints,
with browser-native SpeechSynthesis fallback and multi-lingual conversational survey sequencing.
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)

BHASHINI_TTS_URL = os.environ.get("BHASHINI_TTS_URL", "https://dhruva-api.bhashini.gov.in/services/inference/tts")
BHASHINI_API_KEY = os.environ.get("BHASHINI_API_KEY", "")

# 7-Dimensional Conversational Survey Prompts in 7 Regional Languages
SURVEY_PROMPTS = {
    1: {
        'dimension': 'education_level',
        'title': 'Educational Background',
        'prompts': {
            'hi': 'नमस्ते! पीएम-अजय आजीविका मैपिंग में आपका स्वागत है। कृपया बताएं कि आपने कहाँ तक पढ़ाई की है? (जैसे: 5वीं, 8वीं, 10वीं, 12वीं या आईटीआई)',
            'ta': 'வணக்கம்! பிஎம்-அஜய் வாழ்வாதார திட்டத்திற்கு வரவேற்கிறோம். உங்கள் கல்வித் தகுதி என்ன? (எ.கா: 5-வது, 8-வது, 10-வது, 12-வது அல்லது ஐ.டி.ஐ)',
            'te': 'నమస్కారం! పీఎం-అజయ్ జీవనోపాధి వేదికకు స్వాగతం. మీరు ఎంతవరకు చదువుకున్నారు? (ఉదా: 5వ, 8వ, 10వ, 12వ లేదా ఐటీఐ)',
            'mr': 'नमस्कार! पीएम-अजय उपजीविका मॅपिंगमध्ये आपले स्वागत आहे. आपले शिक्षण कुठपर्यंत झाले आहे? (उदा: ५वी, ८वी, १०वी, १२वी किंवा आयटीआय)',
            'or': 'ନମସ୍କାର! ପିଏମ୍-ଅଜୟ ଜୀବିକା ମ୍ୟାପିଂରେ ଆପଣଙ୍କୁ ସ୍ୱାଗତ। ଦୟାକରି କୁହନ୍ତୁ ଆପଣ କେଉଁ ପର୍ଯ୍ୟନ୍ତ ପାଠ ପଢ଼ିଛନ୍ତି? (ଯଥା: ୫ମ, ୮ମ, ୧୦ମ, ୧୨ଶ କିମ୍ବା ଆଇଟିଆଇ)',
            'bn': 'নমস্কার! পিএম-অজয় জীবিকা ম্যাপিংয়ে আপনাকে স্বাগত। আপনি কতদূর পড়াশোনা করেছেন? (যেমন: ৫ম, ৮ম, ১০ম, ১২শ বা আইটিআই)',
            'en': 'Welcome to the PM-AJAY Livelihood Mapping. Could you please share your highest educational qualification? (e.g., 5th, 8th, 10th, 12th, ITI, or Graduate)'
        }
    },
    2: {
        'dimension': 'family_occupation',
        'title': 'Traditional Family Occupation',
        'prompts': {
            'hi': 'बहुत बढ़िया। आपके परिवार में पारंपरिक रूप से कौन सा काम या व्यवसाय होता आया है? (जैसे: हथकरघा/सिलाई, कृषि, बढ़ईगीरी, लोहार, कुम्हार या अन्य हस्तशिल्प)',
            'ta': 'மிக நன்று. உங்கள் குடும்பத்தில் பாரம்பரியமாக என்ன தொழில் செய்து வருகிறார்கள்? (எ.கா: கைத்தறி, விவசாயம், தச்சு வேலை, மண்பாண்டம்)',
            'te': 'చాలా మంచిది. మీ కుటుంబంలో సాంప్రదాయకంగా ఎలాంటి వృత్తి లేదా పని చేస్తున్నారు? (ఉదా: చేనేత, వ్యవసాయం, వడ్రంగి, కుమ్మరి మొదలైనవి)',
            'mr': 'खूप छान. आपल्या कुटुंबात पारंपरिकपणे कोणता व्यवसाय किंवा काम केले जाते? (उदा: हातमाग/शिलाई, शेती, सुतारकाम, लोहारकाम, कुंभारकाम)',
            'or': 'ବହୁତ ଭଲ। ଆପଣଙ୍କ ପରିବାରରେ ପାରମ୍ପରିକ ଭାବେ କେଉଁ କାମ କରାଯାଏ? (ଯଥା: ହସ୍ତତନ୍ତ, କୃଷି, କାଠ କାମ, କମାର କାମ, କୁମ୍ଭାର କାମ)',
            'bn': 'খুব ভালো। আপনার পরিবারে ঐতিহ্যগতভাবে কী কাজ বা ব্যবসা করা হয়? (যেমন: তাঁত/সেলাই, কৃষি, কাঠের কাজ, কামার বা মৃৎশিল্প)',
            'en': 'Great. What traditional occupation or craft has your family practiced? (e.g., Handloom weaving, Carpentry, Blacksmithing, Pottery, Agriculture, or Masonry)'
        }
    },
    3: {
        'dimension': 'current_livelihood',
        'title': 'Current Livelihood Status',
        'prompts': {
            'hi': 'वर्तमान में आप अपनी आजीविका के लिए क्या काम कर रहे हैं और क्या आपको इसमें नियमित आय मिल रही है?',
            'ta': 'தற்போது உங்கள் வாழ்வாதாரத்திற்கு என்ன வேலை செய்கிறீர்கள்? அதிலிருந்து நிலையான வருமானம் கிடைக்கிறதா?',
            'te': 'ప్రస్తుతం మీరు జీవనోపాధి కోసం ఏ పని చేస్తున్నారు? దాని ద్వారా స్థిరమైన ఆదాయం వస్తుందా?',
            'mr': 'सध्या आपण आपल्या उपजीविकेसाठी कोणते काम करत आहात आणि त्यातून नियमित उत्पन्न मिळते का?',
            'or': 'ବର୍ତ୍ତମାନ ଆପଣ ନିଜର ଗୁଜୁରାଣ ମେଣ୍ଟାଇବା ପାଇଁ କଣ କାମ କରୁଛନ୍ତି?',
            'bn': 'বর্তমানে আপনি আপনার জীবিকার জন্য কী কাজ করছেন এবং সেখান থেকে নিয়মিত আয় হচ্ছে কি?',
            'en': 'What is your current source of livelihood or daily occupation right now?'
        }
    },
    4: {
        'dimension': 'primary_skills',
        'title': 'Skills & Interests',
        'prompts': {
            'hi': 'आपको किन क्षेत्रों या कौशलों में सबसे अधिक रुचि है? (जैसे: सोलर पैनल फिटिंग, इलेक्ट्रिशियन, ऑटोमोबाइल, परिधान निर्माण, डिजिटल व कंप्यूटर रिपेयरिंग)',
            'ta': 'உங்களுக்கு எந்த துறையில் அல்லது திறனில் அதிக ஆர்வம் உள்ளது? (எ.கா: சோலார் நிறுவல், எலக்ட்ரீசியன், ஆடை வடிவமைப்பு, ஆட்டோமொபைல், டிஜிட்டல்)',
            'te': 'మీకు ఏ రంగంలో లేదా నైపుణ్యాలలో ఎక్కువ ఆసక్తి ఉంది? (ఉదా: సోలార్ ప్యానెల్ ఫిట్టింగ్, ఎలక్ట్రీషియన్, టైలరింగ్, ఆటోమొబైల్, డిజిటల్)',
            'mr': 'आपल्याला कोणत्या क्षेत्रात किंवा कौशल्यात सर्वात जास्त रस आहे? (उदा: सोलर पॅनेल, इलेक्ट्रिशियन, गारमेंट, डिजिटल, मेकॅनिक)',
            'or': 'ଆପଣଙ୍କୁ କେଉଁ କ୍ଷେତ୍ରରେ କାମ ଶିଖିବାକୁ ଅଧିକ ଆଗ୍ରହ ଅଛି? (ଯଥା: ସୋଲାର, ଇଲେକ୍ଟ୍ରିସିଆନ୍, ସିଲେଇ, ଗାଡ଼ି ମରାମତି, କମ୍ପ୍ୟୁଟର)',
            'bn': 'আপনার কোন ক্ষেত্রে বা দক্ষতায় সবচেয়ে বেশি আগ্রহ রয়েছে? (যেমন: সোলার প্যানেল, ইলেকট্রিশিয়ান, পোশাক তৈরি, অটোমোবাইল, কম্পিউটার)',
            'en': 'Which technical skills or trade sectors are you most passionate about learning? (e.g., Solar Installation, Electrician, Apparel/Fashion, Automotive, Digital/IT)'
        }
    },
    5: {
        'dimension': 'mobility_constraint',
        'title': 'Physical & Mobility Constraints',
        'prompts': {
            'hi': 'प्रशिक्षण या रोजगार के लिए आपकी आवाजाही की क्या सीमाएं हैं? क्या आप घर से/गाँव में, जिला मुख्यालय में, या राज्य स्तर पर जाकर काम कर सकते हैं?',
            'ta': 'பயிற்சி அல்லது வேலைக்காக உங்களால் வெளியூர் செல்ல முடியுமா? அல்லது உங்கள் மாவட்டத்திற்குள்ளேயே இருக்க விரும்புகிறீர்களா?',
            'te': 'శిక్షణ లేదా ఉద్యోగం కోసం మీరు ఇతర ప్రాంతాలకు వెళ్ళగలరా? లేదా మీ జిల్లాలోనే ఉండాలనుకుంటున్నారా?',
            'mr': 'प्रशिक्षण किंवा कामासाठी आपण बाहेर जाऊ शकता का? की आपल्या जिल्ह्यातच काम करू इच्छिता?',
            'or': 'ତାଲିମ କିମ୍ବା ରୋଜଗାର ପାଇଁ ଆପଣ ନିଜ ଜିଲ୍ଲା ଭିତରେ କାମ କରିବାକୁ ଚାହାଁନ୍ତି ନା ବାହାରକୁ ଯାଇପାରିବେ?',
            'bn': 'প্রশিক্ষণ বা কাজের জন্য আপনি কি জেলার বাইরে যেতে পারবেন, নাকি নিজের এলাকাতেই থাকতে চান?',
            'en': 'What are your mobility preferences? Are you seeking home-based/local village work, within district HQ, or open to state-wide mobility?'
        }
    },
    6: {
        'dimension': 'employment_preference',
        'title': 'Self vs Wage Employment Preference',
        'prompts': {
            'hi': 'कौशल सीखने के बाद क्या आप किसी कंपनी/दुकान में मासिक वेतन वाली नौकरी करना चाहते हैं, या अपना खुद का सूक्ष्म उद्यम/व्यवसाय शुरू करना चाहते हैं?',
            'ta': 'பயிற்சிக்கு பிறகு நீங்கள் மாத சம்பள வேலையில் சேர விரும்புகிறீர்களா அல்லது சொந்தமாக சிறு தொழில் தொடங்க விரும்புகிறீர்களா?',
            'te': 'నైపుణ్యం నేర్చుకున్న తర్వాత మీరు ఉద్యోగం చేయాలనుకుంటున్నారా లేదా మీ స్వంత వ్యాపారాన్ని ప్రారంభించాలనుకుంటున్నారా?',
            'mr': 'कौशल्य प्रशिक्षणानंतर आपल्याला पगारी नोकरी करायची आहे की स्वतःचा छोटा व्यवसाय/उद्योग सुरू करायचा आहे?',
            'or': 'ପ୍ରଶିକ୍ଷଣ ପରେ ଆପଣ ଚାକିରି କରିବାକୁ ଚାହାଁନ୍ତି ନା ନିଜର ଛୋଟ ବ୍ୟବସାୟ ଆରମ୍ଭ କରିବାକୁ ଚାହାଁନ୍ତି?',
            'bn': 'প্রশিক্ষণের পর আপনি কি কোথাও চাকরি করতে চান নাকি নিজস্ব ছোট ব্যবসা গড়ে তুলতে চান?',
            'en': 'Do you prefer regular wage employment in an enterprise, or starting your own micro-business / self-employed trade?'
        }
    },
    7: {
        'dimension': 'district_economy',
        'title': 'Local District Economic Realities',
        'prompts': {
            'hi': 'बहुत अच्छा! अंतिम सवाल: आपके जिले और आस-पास के बाजार में किस तरह के सामान या सेवाओं की सबसे ज्यादा मांग है?',
            'ta': 'சிறப்பு! உங்கள் பகுதியில் அல்லது மாவட்டத்தில் எந்த வகையான தொழில்/சேவைகளுக்கு அதிக தேவை உள்ளது?',
            'te': 'చాలా మంచిది! మీ జిల్లా లేదా స్థానిక మార్కెట్లో ఎలాంటి ఉత్పత్తులు లేదా సేవలకు మంచి డిమాండ్ ఉంది?',
            'mr': 'उत्तम! आपल्या जिल्ह्यात किंवा स्थानिक बाजारपेठेत कोणत्या वस्तू किंवा सेवांना सर्वाधिक मागणी आहे?',
            'or': 'ବଢ଼ିଆ! ଆପଣଙ୍କ ଜିଲ୍ଲାରେ ବା ସ୍ଥାନୀୟ ବଜାରରେ କେଉଁ କାମର ବେଶି ଚାହିଦା ଅଛି?',
            'bn': 'চমৎকার! আপনার এলাকায় বা স্থানীয় বাজারে কোন ধরনের কাজ বা পণ্যের চাহিদা সবচেয়ে বেশি?',
            'en': 'Thank you! Lastly, what are the high-demand industries or market opportunities in your local district?'
        }
    }
}


class TTSEngine:
    """
    Synthesizes regional Indic speech and manages conversational prompt generation.
    """

    @classmethod
    def get_prompt_for_step(cls, step_number=1, language='hi'):
        """
        Returns structured prompt metadata and localized text for a specific 7-dimension survey step.
        """
        step = SURVEY_PROMPTS.get(step_number, SURVEY_PROMPTS[1])
        prompts = step['prompts']
        text = prompts.get(language, prompts.get('hi', ''))
        return {
            'step': step_number,
            'dimension': step['dimension'],
            'title': step['title'],
            'text': text,
            'language': language,
            'is_last_step': step_number >= 7
        }

    @classmethod
    def synthesize_speech_payload(cls, text, language='hi', gender='female'):
        """
        Returns speech audio configuration / SSML metadata for browser and external Indic-TTS.
        """
        # Map regional ISO code to browser SpeechSynthesis voice tags
        voice_lang_tag = {
            'hi': 'hi-IN',
            'ta': 'ta-IN',
            'te': 'te-IN',
            'mr': 'mr-IN',
            'or': 'or-IN',
            'bn': 'bn-IN',
            'en': 'en-IN',
            'gu': 'gu-IN',
            'pa': 'pa-IN'
        }.get(language, 'hi-IN')

        return {
            'text': text,
            'language': language,
            'voice_lang_tag': voice_lang_tag,
            'rate': 0.95,
            'pitch': 1.05,
            'indic_tts_supported': True
        }
