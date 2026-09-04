"""
URL routing for livelihood_app.
"""

from django.urls import path
from . import views

app_name = 'livelihood'

urlpatterns = [
    # Template Views
    path('', views.index_view, name='index'),
    path('interview/', views.interview_view, name='interview'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # REST API Endpoints
    path('api/stt/transcribe/', views.STTTranscribeAPIView.as_view(), name='api_stt_transcribe'),
    path('api/interview/chat/', views.VoiceInterviewChatAPIView.as_view(), name='api_interview_chat'),
    path('api/recommend/', views.NSQFRecommendationAPIView.as_view(), name='api_recommend'),
    path('api/trades/', views.NSQFTradeListAPIView.as_view(), name='api_trades'),
    path('api/centers/', views.SkillCenterListAPIView.as_view(), name='api_centers'),
    path('api/widget/tts/', views.WidgetTTSAPIView.as_view(), name='api_widget_tts'),
]
