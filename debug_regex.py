
import re

def get_intensity_level(text):
    text = f" {text.lower()} " # Pad with spaces for word boundary matching
    
    # Priority 1: High Anxiety Indicators (Strong Expressions)
    high_patterns = [
        r"\bpanic\w*\b", r"\bextremely\s+anxious\b", r"\bintense\s+fear\b", 
        r"\bheart\s+race\w*\b", r"\bavoid\s+.*social\s+gatherings?\b", 
        r"\bavoid\s+.*public\s+speaking\b", r"\boverwhelmed\s+.*crowds?\b", 
        r"\bavoid\s+.*eye\s+contact\b", r"\bfear\s+embarrassment\b", 
        r"\bscared\s+to\s+speak\b"
    ]
    for pattern in high_patterns:
        if re.search(pattern, text):
            return "High", pattern
            
    # Priority 2: Moderate Anxiety Indicators
    moderate_patterns = [
        r"\bnervous\b", r"\bslightly\s+anxious\b", r"\buncomfortable\b", 
        r"\bshy\b", r"\bworry\b", r"\bhesitate\b", r"\bawkward\b", 
        r"\bconcern\s+.*about\s+judg[e|me]ment\b"
    ]
    for pattern in moderate_patterns:
        if re.search(pattern, text):
            return "Moderate", pattern
            
    # Priority 3: Low Anxiety/Positive Indicators
    low_patterns = [
        r"\benjoy\s+.*meeting\s+people\b", r"\bcomfortable\s+.*talking\b", 
        r"\bconfident\s+.*speaking\b", r"\blike\s+.*participating\b", 
        r"\bfeel\s+relaxed\b", r"\bno\s+problem\s+.*making\s+friends\b"
    ]
    for pattern in low_patterns:
        if re.search(pattern, text):
            return "Low", pattern
            
    return None, None

test_cases = [
    "I get slightly anxious during presentations.",
    "I enjoy meeting new people at social events.",
    "I feel extremely anxious when talking to strangers.",
    "I avoid public speaking at all costs."
]

for t in test_cases:
    level, pattern = get_intensity_level(t)
    print(f"Text: '{t}' -> Level: {level} (Pattern: {pattern})")
