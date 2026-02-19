"""
Django models for exams app.
"""
from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import User


class Teacher(models.Model):
    """Teacher/Professor test model"""
    tid = models.BigAutoField(primary_key=True)
    email = models.EmailField(max_length=100)
    test_id = models.CharField(max_length=100)
    test_type = models.CharField(max_length=75)  # 'objective', 'subjective', 'practical'
    start = models.DateTimeField(auto_now=True)
    end = models.DateTimeField()
    duration = models.IntegerField(validators=[MinValueValidator(1)])
    show_ans = models.IntegerField(default=0)
    password = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    topic = models.CharField(max_length=100)
    neg_marks = models.IntegerField(default=0)
    calc = models.IntegerField(default=0)
    proctoring_type = models.IntegerField(default=0)
    uid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='uid')
    
    class Meta:
        db_table = 'teachers'
        indexes = [
            models.Index(fields=['email', 'uid']),
            models.Index(fields=['test_id']),
        ]
    
    def __str__(self):
        return f"{self.test_id} - {self.subject}"


class Question(models.Model):
    """Objective test questions"""
    questions_uid = models.BigAutoField(primary_key=True)
    test_id = models.CharField(max_length=100)
    qid = models.CharField(max_length=25)
    q = models.TextField()
    a = models.CharField(max_length=100)
    b = models.CharField(max_length=100)
    c = models.CharField(max_length=100)
    d = models.CharField(max_length=100)
    ans = models.CharField(max_length=10)
    marks = models.IntegerField(validators=[MinValueValidator(1)])
    uid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='uid')
    
    class Meta:
        db_table = 'questions'
        indexes = [
            models.Index(fields=['test_id', 'qid']),
            models.Index(fields=['uid']),
        ]
    
    def __str__(self):
        return f"{self.test_id} - Q{self.qid}"


class Student(models.Model):
    """Student answers for objective tests"""
    sid = models.BigAutoField(primary_key=True)
    email = models.EmailField(max_length=100)
    test_id = models.CharField(max_length=100)
    qid = models.CharField(max_length=25, null=True, blank=True)
    ans = models.TextField(null=True, blank=True)
    uid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='uid')
    
    class Meta:
        db_table = 'students'
        indexes = [
            models.Index(fields=['email', 'test_id']),
            models.Index(fields=['uid']),
        ]
    
    def __str__(self):
        return f"{self.email} - {self.test_id}"


class StudentTestInfo(models.Model):
    """Student test session information"""
    stiid = models.BigAutoField(primary_key=True)
    email = models.EmailField(max_length=100)
    test_id = models.CharField(max_length=100)
    time_left = models.IntegerField()  # Time in seconds
    completed = models.IntegerField(default=0)
    uid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='uid')
    
    class Meta:
        db_table = 'studenttestinfo'
        indexes = [
            models.Index(fields=['email', 'test_id']),
            models.Index(fields=['uid']),
        ]
    
    def __str__(self):
        return f"{self.email} - {self.test_id}"


class LongQA(models.Model):
    """Subjective/Long answer questions"""
    longqa_qid = models.BigAutoField(primary_key=True)
    test_id = models.CharField(max_length=100)
    qid = models.CharField(max_length=25)
    q = models.TextField()
    marks = models.IntegerField(null=True, blank=True)
    uid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='uid', null=True, blank=True)
    
    class Meta:
        db_table = 'longqa'
        indexes = [
            models.Index(fields=['test_id', 'qid']),
            models.Index(fields=['uid']),
        ]
    
    def __str__(self):
        return f"{self.test_id} - Q{self.qid}"


class LongTest(models.Model):
    """Student answers for subjective tests"""
    longtest_qid = models.BigAutoField(primary_key=True)
    email = models.EmailField(max_length=100)
    test_id = models.CharField(max_length=100)
    qid = models.IntegerField()
    ans = models.TextField()
    marks = models.IntegerField()
    uid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='uid')
    
    class Meta:
        db_table = 'longtest'
        indexes = [
            models.Index(fields=['email', 'test_id']),
            models.Index(fields=['uid']),
        ]
    
    def __str__(self):
        return f"{self.email} - {self.test_id} - Q{self.qid}"


class PracticalQA(models.Model):
    """Practical/Programming questions"""
    pracqa_qid = models.BigAutoField(primary_key=True)
    test_id = models.CharField(max_length=100)
    qid = models.CharField(max_length=25)
    q = models.TextField()
    compiler = models.IntegerField()
    marks = models.IntegerField()
    uid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='uid')
    
    class Meta:
        db_table = 'practicalqa'
        indexes = [
            models.Index(fields=['test_id', 'qid']),
            models.Index(fields=['uid']),
        ]
    
    def __str__(self):
        return f"{self.test_id} - Q{self.qid}"


class PracticalTest(models.Model):
    """Student answers for practical tests"""
    pid = models.BigAutoField(primary_key=True)
    email = models.EmailField(max_length=100)
    test_id = models.CharField(max_length=100)
    qid = models.CharField(max_length=25)
    code = models.TextField(null=True, blank=True)
    input = models.TextField(null=True, blank=True)
    executed = models.CharField(max_length=125, null=True, blank=True)
    marks = models.IntegerField()
    uid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='uid')
    
    class Meta:
        db_table = 'practicaltest'
        indexes = [
            models.Index(fields=['email', 'test_id']),
            models.Index(fields=['uid']),
        ]
    
    def __str__(self):
        return f"{self.email} - {self.test_id} - Q{self.qid}"


class ViolationLog(models.Model):
    """Log for proctoring violations"""
    vid = models.BigAutoField(primary_key=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='violations')
    test_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()
    evidence = models.TextField(null=True, blank=True)  # Base64 image or path
    score = models.IntegerField(default=0)

    class Meta:
        db_table = 'violation_logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.student.email} - {self.test_id} - {self.timestamp}"
