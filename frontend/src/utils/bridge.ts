import { useChatStore } from '@/stores/chat'
import { AgentEventType } from '@/types'
import type { ConversationSummary, ConversationDetail, SettingsState } from '@/types'

interface PyWebViewWindow extends Window {
  pywebview?: {
    api: {
      send_message: (text: string, images?: string[]) => Promise<void>
      start_recording: () => Promise<void>
      start_recording_vad: () => Promise<void>
      stop_recording: () => Promise<void>
      // 会话管理
      get_history_list: () => Promise<ConversationSummary[]>
      get_conversation: (id: string) => Promise<ConversationDetail | null>
      create_conversation: () => Promise<string | null>
      rename_conversation: (id: string, title: string) => Promise<boolean>
      delete_conversation: (id: string) => Promise<boolean>
      // 设置
      get_settings: () => Promise<Partial<SettingsState>>
      update_settings: (settings: Partial<SettingsState>) => Promise<boolean>
      validate_whisper_path: (path: string) => Promise<{ valid: boolean; message: string }>
      // 技能
      get_skills: () => Promise<any[]>
      reload_skills: () => Promise<boolean>
      // 兼容旧 API
      get_history: () => Promise<any[]>
    }
  }
}

declare const window: PyWebViewWindow

/**
 * 统一异步桥接层 —— 所有 pywebview API 返回 Promise
 * 在浏览器 dev 环境下走 mock fallback
 */
export const api = {
  // ---- 消息 ----
  sendMessage: async (text: string, images?: string[]) => {
    if (window.pywebview?.api?.send_message) {
      await window.pywebview.api.send_message(text, images)
    } else {
      console.warn('[bridge] pywebview.api not available, simulating send')
    }
  },

  // ---- 录音 ----
  startRecording: async () => {
    if (window.pywebview?.api?.start_recording) {
      await window.pywebview.api.start_recording()
    } else {
      console.warn('[bridge] pywebview.api not available')
    }
  },

  stopRecording: async () => {
    if (window.pywebview?.api?.stop_recording) {
      await window.pywebview.api.stop_recording()
    } else {
      console.warn('[bridge] pywebview.api not available')
    }
  },

  startRecordingVad: async () => {
    if (window.pywebview?.api?.start_recording_vad) {
      await window.pywebview.api.start_recording_vad()
    } else {
      console.warn('[bridge] pywebview.api not available')
    }
  },

  // ---- 会话管理 ----
  getHistoryList: async (): Promise<ConversationSummary[]> => {
    if (window.pywebview?.api?.get_history_list) {
      const result = await window.pywebview.api.get_history_list()
      return result || []
    }
    // dev fallback: 空列表
    console.warn('[bridge] dev fallback: getHistoryList returning empty')
    return []
  },

  getConversation: async (id: string): Promise<ConversationDetail | null> => {
    if (window.pywebview?.api?.get_conversation) {
      return await window.pywebview.api.get_conversation(id)
    }
    console.warn('[bridge] dev fallback: getConversation returning null')
    return null
  },

  createConversation: async (): Promise<string | null> => {
    if (window.pywebview?.api?.create_conversation) {
      return await window.pywebview.api.create_conversation()
    }
    console.warn('[bridge] dev fallback: createConversation')
    return 'dev-' + Date.now()
  },

  renameConversation: async (id: string, title: string): Promise<boolean> => {
    if (window.pywebview?.api?.rename_conversation) {
      return await window.pywebview.api.rename_conversation(id, title)
    }
    console.warn('[bridge] dev fallback: renameConversation')
    return false
  },

  deleteConversation: async (id: string): Promise<boolean> => {
    if (window.pywebview?.api?.delete_conversation) {
      return await window.pywebview.api.delete_conversation(id)
    }
    console.warn('[bridge] dev fallback: deleteConversation')
    return false
  },

  // ---- 设置 ----
  getSettings: async (): Promise<Partial<SettingsState>> => {
    if (window.pywebview?.api?.get_settings) {
      return await window.pywebview.api.get_settings()
    }
    console.warn('[bridge] dev fallback: getSettings')
    return {}
  },

  updateSettings: async (settings: Partial<SettingsState>): Promise<boolean> => {
    if (window.pywebview?.api?.update_settings) {
      return await window.pywebview.api.update_settings(settings)
    }
    console.warn('[bridge] dev fallback: updateSettings')
    return false
  },

  validateWhisperPath: async (path: string): Promise<{ valid: boolean; message: string }> => {
    if (window.pywebview?.api?.validate_whisper_path) {
      return await window.pywebview.api.validate_whisper_path(path)
    }
    return { valid: false, message: 'pywebview 不可用' }
  },

  // ---- 技能 ----
  getSkills: async (): Promise<any[]> => {
    if (window.pywebview?.api?.get_skills) {
      return await window.pywebview.api.get_skills()
    }
    console.warn('[bridge] pywebview.api not available')
    return []
  },

  reloadSkills: async (): Promise<boolean> => {
    if (window.pywebview?.api?.reload_skills) {
      return await window.pywebview.api.reload_skills()
    }
    console.warn('[bridge] pywebview.api not available')
    return false
  }
}

/**
 * 注册 Python → JS 回调函数
 */
export function registerCallbacks() {
  const chatStore = useChatStore()

  ;(window as any).onThinking = (reasoning: string) => {
    console.log('onThinking:', reasoning)
    chatStore.updateLastThinking(reasoning)
  }

  ;(window as any).onToolStart = (toolCall: any) => {
    console.log('onToolStart:', toolCall)
    chatStore.addThinkingEvent({
      type: AgentEventType.TOOL_START,
      data: toolCall,
      timestamp: Date.now()
    })
  }

  ;(window as any).onToolResult = (result: string) => {
    console.log('onToolResult:', result)
    chatStore.addThinkingEvent({
      type: AgentEventType.TOOL_RESULT,
      data: { result },
      timestamp: Date.now()
    })
  }

  ;(window as any).onAgentReply = (content: string) => {
    console.log('onAgentReply:', content)
    if (chatStore.messages.length === 0 || chatStore.messages[chatStore.messages.length - 1].role !== 'assistant') {
      chatStore.addMessage({ role: 'assistant', content: '', status: 'streaming' })
    }
    chatStore.updateLastMessage(content)
  }

  ;(window as any).onAgentError = (error: string) => {
    console.error('onAgentError:', error)
    chatStore.addThinkingEvent({
      type: AgentEventType.ERROR,
      data: { error },
      timestamp: Date.now()
    })
    chatStore.markLastMessageError()
    chatStore.setLoading(false)
  }

  ;(window as any).onAgentStart = () => {
    console.log('onAgentStart')
    chatStore.setLoading(true)
    chatStore.clearThinkingChain()
  }

  ;(window as any).onAgentComplete = () => {
    console.log('onAgentComplete')
    chatStore.setLoading(false)
    chatStore.markLastMessageDone()
    chatStore.attachThinkingChainToLastMessage()
    // 刷新侧栏会话列表（新对话/消息计数可能变化）
    chatStore.loadConversationList()
  }

  ;(window as any).onUserMessage = (text: string) => {
    console.log('onUserMessage:', text)
    chatStore.addMessage({
      role: 'user',
      content: text,
      status: 'done'
    })
  }

  ;(window as any).onWakeup = () => {
    console.log('onWakeup: 唤醒事件，通知切换到悬浮录音态')
    chatStore.triggerWakeup()
  }

  ;(window as any).onRecordingStopped = () => {
    console.log('onRecordingStopped: 录音已停止')
    chatStore.setRecording(false)
  }

  console.log('Bridge callbacks registered')
}
