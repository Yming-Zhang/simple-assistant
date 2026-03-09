import { useSettingsStore } from '@/stores/settings'
import type { ThemeType } from '@/types'

export interface ThemeOption {
  value: ThemeType
  label: string
  icon: string
  preview: string  // CSS gradient / color for preview dot
}

export const themeOptions: ThemeOption[] = [
  {
    value: 'blue-gradient',
    label: '蓝色',
    icon: '🔵',
    preview: 'linear-gradient(135deg, #4a90d9, #6cb4ee)'
  },
  {
    value: 'pink-gradient',
    label: '粉色',
    icon: '🌸',
    preview: 'linear-gradient(135deg, #d94a8a, #ee6cb4)'
  },
  {
    value: 'pure-white',
    label: '纯白',
    icon: '⚪',
    preview: 'linear-gradient(135deg, #e5e7eb, #f3f4f6)'
  }
]

export function useTheme() {
  const settingsStore = useSettingsStore()

  function applyTheme(theme: ThemeType) {
    settingsStore.setTheme(theme)
  }

  function currentTheme(): ThemeType {
    return settingsStore.theme
  }

  function getThemeMeta(theme: ThemeType): ThemeOption | undefined {
    return themeOptions.find(t => t.value === theme)
  }

  return {
    themeOptions,
    applyTheme,
    currentTheme,
    getThemeMeta
  }
}
