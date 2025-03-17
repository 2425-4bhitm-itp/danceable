import { html, render } from 'lib/pure-html'
import { addLinks } from 'lib/router'

export const SnippetComponent = 'snippet-component'

class SnippetElement extends HTMLElement {
  static observedAttributes = ['hidden', 'id', 'fileName', 'speed', 'songSnippetIndex']

  snippetId: number

  constructor() {
    super()
  }

  connectedCallback() {
    this.render()

    this.addEventListener('click', (e: MouseEvent) => this.clicked())
  }

  render() {
    render(html`
      <div class="w-full p-1 cursor-pointer" data-id="${this.snippetId}">
        <span>
          ${this.getAttribute('fileName')}
            (${this.getAttribute('songSnippetIndex')})
        </span>
        <span>${this.getAttribute('speed')}</span>
      </div>
    `, this)

    addLinks(this)
  }

  attributeChangedCallback(name: string, newValue: string | null, oldValue: string) {
    this.snippetId = Number.parseInt(this.getAttribute('id'))

    this.render()
  }

  clicked() {
    this.dispatchEvent(new CustomEvent('snippet-selected', { detail: this.id }))
  }
}

customElements.define(SnippetComponent, SnippetElement)
