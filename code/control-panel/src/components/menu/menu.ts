import { html, render } from 'lib/pure-html'
import { addLinks } from 'lib/router'

class MenuElement extends HTMLElement {
  constructor() {
    super()
    this.attachShadow({ mode: 'open' })
  }

  connectedCallback() {
    this.render()
  }

  render() {
    if (this.shadowRoot) {
      render(html`
         menu
      `, this.shadowRoot)
      addLinks(this.shadowRoot)
    }
  }
}

export const AppMenu = 'menu-component'

customElements.define(AppMenu, MenuElement)