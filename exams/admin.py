"""
Admin configuration for exams app.
"""
from django.contrib import admin
from .models import Teacher, Question, Student, StudentTestInfo, LongQA, LongTest, PracticalQA, PracticalTest

admin.site.register(Teacher)
admin.site.register(Question)
admin.site.register(Student)
admin.site.register(StudentTestInfo)
admin.site.register(LongQA)
admin.site.register(LongTest)
admin.site.register(PracticalQA)
admin.site.register(PracticalTest)
