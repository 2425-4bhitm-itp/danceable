import { set } from '../model'
import { libraryRoute } from 'components/library'

interface NavigationState {
  pane: string
}

const DEFAULT_PANE = '/' + libraryRoute

function setupRoute() {
  let state: NavigationState = history.state
    ? history.state
    : createNavigationStateWith(document.location.href)

  const pathname = window.location.pathname

  if (pathname === '/') {
    if (state.pane !== DEFAULT_PANE) {
      state.pane = DEFAULT_PANE
      window.history.pushState(state, '', state.pane)
    }
  } else if (pathname !== state.pane) {
    state.pane = pathname
    window.history.pushState(state, '', state.pane)
  }

  set((model) => {
    model.currentPane = state.pane
  })
}

setup()

function setup() {
  setupRoute()

  window.addEventListener('popstate', (event: PopStateEvent) => {
    const state = event.state as NavigationState
    set((model) => {
      model.currentPane = state.pane
    })
  })
}

function createNavigationStateWith(location: string) {
  const url = new URL(location)
  const pane = url.pathname
  const state: NavigationState = {
    pane: pane,
  }

  return state
}

function addLinks(element: HTMLElement | ShadowRoot) {
  const linksList = element.querySelectorAll('a')
  const links = Array.from(linksList)
  links.forEach((a) => {
    a.onclick = (e: MouseEvent) => {
      e.preventDefault()
      const state = createNavigationStateWith(a.href)
      history.pushState(state, '', a.href)
      set((model) => (model.currentPane = state.pane))
    }
  })
}

export { addLinks, createNavigationStateWith }
