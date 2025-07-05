#!/usr/bin/env python3

import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app.main import app

# Initialize TestClient with the app
client = TestClient(app)

class TestChatbotAPI:
    """Test chatbot API endpoints"""
    
    def test_chat_endpoint_exists(self):
        """Test that chat endpoint is accessible"""
        response = client.post("/api/v1/chatbot/chat", json={
            "message": "Hello",
            "context": "consultant"
        })
        # Should not return 404
        assert response.status_code != 404
    
    def test_chat_general_question(self):
        """Test general question fallback to AI"""
        response = client.post("/api/v1/chatbot/chat", json={
            "message": "What is AI?",
            "context": "consultant"
        })
        
        if response.status_code == 200:
            data = response.json()
            assert "response" in data
            assert len(data["response"]) > 0
            # Should not have booking options for general questions
            assert data.get("booking_options", []) == []
    
    def test_chat_booking_question(self):
        """Test booking-related question"""
        response = client.post("/api/v1/chatbot/chat", json={
            "message": "book lịch 8h",
            "context": "consultant"
        })
        
        if response.status_code == 200:
            data = response.json()
            assert "response" in data
            assert "conversation_id" in data
    
    def test_conversation_endpoints(self):
        """Test conversation management endpoints"""
        # Test get conversations (should require auth)
        response = client.get("/api/v1/chatbot/conversations")
        assert response.status_code in [401, 403]  # Should require authentication
    
    def test_invalid_requests(self):
        """Test invalid request handling"""
        # Empty message
        response = client.post("/api/v1/chatbot/chat", json={})
        assert response.status_code == 422  # Validation error
        
        # Missing required fields
        response = client.post("/api/v1/chatbot/chat", json={
            "context": "consultant"
        })
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__]) 