import { cn } from "@/lib/utils";
import { Mic, SendHorizonal, X } from "lucide-react";
import React, { useCallback, useEffect, useRef, useState } from "react";
import { BottomSheet, BottomSheetRef } from "react-spring-bottom-sheet";
import "react-spring-bottom-sheet/dist/style.css";
import { ChatbotIcon } from "./icons/ChatbotIcon";
import chatbotApi from "@/lib/api/chatbot.api";

interface ConversationModalProps {
  open: boolean;
  onClose: () => void;
}

interface Message {
  text: string;
  isBot: boolean;
  timestamp?: Date;
}

const ConversationModal: React.FC<ConversationModalProps> = ({
  open,
  onClose,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [clientId, setClientId] = useState<string>();

  const bottomSheetRef = useRef<BottomSheetRef>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    if (!clientId) {
      await getClientId();
    }

    setInputValue("");

    const newMessage: Message = {
      text: inputValue,
      isBot: false,
      timestamp: new Date(),
    };

    setMessages([...messages, newMessage]);
    setIsLoading(true);

    const { content } = await chatbotApi.chat(inputValue, clientId!);

    const botResponse: Message = {
      text: content,
      isBot: true,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, botResponse]);
    setIsLoading(false);
  };

  const getClientId = useCallback(async () => {
    if (clientId) return;

    const id = await chatbotApi.getClientId();
    if (!id) {
      console.error("Failed to get client ID");
      return;
    }

    setClientId(id);
  }, [clientId]);

  useEffect(() => {
    if (containerRef.current) {
      const lastMessage =
        containerRef.current.lastElementChild?.lastElementChild;
      lastMessage?.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }, [messages]);

  useEffect(() => {
    getClientId();
  }, []);

  return (
    <BottomSheet
      ref={bottomSheetRef}
      open={open}
      onDismiss={onClose}
      snapPoints={({ maxHeight }) => [maxHeight * 0.7, maxHeight * 0.9]}
      blocking={false}
    >
      <div className={cn("flex flex-col relative ")}>
        <div className="fixed top-4 left-0 right-0 z-10 px-5 py-4 border-b flex items-center space-x-2 bg-gradient-to-r from-green-100 to-green-50">
          <button
            className="text-gray-400 hover:text-gray-700 p-2 rounded-full bg-transparent transition-colors duration-200"
            onClick={onClose}
            aria-label="Close"
          >
            <X width={24} height={24} />
          </button>

          <div className="w-10 h-10  flex items-center justify-center fill-green-500">
            <ChatbotIcon className="w-8 h-8" />
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-gray-800">AIBot</h2>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
              <span className="text-sm font-medium text-green-600">Online</span>
            </div>
          </div>
        </div>

        <div className="flex-1 bg-gradient-to-b h-full pt-24 px-4">
          <div className="h-[50vh] overflow-y-auto" ref={containerRef}>
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-gray-500 space-y-4">
                <svg
                  className="w-16 h-16 text-gray-300"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z" />
                </svg>
                <p className="text-sm font-medium">Chưa có tin nhắn nào</p>
                <p className="text-xs opacity-75">
                  Hãy bắt đầu cuộc trò chuyện!
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${
                      message.isBot ? "flex-row" : "flex-row-reverse"
                    } items-end gap-2 animate-fadeIn`}
                  >
                    {message.isBot && (
                      <div className="w-10 h-10  flex items-center justify-center fill-green-500">
                        <ChatbotIcon className="w-8 h-8" />
                      </div>
                    )}
                    <div
                      className={`max-w-[80%] px-5 py-3 shadow-sm ${
                        message.isBot
                          ? "bg-gray-100 text-gray-800 border border-gray-100 rounded-tl-2xl rounded-tr-2xl rounded-br-2xl"
                          : "bg-gradient-to-r from-green-500 to-green-600 text-white rounded-tl-2xl rounded-tr-2xl rounded-bl-2xl"
                      } transform transition-all duration-200 hover:shadow-md`}
                    >
                      {message.text}
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex flex-row items-end gap-2 animate-fadeIn">
                    <div className="w-10 h-10 flex items-center justify-center fill-green-500">
                      <ChatbotIcon className="w-8 h-8" />
                    </div>
                    <div className="max-w-[80%] px-5 py-3 shadow-sm bg-gray-100 text-gray-800 border border-gray-100 rounded-tl-2xl rounded-tr-2xl rounded-br-2xl">
                      <div className="flex items-center space-x-1">
                        <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                        <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse delay-150"></span>
                        <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse delay-300"></span>
                      </div>
                    </div>
                  </div>
                )}
                <div id="message-anchor" className="h-16" />
              </div>
            )}
          </div>
        </div>

        <div className="fixed bottom-0 left-0 right-0 z-10 bg-transparent">
          <form onSubmit={handleSubmit} className="px-5 py-4">
            <div className="flex gap-3 items-center bg-white rounded-full p-2  shadow-[0_3px_10px_rgb(0,0,0,0.2)]">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                className="flex-1 bg-transparent border-none px-3 py-2 text-sm focus:outline-none placeholder:text-gray-400"
                placeholder="Nhập câu hỏi của bạn..."
              />

              <div className="flex flex-row justify-center items-center space-x-2 mr-2">
                <button
                  type="button"
                  className="hover:text-green-500 transition-colors duration-200 bg-transparent"
                  aria-label="Voice input"
                >
                  <Mic
                    width={24}
                    height={24}
                    className="stroke-1 hover:stroke-2 transition-all"
                  />
                </button>

                <button
                  type="submit"
                  className={cn(
                    "p-2 rounded-full transition-all duration-200 bg-transparent",
                    !inputValue.trim() && "cursor-not-allowed opacity-50"
                  )}
                  disabled={!inputValue.trim()}
                  aria-label="Send message"
                >
                  <SendHorizonal
                    width={24}
                    height={24}
                    className={cn(
                      "transition-all duration-200",
                      "stroke-2",
                      inputValue.trim()
                        ? "text-green-500 fill-green-300  hover:scale-110"
                        : "text-gray-300"
                    )}
                  />
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </BottomSheet>
  );
};

export default ConversationModal;
