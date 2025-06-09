export interface WSEvent {
  event: string;
  data: any;
}

export interface WSEventMessage {
  content: string;
  conversationId: string;
  role: 'self' | 'user';
}

export const toEvent = (name: string, data: any) => {
  return JSON.stringify({
    event: name,
    data,
  });
};

export const sendEvent = (ws: WebSocket, name: string, data: any) => {
  ws.send(toEvent(name, data));
};
