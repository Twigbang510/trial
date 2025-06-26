import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '../ui/badge';
import { 
  MessageCircle, 
  Calendar, 
  GraduationCap, 
  Trash2, 
  Plus,
  Clock,
} from 'lucide-react';
import chatbotApi from '@/lib/api/chatbot.api';

interface Conversation {
  id: number;
  title: string | null;
  context: string;
  created_at: string;
  updated_at: string | null;
  message_count: number;
  last_message: string | null;
}

interface ConversationListProps {
  onSelectConversation: (conversationId: number) => void;
  onNewConversation: () => void;
  selectedConversationId?: number;
}

const ConversationList: React.FC<ConversationListProps> = ({
  onSelectConversation,
  onNewConversation,
  selectedConversationId
}) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setLoading(true);
      const data = await chatbotApi.getConversations();
      setConversations(data);
    } catch (error) {
      console.error('Error loading conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteConversation = async (conversationId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      const success = await chatbotApi.deleteConversation(conversationId);
      if (success) {
        setConversations(prev => prev.filter(conv => conv.id !== conversationId));
      }
    }
  };

  const getContextIcon = (context: string) => {
    switch (context) {
      case 'consultant':
        return <GraduationCap className="h-4 w-4" />;
      case 'booking':
        return <Calendar className="h-4 w-4" />;
      default:
        return <MessageCircle className="h-4 w-4" />;
    }
  };

  const getContextColor = (context: string) => {
    switch (context) {
      case 'consultant':
        return 'bg-blue-100 text-blue-600';
      case 'booking':
        return 'bg-green-100 text-green-600';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffInHours < 168) { // 7 days
      return date.toLocaleDateString([], { weekday: 'short' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  const truncateText = (text: string, maxLength: number = 50) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  if (loading) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageCircle className="h-5 w-5" />
            Conversations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <MessageCircle className="h-5 w-5" />
            Conversations
          </CardTitle>
          <Button
            onClick={onNewConversation}
            size="sm"
            variant="outline"
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[calc(100vh-300px)]">
          {conversations.length === 0 ? (
            <div className="text-center py-8">
              <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 mb-4">No conversations yet</p>
              <Button onClick={onNewConversation} size="sm">
                Start New Chat
              </Button>
            </div>
          ) : (
            <div className="space-y-2">
              {conversations.map((conversation) => (
                <div
                  key={conversation.id}
                  onClick={() => onSelectConversation(conversation.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition-colors hover:bg-gray-50 ${
                    selectedConversationId === conversation.id 
                      ? 'bg-blue-50 border-blue-200' 
                      : 'bg-white'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <div className={`p-1 rounded ${getContextColor(conversation.context)}`}>
                          {getContextIcon(conversation.context)}
                        </div>
                        <h4 className="font-medium text-sm truncate">
                          {conversation.title || 'New Conversation'}
                        </h4>
                        <Badge variant="secondary" className="text-xs">
                          {conversation.message_count} messages
                        </Badge>
                      </div>
                      
                      {conversation.last_message && (
                        <p className="text-gray-600 text-xs truncate mb-2">
                          {truncateText(conversation.last_message, 60)}
                        </p>
                      )}
                      
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <Clock className="h-3 w-3" />
                        <span>
                          {conversation.updated_at 
                            ? formatDate(conversation.updated_at)
                            : formatDate(conversation.created_at)
                          }
                        </span>
                      </div>
                    </div>
                    
                    <Button
                      onClick={(e) => handleDeleteConversation(conversation.id, e)}
                      size="sm"
                      variant="ghost"
                      className="text-gray-400 hover:text-red-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default ConversationList; 