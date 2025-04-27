import { useToastStore } from '../../stores/toast/toastStore'
import Toast from './Toast'

function ToastContainer() {
  const { toasts } = useToastStore()

  return (
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
  )
}

export default ToastContainer
