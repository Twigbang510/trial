import axios from 'axios';
import { API_URL } from '@/config/app';

export interface HollandScores {
  realistic: number;
  investigative: number;
  artistic: number;
  social: number;
  enterprising: number;
  conventional: number;
}

export interface CareerSuggestion {
  title: string;
  description: string;
  match_percentage: number;
  required_skills: string[];
  universities: string[];
  industry?: string;
  salary_range?: string;
}

export interface CareerAnalysisRequest {
  mbti_type: string;
  holland_scores: HollandScores;
}

export interface CareerAnalysisResponse {
  id: number;
  mbti_type: string;
  holland_scores: Record<string, number>;
  holland_code?: string;
  personality_summary?: string;
  personality_traits?: string[];
  strengths?: string[];
  growth_areas?: string[];
  career_suggestions?: CareerSuggestion[];
  detailed_analysis?: string;
  recommendations?: string;
  created_at: string;
}

export interface CareerChatRequest {
  analysis_id: number;
  user_question: string;
  focus_area?: string;
}

export interface CareerChatResponse {
  response: string;
  analysis_id: number;
  context: string;
}

const CAREER_API_URL = `${API_URL}/api/v1/career-analysis`;

// Get auth headers for API requests
const getAuthHeaders = () => {
  try {
    const authStateStr = localStorage.getItem('auth_state');
    if (authStateStr) {
      const authState = JSON.parse(authStateStr);
      const token = authState.token;
      if (token) {
        return {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        };
      }
    }
  } catch (error) {
    console.warn('Failed to get auth headers:', error);
  }
  return {
    'Content-Type': 'application/json'
  };
};

class CareerAnalysisApi {
  /**
   * Create new career analysis using AI
   */
  async createAnalysis(data: CareerAnalysisRequest): Promise<CareerAnalysisResponse> {
    const response = await axios.post(`${CAREER_API_URL}/analyze`, data, {
      headers: getAuthHeaders(),
    });
    return response.data;
  }

  /**
   * Get all career analyses for current user
   */
  async getMyAnalyses(skip: number = 0, limit: number = 10): Promise<CareerAnalysisResponse[]> {
    const response = await axios.get(`${CAREER_API_URL}/my-analyses`, {
      params: { skip, limit },
      headers: getAuthHeaders(),
    });
    return response.data;
  }

  /**
   * Get latest career analysis for current user
   */
  async getLatestAnalysis(): Promise<CareerAnalysisResponse> {
    const response = await axios.get(`${CAREER_API_URL}/latest`, {
      headers: getAuthHeaders(),
    });
    return response.data;
  }

  /**
   * Get specific career analysis by ID
   */
  async getAnalysis(analysisId: number): Promise<CareerAnalysisResponse> {
    const response = await axios.get(`${CAREER_API_URL}/${analysisId}`, {
      headers: getAuthHeaders(),
    });
    return response.data;
  }

  /**
   * Chat about career analysis results
   */
  async chatAboutCareer(data: CareerChatRequest): Promise<CareerChatResponse> {
    const response = await axios.post(`${CAREER_API_URL}/chat`, data, {
      headers: getAuthHeaders(),
    });
    return response.data;
  }
}

// Export singleton instance
const careerAnalysisApi = new CareerAnalysisApi();
export default careerAnalysisApi; 