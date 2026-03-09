import { defineStore } from 'pinia'
import type { Message, AgentEvent, ChatState, ConversationSummary, MessageStatus } from '@/types'
import { AgentEventType } from '@/types'
import { api } from '@/utils/bridge'

export const useChatStore = defineStore('chat', {
  state: (): ChatState => ({
    messages: [],
    isLoading: false,
    currentThinkingChain: [],
    activeConversationId: null,
    conversationList: []
  }),

  actions: {
    // ---- 会话列表 ----

    /** 从 bridge 加载真实会话列表 */
    async loadConversationList() {
      try {
        const list = await api.getHistoryList()
        this.conversationList = list
      } catch (e) {
        console.error('加载会话列表失败:', e)
      }
    },

    /** 切换到指定会话 */
    async switchConversation(convId: string) {
      try {
        const detail = await api.getConversation(convId)
        if (detail) {
          this.activeConversationId = detail.id
          // 转换消息格式
          this.messages = (detail.messages || []).map((m: any) => ({
            id: String(m.id || Date.now()),
            role: m.role as 'user' | 'assistant',
            content: m.content,
            images: m.images || [],
            timestamp: new Date(m.timestamp).getTime() || Date.now(),
            status: 'done' as MessageStatus
          }))
          this.clearThinkingChain()
        }
      } catch (e) {
        console.error('切换会话失败:', e)
      }
    },

    /** 创建新会话 */
    async createNewConversation() {
      try {
        const convId = await api.createConversation()
        if (convId) {
          this.activeConversationId = convId
          this.messages = []
          this.clearThinkingChain()
          await this.loadConversationList()
        }
        return convId
      } catch (e) {
        console.error('创建会话失败:', e)
        return null
      }
    },

    /** 重命名会话 */
    async renameConversation(convId: string, title: string) {
      try {
        const ok = await api.renameConversation(convId, title)
        if (ok) {
          await this.loadConversationList()
        }
        return ok
      } catch (e) {
        console.error('重命名会话失败:', e)
        return false
      }
    },

    /** 删除会话 */
    async deleteConversation(convId: string) {
      try {
        const ok = await api.deleteConversation(convId)
        if (ok) {
          if (this.activeConversationId === convId) {
            this.activeConversationId = null
            this.messages = []
          }
          await this.loadConversationList()
        }
        return ok
      } catch (e) {
        console.error('删除会话失败:', e)
        return false
      }
    },

    // ---- 消息操作 ----

    addMessage(message: Omit<Message, 'id' | 'timestamp'>) {
      const newMessage: Message = {
        ...message,
        id: Date.now().toString(),
        timestamp: Date.now(),
        status: message.status || 'done'
      }
      this.messages.push(newMessage)
      return newMessage
    },

    updateLastMessage(content: string) {
      if (this.messages.length > 0) {
        const lastMessage = this.messages[this.messages.length - 1]
        if (lastMessage.role === 'assistant') {
          lastMessage.content = content
          lastMessage.status = 'streaming'
        }
      }
    },

    markLastMessageDone() {
      if (this.messages.length > 0) {
        const lastMessage = this.messages[this.messages.length - 1]
        if (lastMessage.role === 'assistant') {
          lastMessage.status = 'done'
        }
      }
    },

    markLastMessageError() {
      if (this.messages.length > 0) {
        const lastMessage = this.messages[this.messages.length - 1]
        if (lastMessage.role === 'assistant') {
          lastMessage.status = 'error'
        }
      }
    },

    setLoading(loading: boolean) {
      this.isLoading = loading
    },

    // ---- 思考链 ----

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
