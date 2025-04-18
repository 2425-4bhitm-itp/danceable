import { useEffect, useState } from 'react'
import { ToastType } from './ToastType'
import { ToastData } from '../../stores/toast/ToastData'

type ToastProps = Omit<ToastData, 'id'> & {
  onRemove: () => void
}

function Toast(props: ToastProps) {
  const [visible, setVisible] = useState(false)
  const [exiting, setExiting] = useState(false)

  const stylesBasedOnType = new Map<ToastType, string>([
    [ToastType.INFO, 'border-blue-200'],
    [ToastType.DEBUG, 'border-purple-200'],
    [ToastType.ERROR, 'border-red-300'],
  ])

  useEffect(() => {
    const frame = requestAnimationFrame(() => setVisible(true))
    let hideTimeout: ReturnType<typeof setTimeout> | undefined

    if (props.timeToLive) {
      hideTimeout = setTimeout(() => {
        setVisible(false)
        setExiting(true)

        setTimeout(() => {
          props.onRemove()
        }, 400)
      }, props.timeToLive)
    }

    return () => {
      cancelAnimationFrame(frame)
      if (hideTimeout) clearTimeout(hideTimeout)
    }
  }, [props.timeToLive])

  return (
    <div
      className={
        'm-2 max-w-128 rounded-xl border-2 bg-white p-3 align-baseline text-lg shadow-lg transition-all duration-400 select-none hover:-translate-y-0.5 hover:scale-101 ' +
        stylesBasedOnType.get(props.type) +
        ' ' +
        (visible
          ? 'scale-100 opacity-100'
          : exiting
            ? '-translate-y-16 scale-90 opacity-0'
            : 'translate-y-12 scale-90 opacity-0')
      }
    >
      <span>{props.message}</span>
    </div>
  )
}

export default Toast
