import { ref, watch, type WatchCallback } from 'vue'

export function useAutoSave<T>(key: string, initial: T) {
  const state = ref<T>(load())

  function load(): T {
    try {
      const raw = localStorage.getItem(key)
      return raw ? (JSON.parse(raw) as T) : initial
    } catch {
      return initial
    }
  }

  function save(val: T) {
    try {
      localStorage.setItem(key, JSON.stringify(val))
    } catch {
      // ignore write errors
    }
  }

  watch(state, (val) => save(val), { deep: true, immediate: true })
  return state
}
