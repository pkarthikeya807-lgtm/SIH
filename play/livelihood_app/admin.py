"""
Django Admin registration for PM-AJAY Livelihood models.
"""

from django.contrib import admin
from .models import NSQFTrade, SkillCenter, Beneficiary, VoiceLog


@admin.register(NSQFTrade)
class NSQFTradeAdmin(admin.ModelAdmin):
    list_display = ('qp_code', 'name', 'sector', 'nsqf_level', 'min_education', 'avg_monthly_income_inr', 'wage_vs_self_score')
    list_filter = ('sector', 'nsqf_level', 'min_education')
    search_fields = ('qp_code', 'name', 'sector', 'description')


@admin.register(SkillCenter)
class SkillCenterAdmin(admin.ModelAdmin):
    list_display = ('center_id', 'name', 'district', 'state', 'hostel_available', 'pm_ajay_funded')
    list_filter = ('state', 'district', 'hostel_available', 'pm_ajay_funded')
    search_fields = ('center_id', 'name', 'district', 'state', 'address')
    filter_horizontal = ('trades_offered',)


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'state', 'preferred_language', 'education_level', 'family_occupation', 'survey_completed', 'created_at')
    list_filter = ('preferred_language', 'survey_completed', 'state', 'education_level')
    search_fields = ('name', 'phone', 'district', 'family_occupation', 'current_livelihood')


@admin.register(VoiceLog)
class VoiceLogAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'step_number', 'detected_language', 'confidence_score', 'created_at')
    list_filter = ('detected_language',)
    search_fields = ('session_id', 'transcribed_text', 'response_text')
