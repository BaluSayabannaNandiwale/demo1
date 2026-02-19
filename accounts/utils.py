"""
Utility functions for accounts app.
"""
import math
import random


def generate_otp():
    """Generate 5-digit OTP"""
    digits = "0123456789"
    otp = ""
    for i in range(5):
        otp += digits[math.floor(random.random() * 10)]
    return otp
