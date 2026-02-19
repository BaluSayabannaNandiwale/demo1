"""
Objective Question Generator using Google Gemini AI
Generates multiple-choice questions from input text.
"""

import json
import re
import os
import time


def _select_gemini_model(genai, preferred_name: str | None = None):
    """
    Return a GenerativeModel using a name that exists for the current API/version.
    Fixes errors like: "models/gemini-pro is not found for API version v1beta".
    """
    # Candidate names to try first (order matters)
    candidates: list[str] = []
    env_name = os.getenv("GEMINI_MODEL")
    for n in [preferred_name, env_name]:
        if n and n not in candidates:
            candidates.append(n)

    # Common Gemini model ids seen across library versions
    for n in [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro",
        "models/gemini-2.0-flash",
        "models/gemini-1.5-flash",
        "models/gemini-1.5-pro",
        "models/gemini-pro",
    ]:
        if n not in candidates:
            candidates.append(n)

    # Prefer selecting from server-reported model list (most reliable)
    try:
        models = list(genai.list_models())
        available: list[str] = []
        for m in models:
            name = getattr(m, "name", None)
            if not name:
                continue
            methods = getattr(m, "supported_generation_methods", None) or []
            # Some SDKs use "generateContent"
            if methods and ("generateContent" not in methods):
                continue
            available.append(name)

        # If we got a list, pick best match
        if available:
            for cand in candidates:
                if cand in available:
                    return genai.GenerativeModel(cand)
                if not cand.startswith("models/") and f"models/{cand}" in available:
                    return genai.GenerativeModel(f"models/{cand}")

            # Otherwise pick the first Gemini-capable model
            for name in available:
                if "gemini" in name.lower():
                    return genai.GenerativeModel(name)

            # Fallback to first available
            return genai.GenerativeModel(available[0])
    except Exception:
        # If listing models fails, fall back to trying common names directly.
        pass

    last_err: Exception | None = None
    for cand in candidates:
        try:
            return genai.GenerativeModel(cand)
        except Exception as e:
            last_err = e
            continue

    raise last_err or RuntimeError("No usable Gemini model found.")


class ObjectiveTest:
    def __init__(self, text_content, no_of_questions, api_key=None):
        self.text_content = text_content
        self.no_of_questions = no_of_questions
        # Get API key from parameter, environment variable, or try Django settings
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            try:
                from django.conf import settings
                self.api_key = getattr(settings, 'GEMINI_API_KEY', None)
            except ImportError:
                pass
        
    def generate_test(self):
        """Generate objective (multiple-choice) questions using Gemini AI."""
        try:
            import google.generativeai as genai
            
            if not self.api_key:
                raise ValueError("Gemini API key not configured in settings.")
            
            # Configure Gemini API
            genai.configure(api_key=self.api_key)
            
            # Use an available Gemini model (auto-selected)
            model = _select_gemini_model(genai)
            
            # Create prompt for question generation
            prompt = f"""You are an expert educational content creator. Generate {self.no_of_questions} multiple-choice questions based on the following text.

Text content:
{self.text_content}

Requirements:
1. Generate exactly {self.no_of_questions} questions
2. Each question should have 4 options (A, B, C, D)
3. Only one option should be correct
4. Questions should test understanding of key concepts from the text
5. Make questions clear and unambiguous
6. Options should be plausible but only one correct answer

Format your response as JSON with this structure:
{{
    "questions": [
        {{
            "question": "Question text here?",
            "options": {{
                "A": "Option A text",
                "B": "Option B text",
                "C": "Option C text",
                "D": "Option D text"
            }},
            "correct_answer": "A"
        }}
    ]
}}

Return ONLY valid JSON, no additional text or explanation."""

            # Generate questions with retry logic for quota errors
            max_retries = 3
            retry_delay = 15  # Start with 15 seconds
            response_text = None
            
            for attempt in range(max_retries):
                try:
                    response = model.generate_content(prompt)
                    response_text = response.text.strip()
                    break  # Success, exit retry loop
                except Exception as e:
                    error_str = str(e)
                    
                    # Check if it's a quota/rate limit error
                    if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                        # Try to extract retry delay from error message
                        import re as re_module
                        delay_match = re_module.search(r'retry.*?(\d+(?:\.\d+)?)\s*s', error_str, re.IGNORECASE)
                        if delay_match:
                            retry_delay = float(delay_match.group(1)) + 2  # Add 2 seconds buffer
                        else:
                            retry_delay = retry_delay * (attempt + 1)  # Exponential backoff
                        
                        if attempt < max_retries - 1:
                            # Wait before retrying
                            time.sleep(min(retry_delay, 60))  # Cap at 60 seconds
                            continue
                        else:
                            # Last attempt failed, raise user-friendly error
                            raise Exception(
                                f"Gemini API quota exceeded. The free tier has limited requests per day/minute. "
                                f"Please wait {int(retry_delay)} seconds and try again, or upgrade your API plan. "
                                f"For more info: https://ai.google.dev/gemini-api/docs/rate-limits"
                            )
                    else:
                        # Not a quota error, raise immediately
                        raise
            
            if not response_text:
                raise Exception("Failed to generate response from Gemini AI after retries.")
            
            # Clean response - remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON response
            try:
                data = json.loads(response_text)
                questions = []
                answers = []
                
                for item in data.get("questions", []):
                    question_text = item.get("question", "")
                    options = item.get("options", {})
                    correct_answer = item.get("correct_answer", "A")
                    
                    # Format question with options
                    formatted_question = f"{question_text}\nA) {options.get('A', '')}\nB) {options.get('B', '')}\nC) {options.get('C', '')}\nD) {options.get('D', '')}"
                    questions.append(formatted_question)
                    
                    # Store correct answer
                    answers.append(options.get(correct_answer, ""))
                
                # Ensure we have the requested number of questions
                if len(questions) < self.no_of_questions:
                    # If AI didn't generate enough, pad with placeholder
                    while len(questions) < self.no_of_questions:
                        questions.append("Question could not be generated.")
                        answers.append("Answer not available.")
                elif len(questions) > self.no_of_questions:
                    # If AI generated too many, take only requested number
                    questions = questions[:self.no_of_questions]
                    answers = answers[:self.no_of_questions]
                
                return questions, answers
                
            except json.JSONDecodeError as e:
                # Fallback: try to extract questions manually
                return self._fallback_parse(response_text)
                
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        except Exception as e:
            raise Exception(f"Error generating questions with Gemini AI: {str(e)}")
    
    def _fallback_parse(self, text):
        """Fallback parser if JSON parsing fails."""
        questions = []
        answers = []
        
        # Try to extract questions using regex
        question_pattern = r'(\d+\.\s*[^?]+\?)'
        matches = re.findall(question_pattern, text)
        
        for i, match in enumerate(matches[:self.no_of_questions]):
            questions.append(match)
            answers.append(f"Answer {i+1}")
        
        # If still not enough, create placeholders
        while len(questions) < self.no_of_questions:
            questions.append(f"Question {len(questions) + 1} could not be generated.")
            answers.append("Answer not available.")
        
        return questions[:self.no_of_questions], answers[:self.no_of_questions]
