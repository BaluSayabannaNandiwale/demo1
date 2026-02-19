"""
URLs for exams app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('update/<str:test_id>/<str:qid>/', views.update_objective_question_view, name='update_objective_question'),
    path('updateLQA/<str:test_id>/<str:qid>/', views.update_long_question_view, name='update_long_question'),
    path('updatePQA/<str:test_id>/<str:qid>/', views.update_practical_question_view, name='update_practical_question'),
    path('delete_questions/<str:test_id>/', views.delete_questions_view, name='delete_questions'),
    path('scan-360/<str:test_id>/', views.scan_360_view, name='scan_360'),
    path('process-scan-frame/', views.process_scan_frame, name='process_scan_frame'),
    path('detect-cheating/', views.video_feed_view, name='detect_cheating'), # Mapped to video_feed_view as requested
    path('video_feed', views.video_feed_view, name='video_feed'), # Legacy path
    path('check-environment/', views.check_environment_view, name='check_environment'),
]
