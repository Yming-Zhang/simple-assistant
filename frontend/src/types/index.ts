export enum AgentEventType {
  THINKING = 'thinking',
  TOOL_START = 'tool_start',
  TOOL_RESULT = 'tool_result',
  REPLY = 'reply',
  ERROR = 'error'
}

export interface AgentEvent {
  type: AgentEventType
  data: any
  timestamp: number
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  images?: string[]
  timestamp: number
  thinkingChain?: AgentEvent[]
}

export interface ChatState {
  messages: Message[]
  isLoading: boolean
  currentThinkingChain: AgentEvent[]
}

export interface SettingsState {
  showThinkingChain: boolean
  model: string
  temperature: number
}
