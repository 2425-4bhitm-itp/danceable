import { useToastStore } from '../../stores/toast/toastStore'
import Toast from './Toast'
import { useEffect } from 'react'

function ToastContainer() {
  const { toasts } = useToastStore()

  useEffect(() => console.log('toasts:', toasts), [toasts])

  return (
    <>
      <div className="fixed right-2 bottom-2 z-30">
        {Array.from(toasts).map((t) => {
          return (
            <>
              <Toast
                key={t.id}
                type={t.type}
                message={t.message}
                timeToLive={t.timeToLive}
                onRemove={() => {}}
              />
            </>
          )
        })}
      </div>
    </>
  )
}

export default ToastContainer
