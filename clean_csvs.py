import csv
import os

# Define words that are strictly prohibited due to their lack of emotional value
STOPWORDS = {
    'feel', 'get', 'make', 'time', 'day', 'thing', 'people', 'friend', 'kind', 'like', 
    'do', 'have', 'something', 'really', 'very', 'know', 'go', 'think', 'say', 'want',
    'would', 'could', 'should', 'good', 'bad', 'much', 'well', 'see', 'come', 'look', 
    'way', 'even', 'new', 'use', 'back', 'just', 'also'
}

REQUIRED_WORDS = {
    'High': ['panic', 'nervous', 'sweating', 'racing', 'fear', 'overwhelmed', 'breathless'],
    'Moderate': ['uneasy', 'unsure', 'awkward', 'hesitant'],
    'Low': ['calm', 'relaxed', 'happy', 'confident']
}

def load_csv(path):
    words = {}
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row['word'].strip().lower()
                weight = int(row['weight'])
                words[word] = weight
    return words

def save_csv(path, words, label):
    sorted_words = sorted(words.items(), key=lambda x: (-x[1], x[0]))
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['word', 'label', 'weight'])
        writer.writeheader()
        for w, weight in sorted_words:
            writer.writerow({'word': w, 'label': label, 'weight': weight})

def clean():
    base_dir = r"c:\Users\ragha\OneDrive\Desktop\Social_Anxiety_"
    high_path = os.path.join(base_dir, "high_anxiety_words.csv")
    mod_path = os.path.join(base_dir, "moderate_anxiety_words.csv")
    low_path = os.path.join(base_dir, "low_anxiety_words.csv")

    high_words = load_csv(high_path)
    mod_words = load_csv(mod_path)
    low_words = load_csv(low_path)

    # Intersection (even if run on already cleaned files, intersection is empty now)
    intersection = set(high_words.keys()) & set(mod_words.keys()) & set(low_words.keys())
    
    # Also explicitly whitelist REQUIRED_WORDS so they are never dropped
    whitelist = set(REQUIRED_WORDS['High'] + REQUIRED_WORDS['Moderate'] + REQUIRED_WORDS['Low'])
    words_to_remove = (intersection | STOPWORDS) - whitelist

    def process_dict(d, required_list):
        cleaned = {k: v for k, v in d.items() if k not in words_to_remove and len(k) > 2}
        # Force inject required words with max weight 5
        for rw in required_list:
            cleaned[rw] = 5
        return cleaned

    high_cleaned = process_dict(high_words, REQUIRED_WORDS['High'])
    mod_cleaned = process_dict(mod_words, REQUIRED_WORDS['Moderate'])
    low_cleaned = process_dict(low_words, REQUIRED_WORDS['Low'])

    save_csv(high_path, high_cleaned, 'High')
    save_csv(mod_path, mod_cleaned, 'Moderate')
    save_csv(low_path, low_cleaned, 'Low')
    print("Sucessfully purged generic stopwords and injected strict required words.")

if __name__ == "__main__":
    clean()
