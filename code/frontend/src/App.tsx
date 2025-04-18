import Library from './pages/Library.tsx'
import Analysis from './pages/Analysis.tsx'
import Home from './pages/Home.tsx'

import { createBrowserRouter, RouterProvider } from 'react-router'
import RootLayout from './components/RootLayout.tsx'
import { useDanceStore } from './stores/dance/danceStore.ts'
import { useEffect } from 'react'
import { useClipStore } from './stores/clip/clipStore.ts'
import { useSongStore } from './stores/song/songStore.ts'
import { ToastType } from './components/toast/ToastType.ts'
import ToastContainer from './components/toast/ToastContainer.tsx'
import { ToastData } from './stores/toast/ToastData.ts'
import { useToastStore } from './stores/toast/toastStore.ts'
import Toast from './components/toast/Toast.tsx'

const router = createBrowserRouter([
  {
    path: '/',
    Component: RootLayout,
    children: [
      { path: '', element: <Home /> },
      { path: 'library', element: <Library /> },
      { path: 'analysis', element: <Analysis /> },
    ],
  },
])

function App() {
  const { fetchDances } = useDanceStore()
  const { fetchClips } = useClipStore()
  const { fetchSongs } = useSongStore()
  const { createToast } = useToastStore()

  const fetchData = async () => {
    await fetchClips((message) =>
      createToast({
        type: ToastType.ERROR,
        message: message,
        timeToLive: 3000,
      } as ToastData)
    )

    await fetchSongs((message) =>
      createToast({
        type: ToastType.ERROR,
        message: message,
        timeToLive: 3000,
      } as ToastData)
    )

    await fetchDances((message) =>
      createToast({
        type: ToastType.ERROR,
        message: message,
        timeToLive: 3000,
      } as ToastData)
    )
  }

  useEffect(() => {
    fetchData()
  }, [])

  return (
    <>
      <ToastContainer />
      <RouterProvider router={router} />
    </>
  )
}

export default App
