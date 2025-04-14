import os
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
from dotenv import load_dotenv
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create the improved prompt template for ad copy keyword extraction
example_prompt = """
[INST] Extract compelling keywords from the following ad copy:
"This revolutionary smartwatch stands out with its unique features like heart rate monitoring, sleep tracking, and water resistance. Ideal for fitness enthusiasts, it offers seamless health management. Act now and transform your lifestyle!"

List the keywords present in this document, separated by commas. Only return the keywords, nothing else. Rank them by importance, considering product features, target audience, benefits, and call to action. [/INST]
smartwatch, fitness, health management, heart rate monitoring, sleep tracking, water resistance, lifestyle, act now
"""

keyword_prompt = """
[INST] Extract compelling keywords from the following ad copy:
"[DOCUMENT]"

List the keywords present in this document, separated by commas. Only return the keywords, nothing else. Rank them by importance, considering product features, target audience, benefits, and call to action. [/INST]
"""

ad_copy_prompt = example_prompt + keyword_prompt

class KeywordExtractionView(APIView):
    def extract_keywords_using_openai(self, ad_copy):
        try:
            # Use the OpenAI chat completion
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": ad_copy_prompt},
                    {"role": "user", "content": ad_copy}
                ],
                max_tokens=150,
                temperature=0.7
            )

            # Access the response content correctly
            response_message = response.choices[0].message.content.strip()

            # Initialize KeyBERT model with appropriate LLM
            sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            kw_model = KeyBERT(model=sentence_model)
            
            # Extract keywords using KeyBERT
            keywords = kw_model.extract_keywords(response_message, 
                                                 keyphrase_ngram_range=(1, 2), 
                                                 stop_words='english', 
                                                 use_mmr=True, 
                                                 diversity=0.7)
            
            return [kw[0] for kw in keywords]
        
        except Exception as e:
            logging.error(f"Error in extract_keywords: {e}")
            return []

    def post(self, request):
        ad_copy = request.data.get('ad_copy')
        if not ad_copy:
            logging.warning(f"Missing ad_copy in request: {request.data}")
            return Response({"error": "Ad copy is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        keywords = self.extract_keywords_using_openai(ad_copy)
        if keywords:
            return Response({"keywords": keywords}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to extract keywords."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

