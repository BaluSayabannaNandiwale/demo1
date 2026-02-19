"""
Admin configuration for proctoring app.
"""
from django.contrib import admin
from .models import ProctoringLog, WindowEstimationLog

admin.site.register(ProctoringLog)
admin.site.register(WindowEstimationLog)
