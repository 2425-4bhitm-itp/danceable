import Library from './pages/Library.tsx'
import Analysis from './pages/Analysis.tsx'
import Home from './pages/Home.tsx'

import { createBrowserRouter, RouterProvider } from 'react-router'
import RootLayout from './components/RootLayout.tsx'
import ToastContainer from './components/toast/ToastContainer.tsx'

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
  return (
    <>
      <ToastContainer />
      <RouterProvider router={router} />
    </>
  )
}

export default App
