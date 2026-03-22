import csv
import os

STRICT_WORDS = {
    'High': {
        'panic': 5, 'anxious': 5, 'nervous': 5, 'sweating': 5, 'racing': 5, 
        'fear': 5, 'overwhelmed': 5, 'breathless': 5, 'shaking': 5, 'tense': 4,
        'sweat': 5, 'panicking': 5, 'anxiety': 5, 'terrified': 5, 'heartbeat': 4, 
        'palpitation': 5, 'trembling': 5, 'dread': 5
    },
    'Moderate': {
        'awkward': 4, 'uneasy': 4, 'unsure': 3, 'hesitant': 3, 
        'uncomfortable': 4, 'worried': 4, 'worry': 4, 'nervousness': 3,
        'shy': 3, 'insecure': 3, 'judged': 4, 'staring': 3
    },
    'Low': {
        'calm': 5, 'relaxed': 5, 'happy': 5, 'confident': 5, 
        'peaceful': 5, 'comfortable': 5, 'positive': 5, 'enjoyed': 4, 
        'enjoy': 4, 'great': 4, 'good': 3, 'fine': 3, 'okay': 3, 'safe': 5
    }
}

def save_csv(path, words_dict, label):
    sorted_words = sorted(words_dict.items(), key=lambda x: (-x[1], x[0]))
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['word', 'label', 'weight'])
        writer.writeheader()
        for w, weight in sorted_words:
            writer.writerow({'word': w, 'label': label, 'weight': weight})

def build():
    base_dir = r"c:\Users\ragha\OneDrive\Desktop\Social_Anxiety_"
    high_path = os.path.join(base_dir, "high_anxiety_words.csv")
    mod_path = os.path.join(base_dir, "moderate_anxiety_words.csv")
    low_path = os.path.join(base_dir, "low_anxiety_words.csv")

    save_csv(high_path, STRICT_WORDS['High'], 'High')
    save_csv(mod_path, STRICT_WORDS['Moderate'], 'Moderate')
    save_csv(low_path, STRICT_WORDS['Low'], 'Low')
    print("Successfully built strictly-curated CSV dictionaries.")

if __name__ == "__main__":
    build()
