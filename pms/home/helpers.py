import re
from difflib import SequenceMatcher
weak_passwords = [
    # Common English weak passwords
    'password', '123456', '123456789', 'qwerty', '12345', '12345678', '111111', 'abc123', 'password1', '1234',
    '123123', 'admin', 'welcome', 'letmein', 'monkey', 'dragon', 'football', 'baseball', 'master', 'hello', 
    'shadow', 'sunshine', 'iloveyou', 'trustno1', 'princess', 'password123', 'passw0rd', 'charlie', 'tigger', 
    'michael', 'jordan', 'superman', 'batman', 'soccer', 'hockey', 'ginger', 'liverpool', 'mickey', 'justin', 
    'love', 'jennifer', 'george', 'harley', 'rangers', 'snoopy', 'buster', 'qazwsx', 'qwertyuiop', 'starwars', 
    'pokemon', 'mercedes', 'ferrari', 'taylor', 'buster', 'yankees', 'chelsea', 'blink182', 'london', 'manchester',
    'startrek', 'password2', 'secret', '1234567', 'password1234', 'admin123', 'test', 'user', 'welcome123',
    '1q2w3e4r', 'abcd1234', 'qwerty123', 'mypass', 'mypassword', 'letmein1', 'admin1', 'login', 'access', 
    'batman123', 'superman123', 'q1w2e3r4', 'asdf1234', 'asdfgh', '123qwe', 'zxcvbn', 'asdfghjkl', 'asdfgh123', 
    'iloveyou1', 'welcome1', 'mypassword123', 'temp123', 'temp', 'changeme', 'newpassword', 'temporary', 'default',
    'guest', 'sunshine1', 'football123', 'whatever', 'nothing', 'passwords', 'guessme', 'welcomehome',

    # Hindi weak passwords
    'maibhulgya', 'pyar', 'dilse', 'dost', 'hindustan', 'shiva', 'radhe', 'krishna', 'ram123', 'bharat', 'vande', 
    'matram', 'meraindia', 'ishq', 'dil', 'mohabbat', 'zindagi', 'jee', 'ladki', 'ladka', 'mainhoon', 'swagat', 
    'chotu', 'pappu', 'aakash', 'sundar', 'samay', 'tiger', 'shaktiman', 'balaji', 'mahabharat', 'ganga', 
    'shaktishali', 'jayhind', 'deshbhakt', 'desi', 'namaste', 'shaan', 'jawan', 'mitra', 'nayi', 'bat', 'ankit', 
    'bholenath', 'bhai', 'golu', 'sonu', 'sanju', 'shiv', 'jai', 'hindustani', 'badshah', 'mumbai', 'delhi', 
    'kanha', 'pyaar', 'mitti', 'dosti', 'aapki', 'sapna', 'kal', 'raja', 'rani', 'amitabh', 'bollywood', 'hero', 
    'janam', 'ratan', 'mittal', 'suraj', 'chand', 'badal', 'babu', 'amrita', 'simran', 'roshan', 'singh', 'khan', 
    'golu', 'kajal', 'rajput', 'veer', 'bhagat', 'gulab', 'gaurav', 'kittu', 'geeta', 'prince', 'sunny', 'lalit', 
    'vivek', 'amit', 'seema', 'jeet', 'ranbir', 'kavita', 'kajol', 'ajay', 'raj', 'rajkumar', 'roy', 'vijay', 'neha', 
    'vicky', 'veer123', 'pyari', 'anil', 'nisha', 'megha', 'neetu', 'hero123', 'bolly123', 'raj123', 'simran123',
    'amrit123'
]



def calculate_strength(password, username=None, email=None):
    score = 0
    length = len(password)

    # Criteria 1: Password length scaling
    if length >= 10:
        score += 30
    elif length >= 8:
        score += 20
    elif length >= 6:
        score += 10
    else:
        score += 5

    # Criteria 2: Use of different character sets
    if re.search(r'[a-z]', password):
        score += 10  # Lowercase letters
    if re.search(r'[A-Z]', password):
        score += 10  # Uppercase letters
    if re.search(r'[0-9]', password):
        score += 10  # Digits
    if re.search(r'[^a-zA-Z0-9]', password):
        score += 15  # Special characters

    # Criteria 3: Penalty for common patterns
    common_patterns = ['1234', 'abcd', 'qwer', 'password', 'admin', 'letmein']
    if any(pattern in password.lower() for pattern in common_patterns):
        score -= 10

    # Criteria 4: Penalize repetition or sequences (e.g., "aaa", "111", "abc", "123")
    if re.search(r'(.)\1\1', password):  # Repeated characters
        score -= 7
    if re.search(r'012|123|234|345|456|567|678|789|890', password):  # Sequential numbers
        score -= 7
    if re.search(r'abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz', password):  # Sequential letters
        score -= 7

    # Criteria 5: Penalize if the password contains parts of username or email
    if username and SequenceMatcher(None, username.lower(), password.lower()).ratio() > 0.5:
        score -= 10
    if email and SequenceMatcher(None, email.split('@')[0].lower(), password.lower()).ratio() > 0.5:
        score -= 10

    # Criteria 6: Penalize for using common dictionary words or weak passwords
    if password.lower() in weak_passwords:
        score -= 20

    # Criteria 7: Reward for very strong combinations (rare special characters, good variety)
    if re.search(r'[!@#$%^&*()_+=]', password) and length >= 12:
        score += 15

    # Ensure the score is within the bounds of 0-100
    score = min(max(score, 0), 100)

    return score
