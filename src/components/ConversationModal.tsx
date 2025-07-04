import { cn } from "@/lib/utils";
import { X } from "lucide-react";
import React, { useRef } from "react";
import { BottomSheet, BottomSheetRef } from "react-spring-bottom-sheet";
import "react-spring-bottom-sheet/dist/style.css";
import { ChatContainer } from "./ui/chat-container";
import { ChatMessage } from "@/hooks/useChat";

interface ConversationModalProps {
  open: boolean;
  onClose: () => void;
}

const ConversationModal: React.FC<ConversationModalProps> = ({
  open,
  onClose,
}) => {
  const bottomSheetRef = useRef<BottomSheetRef>(null);

  const handleNewMessage = (message: ChatMessage) => {
    // Handle any specific logic for new messages if needed
    console.log('New message received:', message);
  };

  const handleError = (error: Error) => {
    console.error('Chat error:', error);
  };

  return (
    <BottomSheet
      ref={bottomSheetRef}
      open={open}
      onDismiss={onClose}
      snapPoints={({ maxHeight }) => [maxHeight * 0.7, maxHeight * 0.9]}
      blocking={false}
      placeholder={<div className="h-16" />}
      onPointerEnterCapture={() => {}}
      onPointerLeaveCapture={() => {}}
    >
      <div className={cn("flex flex-col relative")}>
        {/* Close button */}
        <button
          className="absolute top-4 left-4 z-20 text-gray-400 hover:text-gray-700 p-2 rounded-full bg-white shadow-sm transition-colors duration-200"
          onClick={onClose}
          aria-label="Close"
        >
          <X width={24} height={24} />
        </button>

        {/* Chat Container */}
        <ChatContainer
          context="consultant"
          onNewMessage={handleNewMessage}
          onError={handleError}
          placeholder="Nhập câu hỏi của bạn..."
          showVoiceButton={true}
          variant="default"
          inputVariant="floating"
          emptyStateMessage="Chưa có tin nhắn nào"
          height="h-[50vh]"
          className="h-full"
        />
      </div>
    </BottomSheet>
  );
};

export default ConversationModal;
