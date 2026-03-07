import { defineStore } from 'pinia'
import type { SettingsState } from '@/types'

export const useSettingsStore = defineStore('settings', {
  state: (): SettingsState => ({
    showThinkingChain: true,
    model: 'qwen3.5',
    temperature: 0.7
  }),

  actions: {
    setShowThinkingChain(show: boolean) {
      this.showThinkingChain = show
    },

    setModel(model: string) {
      this.model = model
    },

    setTemperature(temp: number) {
      this.temperature = temp
    }
  }
})
