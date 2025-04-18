import { html, render } from 'lib/pure-html'
import { addLinks } from 'lib/router'

import { libraryRoute } from 'components/library'
import { analysisRoute } from 'components/analysis'
import { store } from 'model/index'

export const AppMenu = 'menu-component'

class MenuElement extends HTMLElement {
  connectedCallback() {
    this.render()

    store.subscribe((model) => this.highlightLink(model.currentPane))
  }

  render() {
    render(
      html`
        <div class="h-full flex-initial border-r-2 border-r-gray-200 p-2">
          <div class="m-4 flex items-center justify-center">
            <div class="h-12">
              <img class="h-full" src="/public/svgs/logo/danceable-logo.svg" alt="" />
            </div>
          </div>
          <a
            class="m-2 flex aspect-square items-center justify-center rounded-2xl bg-gray-100 p-4 transition hover:bg-gray-200"
            href="${libraryRoute}"
          >
            <div class="w-6">
              <img class="w-full" src="/public/svgs/menu/library-icon-dark.svg" alt="" />
            </div>
          </a>
          <a
            class="m-2 flex aspect-square items-center justify-center rounded-2xl bg-gray-100 p-4 transition hover:bg-gray-200"
            href="${analysisRoute}"
          >
            <div class="w-6">
              <img class="w-full" src="/public/svgs/menu/analysis-icon-dark.svg" alt="" />
            </div>
          </a>
        </div>
      `,
      this
    )

    addLinks(this)
  }

  private highlightLink(currentPane: string) {
    const links = this.querySelectorAll('a')

    links.forEach((link) => {
      link.classList.remove('bg-gray-dark')
      link.classList.remove('hover:bg-gray-200')

      link.querySelector('img').src = link.querySelector('img').src.replace('light', 'dark')

      if ('/' + link.getAttribute('href') === currentPane) {
        link.classList.add('bg-gray-dark')
        link.querySelector('img').src = link.querySelector('img').src.replace('dark', 'light')
      } else {
        link.classList.add('hover:bg-gray-200')
      }
    })
  }
}

customElements.define(AppMenu, MenuElement)
