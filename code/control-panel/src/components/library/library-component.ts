import { html, render } from 'lib/pure-html'
import { addLinks } from 'lib/router'

class LibraryElement extends HTMLElement {
  constructor() {
    super()
    this.attachShadow({ mode: 'open' })
  }

  connectedCallback() {
    this.render()
  }

  render() {
    render(html` library `, this.shadowRoot)
    addLinks(this.shadowRoot)
  }
}

export const Library = 'library-component'

customElements.define(Library, LibraryElement)
