"""
SQL Database Models for PM-AJAY NSQF Livelihood Platform.
Adheres strictly to the 7-dimension beneficiary mapping survey and NSQF Qualification Packs.
"""

import uuid
from django.db import models


class NSQFTrade(models.Model):
    """
    NSQF Qualification Pack (QP) definition.
    """
    qp_code = models.CharField(max_length=50, unique=True, help_text="Official QP Code, e.g. ELE/Q3102")
    name = models.CharField(max_length=200, help_text="Official Trade / QP Name")
    sector = models.CharField(max_length=100, help_text="Sector Skill Council / Domain")
    nsqf_level = models.IntegerField(default=3, help_text="NSQF Level from 1 to 7")
    min_education = models.CharField(
        max_length=100,
        default="8th Pass",
        help_text="Minimum education qualification requirement"
    )
    wage_vs_self_score = models.FloatField(
        default=0.5,
        help_text="0.0 = Pure Wage Employment, 1.0 = Pure Self-Employment / Micro-enterprise"
    )
    traditional_synergy_tags = models.JSONField(
        default=list,
        help_text="List of traditional family occupation keywords synergizing with this QP"
    )
    district_demand_tags = models.JSONField(
        default=list,
        help_text="List of regional district economy profile tags"
    )
    avg_monthly_income_inr = models.IntegerField(
        default=18000,
        help_text="Projected monthly wage/income in INR post certification"
    )
    duration_hours = models.IntegerField(
        default=360,
        help_text="Course duration in total training hours"
    )
    description = models.TextField(blank=True)
    key_modules = models.JSONField(
        default=list,
        help_text="Core technical and soft skill modules covered"
    )
    prerequisite_skills = models.JSONField(
        default=list,
        help_text="Foundational baseline skills"
    )

    class Meta:
        ordering = ['sector', 'nsqf_level', 'name']
        verbose_name = "NSQF Trade Qualification Pack"
        verbose_name_plural = "NSQF Trade Qualification Packs"

    def __str__(self):
        return f"[{self.qp_code}] {self.name} (Level {self.nsqf_level})"


class SkillCenter(models.Model):
    """
    PM-AJAY and PMKVY affiliated skill training centers.
    """
    center_id = models.CharField(max_length=50, unique=True, help_text="Unique Center Code, e.g. PMAJAY-TC-UP-01")
    name = models.CharField(max_length=200, help_text="Center name")
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    address = models.TextField()
    contact_person = models.CharField(max_length=120, blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    contact_email = models.EmailField(blank=True)
    latitude = models.FloatField(default=28.6139)
    longitude = models.FloatField(default=77.2090)
    hostel_available = models.BooleanField(default=False)
    pm_ajay_funded = models.BooleanField(default=True, help_text="Funded under PM-AJAY Special Central Assistance")
    trades_offered = models.ManyToManyField(NSQFTrade, related_name="training_centers", blank=True)

    class Meta:
        ordering = ['state', 'district', 'name']
        verbose_name = "PM-AJAY Skill Training Center"
        verbose_name_plural = "PM-AJAY Skill Training Centers"

    def __str__(self):
        return f"{self.name} ({self.district}, {self.state})"


class Beneficiary(models.Model):
    """
    Beneficiary profile mapped against the 7-dimension livelihood framework.
    """
    LANGUAGE_CHOICES = [
        ('hi', 'Hindi (हिन्दी)'),
        ('ta', 'Tamil (தமிழ்)'),
        ('te', 'Telugu (తెలుగు)'),
        ('mr', 'Marathi (मराठी)'),
        ('or', 'Odia (ଓଡ଼ିଆ)'),
        ('bn', 'Bengali (বাংলা)'),
        ('en', 'English'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, default="Anonymous Beneficiary")
    age = models.IntegerField(default=24)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='M')
    phone = models.CharField(max_length=20, blank=True)
    district = models.CharField(max_length=100, default="Varanasi")
    state = models.CharField(max_length=100, default="Uttar Pradesh")
    preferred_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='hi')

    # --- 7 DIMENSIONS ---
    # Dim 1: Educational Background
    education_level = models.CharField(
        max_length=100,
        default="8th Pass",
        help_text="Dim 1: Educational Background"
    )
    # Dim 2: Traditional Family Occupation
    family_occupation = models.CharField(
        max_length=150,
        default="Handloom & Textiles",
        help_text="Dim 2: Traditional Family Occupation"
    )
    # Dim 3: Current Livelihood
    current_livelihood = models.CharField(
        max_length=150,
        default="Daily Wage Helper",
        help_text="Dim 3: Current Livelihood"
    )
    # Dim 4: Skills & Interests
    primary_skills = models.JSONField(
        default=list,
        help_text="Dim 4: Skills & Interests extracted from dialogue"
    )
    # Dim 5: Physical / Mobility Constraints
    mobility_constraint = models.CharField(
        max_length=100,
        default="Within District HQ",
        help_text="Dim 5: Physical & Geographic Mobility constraints"
    )
    # Dim 6: Self vs Wage Employment Preference
    employment_preference = models.CharField(
        max_length=100,
        default="Self-Employed / Micro-Enterprise",
        help_text="Dim 6: Self vs Wage Employment Preference"
    )
    # Dim 7: Local District Economic Realities
    district_economy = models.CharField(
        max_length=150,
        default="Rural Agri-Textile Hub",
        help_text="Dim 7: Local District Economic Realities"
    )

    # Vector cache and survey status
    dimension_vector = models.JSONField(
        default=dict,
        blank=True,
        help_text="Calculated 7-dimension normalized weights"
    )
    survey_completed = models.BooleanField(default=False)
    recommended_trades = models.ManyToManyField(NSQFTrade, blank=True, related_name="recommended_beneficiaries")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Beneficiary Profile"
        verbose_name_plural = "Beneficiary Profiles"

    def __str__(self):
        return f"{self.name} - {self.district}, {self.state} ({self.get_preferred_language_display()})"


class VoiceLog(models.Model):
    """
    Speech and conversation session logs for audit, telemetry, and evaluation.
    """
    session_id = models.CharField(max_length=100, db_index=True)
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="voice_logs"
    )
    audio_file = models.FileField(upload_to="voice_recordings/", null=True, blank=True)
    transcribed_text = models.TextField(blank=True)
    response_text = models.TextField(blank=True)
    detected_language = models.CharField(max_length=20, default='hi')
    confidence_score = models.FloatField(default=0.92)
    step_number = models.IntegerField(default=1)
    extracted_dimension = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Voice Conversation Log"
        verbose_name_plural = "Voice Conversation Logs"

    def __str__(self):
        return f"VoiceLog [{self.session_id}] Step {self.step_number} ({self.detected_language})"
