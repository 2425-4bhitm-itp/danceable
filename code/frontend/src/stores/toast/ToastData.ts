import { ToastType } from '../../components/toast/ToastType'

export interface ToastData {
  id: number
  type: ToastType
  message: string
  timeToLive?: number
}
