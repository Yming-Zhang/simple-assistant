import { useChatStore } from '@/stores/chat'
import { AgentEventType } from '@/types'

interface PyWebViewWindow extends Window {
  pywebview?: {
    api: {
      send_message: (text: string, images?: string[]) => void
      start_recording: () => void
      stop_recording: () => void
      get_history: () => any[]
      get_settings: () => any
      update_settings: (settings: any) => void
    }
  }
}

declare const window: PyWebViewWindow

export const api = {
  sendMessage: (text: string, images?: string[]) => {
    if (window.pywebview?.api?.send_message) {
      window.pywebview.api.send_message(text, images)
    } else {
      console.warn('pywebview.api not available, simulating send')
    }
  },

  startRecording: () => {
    if (window.pywebview?.api?.start_recording) {
      window.pywebview.api.start_recording()
    } else {
      console.warn('pywebview.api not available')
    }
  },

  stopRecording: () => {
    if (window.pywebview?.api?.stop_recording) {
      window.pywebview.api.stop_recording()
    } else {
      console.warn('pywebview.api not available')
    }
  }
}

export function registerCallbacks() {
  const chatStore = useChatStore()

  ;(window as any).onThinking = (reasoning: string) => {
    console.log('onThinking:', reasoning)
    chatStore.addThinkingEvent({
      type: AgentEventType.THINKING,
      data: { reasoning },
      timestamp: Date.now()
    })
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
    chatStore.updateLastMessage(content)
  }

  ;(window as any).onAgentError = (error: string) => {
    console.error('onAgentError:', error)
    chatStore.addThinkingEvent({
      type: AgentEventType.ERROR,
      data: { error },
      timestamp: Date.now()
    })
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
    chatStore.attachThinkingChainToLastMessage()
  }

  ;(window as any).onUserMessage = (text: string) => {
    console.log('onUserMessage:', text)
    chatStore.addMessage({
      role: 'user',
      content: text
    })
  }

  console.log('Bridge callbacks registered')
}
