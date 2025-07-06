"""
Function calling definitions for AI processing (LEGACY - NOT USED)
Based on TrialResponse architecture but adapted for current backend
Note: This file is kept for reference but function calling is not used due to Gemini API version limitations
"""

# Booking intent classification function
booking_intent_classifier_function = {
    "name": "classify_booking_intent",
    "description": "Classifies user's booking message into intent categories and extracts key information",
    "parameters": {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
                "description": "User's booking intent classification",
                "enum": ["A", "C", "O"]
            },
            "safety_score": {
                "type": "integer",
                "description": "User's safety/engagement score (1-99)",
                "minimum": 1,
                "maximum": 99
            },
            "is_rejection": {
                "type": "boolean",
                "description": "Whether user is rejecting the booking"
            },
            "is_confirmation": {
                "type": "boolean", 
                "description": "Whether user is confirming a time slot"
            },
            "input_slots": {
                "type": "array",
                "description": "Specific time slots mentioned by user (HH:MM format)",
                "items": {
                    "type": "string",
                    "pattern": "^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
                }
            },
            "time_range": {
                "type": "array",
                "description": "Time range mentioned by user [start_time, end_time]",
                "items": {
                    "type": "string",
                    "pattern": "^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
                },
                "maxItems": 2
            },
            "date": {
                "type": "string",
                "description": "Target date in YYYY-MM-DD format",
                "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
            },
            "reasoning": {
                "type": "string",
                "description": "Explanation for the classification"
            }
        },
        "required": ["intent", "safety_score", "is_rejection", "is_confirmation", "reasoning"]
    }
}

# Time extraction function
time_extractor_function = {
    "name": "extract_time_information",
    "description": "Extracts time-related information from user message",
    "parameters": {
        "type": "object",
        "properties": {
            "time_slots": {
                "type": "array",
                "description": "Specific time slots mentioned (HH:MM format)",
                "items": {
                    "type": "object",
                    "properties": {
                        "time": {"type": "string", "pattern": "^([01]?[0-9]|2[0-3]):[0-5][0-9]$"},
                        "date": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"}
                    },
                    "required": ["time"]
                }
            },
            "unavailable_slots": {
                "type": "array",
                "description": "Time slots user cannot attend",
                "items": {
                    "type": "object",
                    "properties": {
                        "time": {"type": "string", "pattern": "^([01]?[0-9]|2[0-3]):[0-5][0-9]$"},
                        "date": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"}
                    },
                    "required": ["time"]
                }
            },
            "dates": {
                "type": "array",
                "description": "Dates mentioned by user (YYYY-MM-DD)",
                "items": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                }
            },
            "times": {
                "type": "array",
                "description": "Times mentioned by user (HH:MM)",
                "items": {
                    "type": "string",
                    "pattern": "^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
                }
            },
            "time_range": {
                "type": "object",
                "description": "Time range specification",
                "properties": {
                    "min_date": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
                    "min_time": {"type": "string", "pattern": "^([01]?[0-9]|2[0-3]):[0-5][0-9]$"},
                    "max_date": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
                    "max_time": {"type": "string", "pattern": "^([01]?[0-9]|2[0-3]):[0-5][0-9]$"}
                }
            },
            "is_slot_accepted": {
                "type": "boolean",
                "description": "Whether user accepted any suggested time slots"
            },
            "reasoning": {
                "type": "string",
                "description": "Explanation for extracted values"
            }
        },
        "required": ["time_slots", "unavailable_slots", "dates", "times", "time_range", "is_slot_accepted", "reasoning"]
    }
}

# Moderation function
moderation_function = {
    "name": "moderate_content",
    "description": "Checks if user message is potentially harmful or inappropriate",
    "parameters": {
        "type": "object",
        "properties": {
            "flagged": {
                "type": "boolean",
                "description": "Whether the message should be flagged"
            },
            "harmful_score": {
                "type": "integer",
                "description": "Harm level score (0-100)",
                "minimum": 0,
                "maximum": 100
            },
            "violation_type": {
                "type": "string",
                "description": "Type of violation if any",
                "enum": ["none", "inappropriate", "spam", "harassment", "other"]
            },
            "reasoning": {
                "type": "string",
                "description": "Explanation for moderation decision"
            }
        },
        "required": ["flagged", "harmful_score", "violation_type", "reasoning"]
    }
}

# Career analysis function
career_analysis_function = {
    "name": "analyze_career_path",
    "description": "Analyzes user's career path based on MBTI and Holland scores",
    "parameters": {
        "type": "object",
        "properties": {
            "personality_summary": {
                "type": "string",
                "description": "Summary of personality traits"
            },
            "holland_code": {
                "type": "string",
                "description": "Top 3 Holland codes (e.g., 'RIAS')"
            },
            "career_suggestions": {
                "type": "array",
                "description": "List of career suggestions",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "match_percentage": {"type": "integer", "minimum": 0, "maximum": 100},
                        "required_skills": {"type": "array", "items": {"type": "string"}},
                        "universities": {"type": "array", "items": {"type": "string"}},
                        "industry": {"type": "string"},
                        "salary_range": {"type": "string"}
                    },
                    "required": ["title", "description", "match_percentage"]
                }
            },
            "personality_traits": {
                "type": "array",
                "description": "Key personality traits",
                "items": {"type": "string"}
            },
            "strengths": {
                "type": "array",
                "description": "User's strengths",
                "items": {"type": "string"}
            },
            "growth_areas": {
                "type": "array",
                "description": "Areas for improvement",
                "items": {"type": "string"}
            },
            "detailed_analysis": {
                "type": "string",
                "description": "Detailed career analysis"
            },
            "recommendations": {
                "type": "string",
                "description": "Specific recommendations"
            }
        },
        "required": ["personality_summary", "holland_code", "career_suggestions", "personality_traits", "strengths", "growth_areas"]
    }
} 