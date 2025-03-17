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
      <div class="flex-initial p-2 h-full">
        <div class="flex justify-center items-center m-4">
          <div class="w-10"><img class="w-full" src="/public/danceable-logo.svg" alt=""></div>
        </div>
        <a class="rounded-2xl bg-gray-100 aspect-square p-4 m-2 flex justify-center items-center"
           href="${libraryRoute}">
          <div class="w-6"><img class="w-full" src="/public/icons/library-icon.svg" alt=""></div>
        </a>
        <a class="rounded-2xl bg-gray-100 aspect-square p-2 m-2 flex justify-center items-center"
           href="${analysisRoute}">
          <div class="w-6"><img class="w-full" src="/public/icons/analysis-icon.svg" alt=""></div>
        </a>
      </div>
    `, this)
    addLinks(this)
  }
}

customElements.define(AppMenu, MenuElement)
