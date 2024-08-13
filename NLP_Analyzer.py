import json
import requests
import sys

class CortexAnalyzer:
    def __init__(self):
        self.language_tool_url = 'https://api.languagetool.org/v2/check'
    
    def check_grammar(self, text):
        response = requests.post(self.language_tool_url, data={
            'text': text,
            'language': 'en-US'
        })
        response.raise_for_status()  # Ensure we notice bad responses
        return response.json()
    
    def is_suspicious(self, email_text, max_misspellings=3, max_percentage=2):
        result = self.check_grammar(email_text)
        misspelled_words = [match for match in result['matches'] if match['rule']['category']['id'] == 'TYPOS']
        
        word_count = len(email_text.split())
        misspelling_count = len(misspelled_words)
        misspelling_percentage = (misspelling_count / word_count) * 100
        
        if misspelling_count > max_misspellings or misspelling_percentage > max_percentage:
            return True
        return False
    
    def analyze_email(self, email_text):
        if self.is_suspicious(email_text):
            return {"status": "suspicious", "message": "Email contains too many spelling errors."}
        return {"status": "safe", "message": "Email is fine."}

if __name__ == "__main__":
    analyzer = CortexAnalyzer()
    
    # Read input from Cortex (ThePhish)
    input_data = sys.stdin.read()
    
    try:
        # Parse the JSON data provided by ThePhish
        data = json.loads(input_data)
        
        # Extract email text from the data
        email_text = data.get('email_text', '')
        
        # Perform the analysis
        result = analyzer.analyze_email(email_text)
        
        # Output the result in JSON format
        print(json.dumps(result))
    
    except json.JSONDecodeError:
        # Handle JSON parsing errors
        print(json.dumps({"error": "Invalid JSON input"}))
