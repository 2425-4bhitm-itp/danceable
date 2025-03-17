import { set } from '../model'

interface NavigationState {
  pane: string
}

setup()

function setup() {
  const path = window.location.pathname
  window.addEventListener('popstate', (event: PopStateEvent) => {
    const state = event.state as NavigationState
    set((model) => (model.currentPane = state.pane))
  })
  const state = createNavigationStateWith(document.location.href)
  history.replaceState(state, '', document.location.href)
}

function createNavigationStateWith(location: string) {
  const url = new URL(location)
  const pane = url.pathname
  const state: NavigationState = {
    pane,
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

export { addLinks }
