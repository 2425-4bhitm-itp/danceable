import { fetchAllDances, fetchAllSnippets, subscribe } from 'model/index'

import { html, render } from 'lib/pure-html'

import { AppMenu } from 'components/menu'
import { Library, libraryRoute } from 'components/library'
import { Analysis, analysisRoute } from 'components/analysis'
import { fetchAllSongs } from 'model/song/song-service'
import { saveModelToSessionStorage } from 'lib/cache'

class ApplicationElement extends HTMLElement {
  connectedCallback() {
    this.render()

    subscribe((model) => this.show(model.currentPane))
    subscribe((model) => saveModelToSessionStorage(model))


    fetchAllDances()
    fetchAllSnippets()
    fetchAllSongs()
  }

  render() {
    render(
      html`
        <div class="flex h-screen">
          <${AppMenu}></${AppMenu}>
          <div class="flex-auto">
            <${Library} hidden data-pane="/${libraryRoute}"></${Library}>
            <${Analysis} hidden data-pane="/${analysisRoute}"></${Analysis}>
          </div>
        </div>
      `,
      this,
    )
  }

  show(pane: string) {
    const panes = [Library, Analysis]

    panes.forEach((el) => {
      const element = this.querySelector(el) as HTMLElement

      if (element.dataset.pane == pane) {
        element.removeAttribute('hidden')
      } else {
        element.setAttribute('hidden', '')
      }
    })
  }
}

customElements.define('application-component', ApplicationElement)
