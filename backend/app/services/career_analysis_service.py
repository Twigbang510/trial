import json
import re
from typing import Dict, List, Tuple
import google.generativeai as genai

from app.core.config import settings
from app.core.prompts import career_analysis_prompt
from app.schemas.career_analysis import HollandScores, CareerSuggestion

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')


class CareerAnalysisService:
    """Career analysis service"""
    def __init__(self):
        self.vietnam_universities = [
            "Vietnam National University",
            "Ho Chi Minh City University of Technology", 
            "University of Economics HCMC",
            "Foreign Trade University",
            "FPT University",
            "University of Information Technology VNU-HCM",
            "University of Medicine and Pharmacy HCMC",
            "Hanoi Medical University",
            "Banking University HCMC",
            "University of Labor and Social Affairs",
            "RMIT University Vietnam",
            "Hue University of Medicine"
        ]
    
    def analyze_career_path(self, mbti_type: str, holland_scores: HollandScores) -> Dict:
        """Main method to analyze career path using Gemini AI"""
        
        holland_code = self._calculate_holland_code(holland_scores)
        
        try:
            prompt = self._create_enhanced_analysis_prompt(mbti_type, holland_scores, holland_code)
            
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1500,
                )
            )
            
            parsed_results = self._parse_gemini_response(response.text)
            
            parsed_results["holland_code"] = holland_code
            
            return parsed_results
            
        except Exception as e:
            print(f"Error in Gemini analysis with enhanced prompts: {str(e)}")
            return self._fallback_analysis(mbti_type, holland_code)
    
    def _calculate_holland_code(self, holland_scores: HollandScores) -> str:
        """Calculate Holland code from scores"""
        scores_dict = holland_scores.model_dump()
        
        sorted_scores = sorted(scores_dict.items(), key=lambda x: x[1], reverse=True)
        
        holland_mapping = {
            'realistic': 'R',
            'investigative': 'I', 
            'artistic': 'A',
            'social': 'S',
            'enterprising': 'E',
            'conventional': 'C'
        }
        
        top_codes = [holland_mapping[item[0]] for item in sorted_scores[:3] if item[1] > 0]
        
        return ''.join(top_codes[:3])
    
    def _create_analysis_prompt(self, mbti_type: str, holland_scores: HollandScores, holland_code: str) -> str:
        """Create comprehensive prompt for Gemini analysis"""
        
        holland_dict = holland_scores.model_dump()
        
        prompt = f"""
        You are a professional career counselor and psychologist. Analyze this person's career path based on their personality assessments:

        **MBTI Type:** {mbti_type}
        **Holland Interest Scores:**
        - Realistic: {holland_dict['realistic']}/100
        - Investigative: {holland_dict['investigative']}/100  
        - Artistic: {holland_dict['artistic']}/100
        - Social: {holland_dict['social']}/100
        - Enterprising: {holland_dict['enterprising']}/100
        - Conventional: {holland_dict['conventional']}/100
        
        **Holland Code:** {holland_code}

        Please provide a comprehensive career analysis in the following JSON format:

        {{
            "personality_summary": "A 2-3 sentence summary of their personality",
            "personality_traits": ["trait1", "trait2", "trait3", "trait4", "trait5"],
            "strengths": ["strength1", "strength2", "strength3", "strength4"],
            "growth_areas": ["area1", "area2", "area3"],
            "career_suggestions": [
                {{
                    "title": "Job Title",
                    "description": "Detailed description of the role and why it fits",
                    "match_percentage": 85,
                    "required_skills": ["skill1", "skill2", "skill3"],
                    "universities": ["University of Economics HCMC", "FPT University"],
                    "industry": "Technology",
                    "salary_range": "15-25 million VND"
                }}
            ],
            "detailed_analysis": "A comprehensive 3-4 paragraph analysis of their personality, strengths, and career fit",
            "recommendations": "Specific actionable recommendations for career development"
        }}

        **Important Guidelines:**
        1. Provide 4-6 career suggestions that genuinely match their MBTI + Holland combination
        2. Focus on careers available in Vietnam
        3. Include Vietnamese universities from this list when relevant: {', '.join(self.vietnam_universities)}
        4. Match percentages should be realistic (70-95%)
        5. Salary ranges should be in Vietnamese context (VND)
        6. Be specific and actionable in recommendations
        7. Consider both personality type and interest scores in suggestions

        Respond ONLY with the JSON format above, no additional text.
        """
        
        return prompt
    
    def _create_enhanced_analysis_prompt(self, mbti_type: str, holland_scores: HollandScores, holland_code: str) -> str:
        """Create prompt with improved structure"""
        
        holland_dict = holland_scores.model_dump()
        
        prompt = f"""
{career_analysis_prompt}

## User Data:
**MBTI Type:** {mbti_type}
**Holland Interest Scores:**
- Realistic: {holland_dict['realistic']}/100
- Investigative: {holland_dict['investigative']}/100  
- Artistic: {holland_dict['artistic']}/100
- Social: {holland_dict['social']}/100
- Enterprising: {holland_dict['enterprising']}/100
- Conventional: {holland_dict['conventional']}/100

**Holland Code:** {holland_code}

## Vietnamese Universities:
{', '.join(self.vietnam_universities)}

## Instructions:
Analyze this person's career path based on their MBTI type and Holland scores.
Focus on careers available in Vietnam and include relevant Vietnamese universities.
Provide realistic match percentages (70-95%) and salary ranges in VND context.

Please provide a comprehensive career analysis in the following JSON format:

{{
    "personality_summary": "A 2-3 sentence summary of their personality",
    "personality_traits": ["trait1", "trait2", "trait3", "trait4", "trait5"],
    "strengths": ["strength1", "strength2", "strength3", "strength4"],
    "growth_areas": ["area1", "area2", "area3"],
    "career_suggestions": [
        {{
            "title": "Job Title",
            "description": "Detailed description of the role and why it fits",
            "match_percentage": 85,
            "required_skills": ["skill1", "skill2", "skill3"],
            "universities": ["University of Economics HCMC", "FPT University"],
            "industry": "Technology",
            "salary_range": "15-25 million VND"
        }}
    ],
    "detailed_analysis": "A comprehensive 3-4 paragraph analysis of their personality, strengths, and career fit",
    "recommendations": "Specific actionable recommendations for career development"
}}

Respond ONLY with the JSON format above, no additional text.
"""
        
        return prompt
    
    def _extract_career_function_result(self, response) -> Dict:
        """Extract function call result from career analysis response"""
        try:
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        return part.function_call.args
            return {}
        except Exception as e:
            print(f"Career function call extraction failed: {e}")
            return {}
    
    def _parse_gemini_response(self, response_text: str) -> Dict:
        """Parse Gemini's JSON response"""
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                return self._validate_response(parsed)
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            print(f"Error parsing Gemini response: {str(e)}")
            print(f"Raw response: {response_text}")
            raise
    
    def _validate_response(self, response: Dict) -> Dict:
        """Validate and clean the parsed response"""
        
        required_fields = [
            "personality_summary", "personality_traits", "strengths", 
            "growth_areas", "career_suggestions", "detailed_analysis", "recommendations"
        ]
        
        for field in required_fields:
            if field not in response:
                response[field] = []
        
        if "career_suggestions" in response:
            validated_careers = []
            for career in response["career_suggestions"]:
                if isinstance(career, dict):
                    validated_career = {
                        "title": career.get("title", "Unknown Position"),
                        "description": career.get("description", ""),
                        "match_percentage": min(max(career.get("match_percentage", 75), 50), 100),
                        "required_skills": career.get("required_skills", []),
                        "universities": career.get("universities", []),
                        "industry": career.get("industry", ""),
                        "salary_range": career.get("salary_range", "")
                    }
                    validated_careers.append(validated_career)
            
            response["career_suggestions"] = validated_careers
        
        return response
    
    def _fallback_analysis(self, mbti_type: str, holland_code: str) -> Dict:
        """Fallback analysis if Gemini fails"""
        
        basic_analysis = {
            "personality_summary": f"Individual with {mbti_type} personality type and {holland_code} interests.",
            "personality_traits": ["Analytical", "Creative", "Communicative", "Goal-oriented"],
            "strengths": ["Problem-solving", "Communication", "Adaptability", "Team collaboration"],
            "growth_areas": ["Time management", "Technical skills", "Leadership development"],
            "career_suggestions": [
                {
                    "title": "Business Analyst",
                    "description": "Analyze business processes and recommend improvements.",
                    "match_percentage": 75,
                    "required_skills": ["Analytical thinking", "Communication", "Problem-solving"],
                    "universities": ["University of Economics HCMC", "Foreign Trade University"],
                    "industry": "Business",
                    "salary_range": "12-20 million VND"
                },
                {
                    "title": "Project Manager", 
                    "description": "Plan, execute, and oversee projects from start to finish.",
                    "match_percentage": 70,
                    "required_skills": ["Leadership", "Organization", "Communication"],
                    "universities": ["RMIT University Vietnam", "FPT University"],
                    "industry": "Technology",
                    "salary_range": "15-25 million VND"
                }
            ],
            "detailed_analysis": f"Based on your {mbti_type} personality type and {holland_code} Holland code, you show strong potential in analytical and communication-focused roles. Your personality indicates good problem-solving abilities and interpersonal skills.",
            "recommendations": "Focus on developing both technical and soft skills. Consider internships in your areas of interest and build a strong professional network."
        }
        
        return basic_analysis
    
    def generate_career_chat_response(self, analysis_id: int, user_question: str, career_context: Dict) -> str:
        """Generate contextual chat response about career analysis"""
        
        prompt = f"""
        You are a career counselor chatting with someone about their career analysis results.
        
        **Their Career Analysis Context:**
        - MBTI: {career_context.get('mbti_type', 'Unknown')}
        - Holland Code: {career_context.get('holland_code', 'Unknown')}
        - Top Career Suggestions: {', '.join([c['title'] for c in career_context.get('career_suggestions', [])[:3]])}
        
        **User's Question:** {user_question}
        
        Provide a helpful, personalized response that:
        1. References their specific career analysis results
        2. Answers their question directly
        3. Gives actionable advice
        4. Keeps a supportive, professional tone
        5. Limits response to 2-3 paragraphs
        
        If they ask about universities, mention Vietnamese institutions. If they ask about salaries, provide Vietnam context.
        """
        
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating career chat response: {e}")
            return f"I'd be happy to help you with career guidance! Could you tell me more about what specific aspect of your career path you'd like to explore?"


# Create singleton instance
career_analysis_service = CareerAnalysisService() 