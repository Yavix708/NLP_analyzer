import requests
import email
from email import policy
from email.parser import BytesParser
from cortexutils.analyzer import Analyzer


class NLPAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
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

    def extract_email_content(self, eml_file_path):
        # Read the .eml file
        with open(eml_file_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)

        # Extract email body (text/plain or text/html)
        email_body = None
        if msg.is_multipart():
            for part in msg.iter_parts():
                if part.get_content_type() == 'text/plain':
                    email_body = part.get_payload(decode=True).decode(part.get_content_charset())
                    break
        else:
            email_body = msg.get_payload(decode=True).decode(msg.get_content_charset())

        return email_body

    def run(self):
        # Extract the data passed by Cortex
        try:
            file_data = self.get_data()
            eml_file_path = file_data['data']
        except KeyError:
            self.error("No data found in the file.")

        # Extract the email content
        email_text = self.extract_email_content(eml_file_path)

        if not email_text:
            self.error("No email content found")

        # Analyze the email content
        if self.is_suspicious(email_text):
            self.report({"status": "suspicious", "message": "Email contains too many spelling errors."})
        else:
            self.report({"status": "safe", "message": "Email is fine."})


if __name__ == "__main__":
    NLPAnalyzer().run()
