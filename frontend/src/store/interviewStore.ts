import { create } from 'zustand';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface InterviewState {
  messages: Message[];
  addMessage: (message: Message) => void;
  clearMessages: () => void;
}

export const useInterviewStore = create<InterviewState>((set) => ({
  messages: [],
  
  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  clearMessages: () => set({ messages: [] }),
}));
