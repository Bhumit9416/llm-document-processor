import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class QueryParser:
    """Parser for extracting structured information from natural language queries"""
    
    def __init__(self):
        self.model = os.getenv("LLM_MODEL", "gpt-4")
    
    def parse(self, query: str) -> Dict[str, Any]:
        """Parse a natural language query to extract structured information
        
        Args:
            query: The natural language query string
            
        Returns:
            Dict containing structured information extracted from the query
        """
        # Define the system prompt for the LLM
        system_prompt = """
        You are an expert query parser for an insurance document processing system. 
        Your task is to extract structured information from natural language queries about insurance policies.
        
        Extract the following information (if present):
        - Age: The age of the person (e.g., 46, 30, etc.)
        - Gender: The gender of the person (e.g., male, female)
        - Procedure: The medical procedure or treatment mentioned (e.g., knee surgery, cataract surgery)
        - Location: The location where the procedure is performed or the person resides
        - Policy Duration: How long the policy has been active (e.g., 3 months, 2 years)
        - Policy Type: The type of insurance policy mentioned
        - Query Type: The type of question being asked (e.g., coverage, conditions, waiting period)
        - Other: Any other relevant information
        
        Return the extracted information in a structured JSON format.
        """
        
        # Call the LLM to parse the query
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.1,  # Low temperature for more deterministic outputs
                max_tokens=500
            )
            
            # Extract the response content
            content = response.choices[0].message.content
            
            # Try to parse the JSON response
            try:
                parsed_data = json.loads(content)
                return parsed_data
            except json.JSONDecodeError:
                # If the response is not valid JSON, try to extract structured data using regex or other methods
                return self._fallback_parsing(content, query)
                
        except Exception as e:
            # Fallback to basic parsing if the LLM call fails
            return self._fallback_parsing("", query)
    
    def _fallback_parsing(self, llm_response: str, query: str) -> Dict[str, Any]:
        """Fallback method for parsing when the LLM response is not valid JSON
        
        Args:
            llm_response: The raw response from the LLM
            query: The original query string
            
        Returns:
            Dict containing basic structured information extracted from the query
        """
        # Initialize the result dictionary with default values
        result = {
            "age": None,
            "gender": None,
            "procedure": None,
            "location": None,
            "policy_duration": None,
            "policy_type": None,
            "query_type": None,
            "other": None
        }
        
        # Basic parsing logic for common patterns
        # Age extraction (e.g., "46-year-old", "46M", "46 years")
        import re
        
        # Age pattern
        age_pattern = r'(\d+)[-\s]*(year|yr|y)[s\s-]*(old)?|^(\d+)[MF]'
        age_match = re.search(age_pattern, query, re.IGNORECASE)
        if age_match:
            result["age"] = age_match.group(1) or age_match.group(4)
        
        # Gender pattern
        if "male" in query.lower():
            result["gender"] = "male"
        elif "female" in query.lower():
            result["gender"] = "female"
        elif re.search(r'\d+M', query):
            result["gender"] = "male"
        elif re.search(r'\d+F', query):
            result["gender"] = "female"
        
        # Procedure pattern (common medical procedures)
        procedures = ["knee surgery", "cataract", "bypass", "transplant", "delivery", "cesarean", "appendectomy"]
        for proc in procedures:
            if proc in query.lower():
                result["procedure"] = proc
                break
        
        # Location pattern (common Indian cities)
        locations = ["mumbai", "delhi", "bangalore", "pune", "hyderabad", "chennai", "kolkata"]
        for loc in locations:
            if loc in query.lower():
                result["location"] = loc
                break
        
        # Policy duration pattern
        duration_pattern = r'(\d+)[-\s]*(month|year|day)[s\s-]*(old)?\s*(policy|insurance)'
        duration_match = re.search(duration_pattern, query, re.IGNORECASE)
        if duration_match:
            value = duration_match.group(1)
            unit = duration_match.group(2)
            result["policy_duration"] = f"{value} {unit}{'s' if int(value) > 1 else ''}"
        
        # Query type pattern
        if "cover" in query.lower() or "coverage" in query.lower():
            result["query_type"] = "coverage"
        elif "condition" in query.lower():
            result["query_type"] = "conditions"
        elif "waiting period" in query.lower():
            result["query_type"] = "waiting period"
        elif "exclusion" in query.lower():
            result["query_type"] = "exclusions"
        
        return result