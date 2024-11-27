import requests
import pandas as pd
import string
from collections import Counter
import time

# Lista Europejskich jezykow razem z ich kodami na wiki
european_languages = {
    'en': 'English',
    'de': 'German',
    'fr': 'French',
    'es': 'Spanish',
    'it': 'Italian',
    'pl': 'Polish',
    'nl': 'Dutch',
    'pt': 'Portuguese',
    'sv': 'Swedish',
    'da': 'Danish',
    'no': 'Norwegian',
    'fi': 'Finnish',
    'cs': 'Czech',
    'hu': 'Hungarian',
    'el': 'Greek',
    'ro': 'Romanian',
    'bg': 'Bulgarian',
    'hr': 'Croatian',
    'sr': 'Serbian',
    'sl': 'Slovenian',
    'sk': 'Slovak',
    'lt': 'Lithuanian',
    'lv': 'Latvian',
    'et': 'Estonian',
    'ga': 'Irish',
    'is': 'Icelandic',
    'mt': 'Maltese',
    'sq': 'Albanian',
    'uk': 'Ukrainian',
    'be': 'Belarusian',
    'ru': 'Russian'
}


MIN_LETTERS = 1000
def fetch_random_articles_text(language_code, min_letters=MIN_LETTERS):
    base_url = f'https://{language_code}.wikipedia.org/w/api.php'
    session = requests.Session()
    texts = [] # tutaj wszystkie teksty ze wszystkich artykulow
    total_letters = 0
    
    while total_letters < min_letters:
        params_random = {
            'action': 'query',
            'list': 'random',
            'rnnamespace': 0,  # 0 czyli tylko artykoly
            'rnlimit': 1,
            'format': 'json',
        }
        try:
            response = session.get(url=base_url, params=params_random)
            data = response.json()
            page_id = data['query']['random'][0]['id']
        except (KeyError, requests.exceptions.RequestException):
            continue  # If can't get page id, skip
        
        # content ze stronki
        params_content = {
            'action': 'query',
            'prop': 'extracts',
            'explaintext': True,
            'pageids': page_id,
            'format': 'json',
        }
        try:
            response = session.get(url=base_url, params=params_content)
            data = response.json()
            page = data['query']['pages'][str(page_id)]
            text = page.get('extract', '')
            if text:
                texts.append(text)
                # Update wszystkich liter
                letters = [char for char in text.lower() if char.isalpha()]
                total_letters += len(letters)
        except (KeyError, requests.exceptions.RequestException):
            continue  # Jak nie ma tekstu to pomijam
        
        time.sleep(0.1)  # Zwalniamy zeby nas serwery nie zblokowaly 
    return texts

# Funkcja zwraca nam dict z czestotliwoscia dla text
def count_letters(text):
    # sortujemy tylko zeby byly litery i wszystko do downcase'u
    text = text.lower()
    letters = [char for char in text if char.isalpha()] # isAlpha sprawdza czy litery sa w alfabecie
    letter_counts = Counter(letters)
    total_letters = sum(letter_counts.values())
    # kalkulacja czestotliwosci 
    letter_freq = {letter: count / total_letters for letter, count in letter_counts.items()} # moze sie przydac https://stackoverflow.com/questions/10635669/how-do-i-calculate-letter-frequency-percentage
    return letter_freq

# Main code
min_letters_per_language = MIN_LETTERS # Globalna zmienna ( na gorze pliku )
all_letters = set() # z dokumentacji (A set in Python is an unordered collection of unique elements), czyli zaczynamu pusty set 
rows = []

for lang_code, lang_name in european_languages.items():
    print(f'Processing language: {lang_name}')
    texts = fetch_random_articles_text(lang_code, min_letters=min_letters_per_language)
    if not texts:
        print(f'No texts retrieved for {lang_name}')
        continue
    # sumujemy teksty
    combined_text = ' '.join(texts)
    letter_freq = count_letters(combined_text)
    all_letters.update(letter_freq.keys())
    row = {'Language': lang_name}
    row.update(letter_freq)
    rows.append(row)

# Tworze dataframe z rowsow
df = pd.DataFrame(rows)
df = df.fillna(0) # uzupelniam braki zerem,, https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html

# Ensure all letters are present in the DataFrame columns
all_letters = sorted(all_letters)
columns_order = ['Language'] + all_letters
df = df[columns_order]

# zapisujemy w csv nasz dataframe
df.to_csv('letter_frequencies.csv', index=False)

print('Data collection complete. The letter frequencies have been saved to "letter_frequencies.csv".')
