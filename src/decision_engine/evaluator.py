import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class DecisionEvaluator:
    """Evaluator for making decisions based on retrieved clauses"""
    
    def __init__(self):
        self.model = os.getenv("LLM_MODEL", "gpt-4")
    
    def evaluate(self, query: Dict[str, Any], clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate a decision based on the query and retrieved clauses
        
        Args:
            query: The structured query dictionary
            clauses: List of relevant clauses with their metadata
            
        Returns:
            Dict containing the decision, amount, and justification
        """
        # Format the clauses for the prompt
        formatted_clauses = self._format_clauses(clauses)
        
        # Format the query for the prompt
        formatted_query = self._format_query(query)
        
        # Define the system prompt for the LLM
        system_prompt = """
        You are an expert insurance policy evaluator. Your task is to evaluate whether a claim or query is covered under the policy based on the relevant clauses provided.
        
        You will be given:
        1. A query about an insurance policy
        2. Relevant clauses from the policy document
        
        Your job is to:
        1. Determine if the query is covered under the policy based on the clauses
        2. If applicable, determine the amount covered
        3. Provide a clear justification for your decision, citing specific clauses
        
        Return your evaluation in the following JSON format:
        {
            "decision": "APPROVED" or "REJECTED" or "PARTIAL" or "INFORMATION_NEEDED",
            "amount": numeric value if applicable, otherwise null,
            "justification": {
                "reason": "Clear explanation of the decision",
                "clause_references": ["List of specific clause references used"]
            }
        }
        
        Be precise, factual, and base your decision strictly on the provided clauses.
        """
        
        # User prompt with the query and clauses
        user_prompt = f"""
        QUERY:
        {formatted_query}
        
        RELEVANT CLAUSES:
        {formatted_clauses}
        
        Based on the above information, evaluate whether the query is covered under the policy.
        Provide your decision, amount (if applicable), and justification in the specified JSON format.
        """
        
        # Call the LLM to evaluate the decision
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for more deterministic outputs
                max_tokens=1000
            )
            
            # Extract the response content
            content = response.choices[0].message.content
            
            # Try to parse the JSON response
            try:
                decision_data = json.loads(content)
                return decision_data
            except json.JSONDecodeError:
                # If the response is not valid JSON, try to extract structured data
                return self._fallback_evaluation(content, query, clauses)
                
        except Exception as e:
            # Fallback to basic evaluation if the LLM call fails
            return self._fallback_evaluation("", query, clauses)
    
    def _format_clauses(self, clauses: List[Dict[str, Any]]) -> str:
        """Format the clauses for the prompt
        
        Args:
            clauses: List of relevant clauses with their metadata
            
        Returns:
            Formatted string of clauses
        """
        formatted = ""
        
        for i, clause in enumerate(clauses):
            # Extract the clause text and source
            clause_text = clause["clause"]
            source = clause["source"]
            score = clause.get("score", 0.0)
            
            # Format the clause with its source and relevance score
            formatted += f"Clause {i+1} [Source: {source}, Relevance: {score:.2f}]:\n{clause_text}\n\n"
        
        return formatted
    
    def _format_query(self, query: Dict[str, Any]) -> str:
        """Format the query for the prompt
        
        Args:
            query: The structured query dictionary
            
        Returns:
            Formatted string of the query
        """
        formatted = ""
        
        # Add the original query if available
        if "original_query" in query:
            formatted += f"Original Query: {query['original_query']}\n\n"
        
        # Add the structured information
        formatted += "Structured Information:\n"
        
        if query.get("age"):
            formatted += f"- Age: {query['age']}\n"
        
        if query.get("gender"):
            formatted += f"- Gender: {query['gender']}\n"
        
        if query.get("procedure"):
            formatted += f"- Procedure: {query['procedure']}\n"
        
        if query.get("location"):
            formatted += f"- Location: {query['location']}\n"
        
        if query.get("policy_duration"):
            formatted += f"- Policy Duration: {query['policy_duration']}\n"
        
        if query.get("policy_type"):
            formatted += f"- Policy Type: {query['policy_type']}\n"
        
        if query.get("query_type"):
            formatted += f"- Query Type: {query['query_type']}\n"
        
        return formatted
    
    def _fallback_evaluation(self, llm_response: str, query: Dict[str, Any], clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback method for evaluation when the LLM response is not valid JSON
        
        Args:
            llm_response: The raw response from the LLM
            query: The structured query dictionary
            clauses: List of relevant clauses with their metadata
            
        Returns:
            Dict containing a basic decision, amount, and justification
        """
        # Initialize the result dictionary with default values
        result = {
            "decision": "INFORMATION_NEEDED",
            "amount": None,
            "justification": {
                "reason": "Unable to make a definitive decision based on the provided information.",
                "clause_references": []
            }
        }
        
        # If we have clauses, try to extract some basic information
        if clauses:
            # Extract clause references
            clause_references = [f"Clause from {clause['source']}" for clause in clauses[:3]]
            result["justification"]["clause_references"] = clause_references
            
            # Check for common keywords in the clauses
            combined_clauses = " ".join([clause["clause"] for clause in clauses])
            combined_clauses_lower = combined_clauses.lower()
            
            # Check for coverage indications
            if "covered" in combined_clauses_lower and not "not covered" in combined_clauses_lower:
                result["decision"] = "APPROVED"
                result["justification"]["reason"] = "The procedure appears to be covered based on the policy clauses."
            elif "not covered" in combined_clauses_lower or "excluded" in combined_clauses_lower:
                result["decision"] = "REJECTED"
                result["justification"]["reason"] = "The procedure appears to be excluded based on the policy clauses."
            
            # Check for waiting period
            import re
            waiting_period_match = re.search(r'waiting period of (\d+)', combined_clauses_lower)
            if waiting_period_match:
                period = waiting_period_match.group(1)
                result["justification"]["reason"] += f" There is a waiting period of {period} mentioned in the policy."
        
        return result