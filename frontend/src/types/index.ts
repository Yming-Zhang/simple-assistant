// ---- 主题 ----
export type ThemeType = 'blue-gradient' | 'pink-gradient' | 'pure-white'

// ---- Agent 事件 ----
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

// ---- 消息状态 ----
export type MessageStatus = 'sending' | 'streaming' | 'done' | 'error'

export interface ToolEvent {
  type: 'tool_start' | 'tool_result'
  name?: string
  args?: Record<string, any>
  result?: string
  timestamp: number
}

export interface Attachment {
  type: 'image'
  url: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  images?: string[]
  timestamp: number
  status?: MessageStatus
  thinkingChain?: AgentEvent[]
  toolEvents?: ToolEvent[]
  attachments?: Attachment[]
}

// ---- 会话 ----
export interface ConversationSummary {
  id: string
  title: string
  preview: string | null
  created_at: string
  updated_at: string
  message_count: number
}

export interface ConversationDetail {
  id: string
  title: string
  created_at: string
  updated_at: string
  messages: ConversationMessage[]
}

export interface ConversationMessage {
  id: number
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  images?: string[]
}

// ---- 状态 ----
export interface ChatState {
  messages: Message[]
  isLoading: boolean
  currentThinkingChain: AgentEvent[]
  activeConversationId: string | null
  conversationList: ConversationSummary[]
}

export interface SettingsState {
  showThinkingChain: boolean
  model: string
  temperature: number
  theme: ThemeType
  voiceReplyEnabled: boolean
  voiceReplyOnlyWhenWakeByVoice: boolean
  voiceReplyVolume: number
  whisperPath: string
  defaultWindowMode: 'expanded' | 'floating'
}

// ---- UI 状态 ----
export interface UIState {
  isExpanded: boolean
  isSidebarOpen: boolean
  isSettingsOpen: boolean
}
