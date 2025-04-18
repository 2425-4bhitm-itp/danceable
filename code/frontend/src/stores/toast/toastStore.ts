import { create } from 'zustand'
import { ToastData } from './ToastData'

type ToastStore = {
  toasts: ToastData[]
  createToast: (toast: ToastData) => void
  deleteToast: (id: number) => void
}

let toastQueue: ToastData[] = []
let isProcessingQueue = false

const STAGGER_DELAY = 401

export const useToastStore = create<ToastStore>((set) => ({
  toasts: [],
  createToast: (toast) => {
    toastQueue.push({ ...toast, id: Date.now() + Math.random() })

    if (!isProcessingQueue) {
      isProcessingQueue = true
      processQueue()
    }

    function processQueue() {
      if (toastQueue.length === 0) {
        isProcessingQueue = false
        return
      }

      const nextToast = toastQueue.shift()

      if (nextToast) {
        set((state) => ({ toasts: [...state.toasts, nextToast] }))
      }

      setTimeout(() => {
        processQueue()
      }, STAGGER_DELAY)
    }
  },
  deleteToast: (id) => {
    set((state) => {
      return { toasts: state.toasts.filter((toast) => toast.id !== id) }
    })
  },
}))
