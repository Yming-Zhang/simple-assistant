import { defineStore } from 'pinia'
import type { SettingsState, ThemeType } from '@/types'

const DEFAULT_SETTINGS: SettingsState = {
  showThinkingChain: true,
  model: 'qwen3.5',
  temperature: 0.7,
  theme: 'blue-gradient',
  voiceReplyEnabled: true,
  voiceReplyOnlyWhenWakeByVoice: true,
  voiceReplyVolume: 0.8,
  whisperPath: '',
  defaultWindowMode: 'expanded'
}

export const useSettingsStore = defineStore('settings', {
  state: (): SettingsState => ({ ...DEFAULT_SETTINGS }),

  actions: {
    /** 从 Python bridge 加载已持久化的设置 */
    async loadSettings() {
      try {
        const pywebview = (window as any).pywebview
        if (pywebview?.api?.get_settings) {
          const saved = await pywebview.api.get_settings()
          if (saved && typeof saved === 'object') {
            // 合并已保存的设置（保留默认值作为兜底）
            Object.assign(this, { ...DEFAULT_SETTINGS, ...saved })
          }
        }
      } catch (e) {
        console.error('加载设置失败:', e)
      }
      // 加载后立即应用主题
      this.applyTheme()
    },

    /** 保存所有设置到 Python bridge（落盘） */
    async saveSettings() {
      try {
        const pywebview = (window as any).pywebview
        if (pywebview?.api?.update_settings) {
          const snapshot: SettingsState = {
            showThinkingChain: this.showThinkingChain,
            model: this.model,
            temperature: this.temperature,
            theme: this.theme,
            voiceReplyEnabled: this.voiceReplyEnabled,
            voiceReplyOnlyWhenWakeByVoice: this.voiceReplyOnlyWhenWakeByVoice,
            voiceReplyVolume: this.voiceReplyVolume,
            whisperPath: this.whisperPath,
            defaultWindowMode: this.defaultWindowMode
          }
          await pywebview.api.update_settings(snapshot)
        }
      } catch (e) {
        console.error('保存设置失败:', e)
      }
    },

    /** 切换主题并持久化 */
    setTheme(theme: ThemeType) {
      this.theme = theme
      this.applyTheme()
      this.saveSettings()
    },

    /** 将主题 CSS 变量应用到 document */
    applyTheme() {
      document.documentElement.setAttribute('data-theme', this.theme)
    },

    /** 设置 Whisper 路径 */
    setWhisperPath(path: string) {
      this.whisperPath = path
      this.saveSettings()
    },

    setShowThinkingChain(show: boolean) {
      this.showThinkingChain = show
      this.saveSettings()
    },

    setModel(model: string) {
      this.model = model
      this.saveSettings()
    },

    setTemperature(temp: number) {
      this.temperature = temp
      this.saveSettings()
    },

    setVoiceReplyEnabled(enabled: boolean) {
      this.voiceReplyEnabled = enabled
      this.saveSettings()
    },

    setVoiceReplyOnlyWhenWakeByVoice(only: boolean) {
      this.voiceReplyOnlyWhenWakeByVoice = only
      this.saveSettings()
    },

    setVoiceReplyVolume(volume: number) {
      this.voiceReplyVolume = volume
      this.saveSettings()
    },

    setDefaultWindowMode(mode: 'expanded' | 'floating') {
      this.defaultWindowMode = mode
      this.saveSettings()
    }
  }
})
