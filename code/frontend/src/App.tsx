import Library from './pages/Library.tsx'
import Analysis from './pages/Analysis.tsx'
import Home from './pages/Home.tsx'

import { createBrowserRouter, RouterProvider } from 'react-router'
import RootLayout from './components/RootLayout.tsx'
import { useDanceStore } from './stores/dance/danceStore.ts'
import { useEffect } from 'react'
import { useClipStore } from './stores/clip/clipStore.ts'
import { useSongStore } from './stores/song/songStore.ts'

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

  useEffect(() => {
    fetchDances()
    fetchClips()
    fetchSongs()
  }, [])

  return <RouterProvider router={router} />
}

export default App
