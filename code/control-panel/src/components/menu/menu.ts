import { html, render } from 'lib/pure-html'
import { addLinks } from 'lib/router'

import { libraryRoute } from 'components/library'
import { analysisRoute } from 'components/analysis'

export const AppMenu = 'menu-component'

class MenuElement extends HTMLElement {
  constructor() {
    super()
  }

  connectedCallback() {
    this.render()
  }

  render() {
    render(html`
      <div class="flex-initial p-1 h-full">
        <a class="rounded-xl bg-gray-200 aspect-square p-2 m-2 flex justify-center items-center"
           href="${libraryRoute}">Library</a>
        <a class="rounded-xl bg-gray-200 aspect-square p-2 m-2 flex justify-center items-center"
           href="${analysisRoute}">Analysis</a>
      </div>
    `, this)
    addLinks(this)
  }
}

customElements.define(AppMenu, MenuElement)
