import { defineStore } from 'pinia'
import type { Message, AgentEvent, ChatState } from '@/types'
import { AgentEventType } from '@/types'

export const useChatStore = defineStore('chat', {
  state: (): ChatState => ({
    messages: [],
    isLoading: false,
    currentThinkingChain: []
  }),

  actions: {
    addMessage(message: Omit<Message, 'id' | 'timestamp'>) {
      const newMessage: Message = {
        ...message,
        id: Date.now().toString(),
        timestamp: Date.now()
      }
      this.messages.push(newMessage)
      return newMessage
    },

    updateLastMessage(content: string) {
      if (this.messages.length > 0) {
        const lastMessage = this.messages[this.messages.length - 1]
        if (lastMessage.role === 'assistant') {
          lastMessage.content = content
        }
      }
    },

    setLoading(loading: boolean) {
      this.isLoading = loading
    },

    addThinkingEvent(event: AgentEvent) {
      this.currentThinkingChain.push(event)
    },
    
    updateLastThinking(reasoning: string) {
      if (this.currentThinkingChain.length > 0) {
        const lastEvent = this.currentThinkingChain[this.currentThinkingChain.length - 1]
        if (lastEvent.type === AgentEventType.THINKING && lastEvent.data.reasoning) {
          lastEvent.data.reasoning = reasoning
        } else {
          this.addThinkingEvent({
            type: AgentEventType.THINKING,
            data: { reasoning },
            timestamp: Date.now()
          })
        }
      } else {
        this.addThinkingEvent({
          type: AgentEventType.THINKING,
          data: { reasoning },
          timestamp: Date.now()
        })
      }
    },

    clearThinkingChain() {
      this.currentThinkingChain = []
    },

    attachThinkingChainToLastMessage() {
      if (this.messages.length > 0 && this.currentThinkingChain.length > 0) {
        const lastMessage = this.messages[this.messages.length - 1]
        if (lastMessage.role === 'assistant') {
          lastMessage.thinkingChain = [...this.currentThinkingChain]
        }
      }
      this.clearThinkingChain()
    }
  }
})
