import React, { useRef, useState } from "react";
import ConversationModal from "./ConversationModal";
import { ChatbotIcon } from "./icons/ChatbotIcon";

const BUTTON_SIZE = 56;

interface ChatButtonProps {}

const ChatButton: React.FC<ChatButtonProps> = () => {
  const [position, setPosition] = useState({
    x: window.innerWidth - 96,
    y: window.innerHeight - 96,
  });
  const [dragging, setDragging] = useState(false);
  const [showConversationModal, setShowConversationModal] = useState(false);

  const offset = useRef({ x: 0, y: 0 });
  const dragStart = useRef({ x: 0, y: 0 });

  const handleStart = (clientX: number, clientY: number) => {
    setDragging(true);
    offset.current = {
      x: clientX - position.x,
      y: clientY - position.y,
    };
    dragStart.current = { x: clientX, y: clientY };
    document.body.style.userSelect = "none";
  };

  const handleMove = (clientX: number, clientY: number) => {
    if (!dragging) return;
    setPosition({
      x: clientX - offset.current.x,
      y: clientY - offset.current.y,
    });
  };

  const handleEnd = (clientX?: number, clientY?: number) => {
    setDragging(false);
    document.body.style.userSelect = "";
    // Only treat as click if pointer did not move significantly
    if (
      clientX &&
      clientY &&
      Math.abs(clientX - dragStart.current.x) < 5 &&
      Math.abs(clientY - dragStart.current.y) < 5
    ) {
      setShowConversationModal(true);
    }
  };

  // Mouse event handlers
  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    handleStart(e.clientX, e.clientY);
  };

  const handleMouseMove = (e: MouseEvent) => {
    handleMove(e.clientX, e.clientY);
  };

  const handleMouseUp = (e: MouseEvent) => {
    handleEnd(e.clientX, e.clientY);
  };

  // Touch event handlers
  const handleTouchStart = (e: React.TouchEvent<HTMLDivElement>) => {
    const touch = e.touches[0];
    handleStart(touch.clientX, touch.clientY);
  };

  const handleTouchMove = (e: TouchEvent) => {
    const touch = e.touches[0];
    handleMove(touch.clientX, touch.clientY);
  };

  const handleTouchEnd = (e: TouchEvent) => {
    if (e.changedTouches.length > 0) {
      const touch = e.changedTouches[0];
      handleEnd(touch.clientX, touch.clientY);
    } else {
      handleEnd();
    }
  };

  React.useEffect(() => {
    if (dragging) {
      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
      window.addEventListener("touchmove", handleTouchMove);
      window.addEventListener("touchend", handleTouchEnd);
    } else {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
      window.removeEventListener("touchmove", handleTouchMove);
      window.removeEventListener("touchend", handleTouchEnd);
    }
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
      window.removeEventListener("touchmove", handleTouchMove);
      window.removeEventListener("touchend", handleTouchEnd);
    };
    // eslint-disable-next-line
  }, [dragging]);

  return (
    <>
      {!showConversationModal && (
        <div
          className="fixed flex items-center justify-center rounded-full bg-white shadow-[0_3px_10px_rgb(0,0,0,0.2)] shadow-green-500 cursor-grab z-[9999] select-none"
          style={{
            left: position.x,
            top: position.y,
            width: BUTTON_SIZE,
            height: BUTTON_SIZE,
            userSelect: "none",
          }}
          onMouseDown={handleMouseDown}
          onTouchStart={handleTouchStart}
          tabIndex={0}
          aria-label="Open chat"
        >
          <ChatbotIcon />
        </div>
      )}
      <ConversationModal
        open={showConversationModal}
        onClose={() => setShowConversationModal(false)}
      />
    </>
  );
};

export default ChatButton;
