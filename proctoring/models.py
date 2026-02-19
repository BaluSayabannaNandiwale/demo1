"""
Django models for proctoring app.
"""
from django.db import models
from accounts.models import User


class ProctoringLog(models.Model):
    """Proctoring activity logs"""
    pid = models.BigAutoField(primary_key=True)
    email = models.EmailField(max_length=100)
    name = models.CharField(max_length=100)
    test_id = models.CharField(max_length=100)
    voice_db = models.IntegerField(default=0)
    img_log = models.TextField()  # Base64 encoded image
    user_movements_updown = models.IntegerField()
    user_movements_lr = models.IntegerField()
    user_movements_eyes = models.IntegerField()
    phone_detection = models.IntegerField()
    person_status = models.IntegerField()
    log_time = models.DateTimeField(auto_now_add=True)
    uid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='uid')
    
    class Meta:
        db_table = 'proctoring_log'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['email', 'test_id']),
            models.Index(fields=['uid']),
        ]
        ordering = ['-log_time']
    
    def __str__(self):
        return f"{self.email} - {self.test_id} - {self.log_time}"


class WindowEstimationLog(models.Model):
    """Window/tab switching event logs"""
    wid = models.BigAutoField(primary_key=True)
    email = models.EmailField(max_length=100)
    test_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    window_event = models.IntegerField()
    transaction_log = models.DateTimeField(auto_now_add=True)
    uid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='uid')
    
    class Meta:
        db_table = 'window_estimation_log'
        indexes = [
            models.Index(fields=['email', 'test_id']),
            models.Index(fields=['uid']),
        ]
        ordering = ['-transaction_log']
    
    def __str__(self):
        return f"{self.email} - {self.test_id} - {self.transaction_log}"
