import { html, render, renderAppendChild } from 'lib/pure-html'
import { addLinks } from 'lib/router'
import { subscribe } from 'model/model'
import { clear } from 'lib/util'
import { Snippet } from 'model/snippet/snippet'
import { SnippetComponent } from 'components/snippet/snippet-component'

export const Library = 'library-component'
export const libraryRoute = 'library'

class LibraryElement extends HTMLElement {
  static observedAttributes = ['hidden']

  constructor() {
    super()
  }

  connectedCallback() {
    this.render()

    subscribe(model => this.renderSnippets(model.snippets))
  }

  render() {
    render(html`
      <div>
        <div class="text-3xl mt-8 mb-4 px-2">Library</div>
        <div id="snippets" class="w-full flex flex-col"></div>
      </div> `, this)

    addLinks(this)
  }

  renderSnippets(snippets: Snippet[]) {
    const snippetsContainer: HTMLElement = this.querySelector('#snippets')
    clear(snippetsContainer)

    if (Array.isArray(snippets)) {
      snippets.forEach(snippet => {
        const snippetComponent = renderAppendChild(html`
          <${SnippetComponent}
            snippet='${JSON.stringify(snippet)}'
            
            class="odd:bg-gray-100 w-full px-2"
          >
          </${SnippetComponent}>
        `, snippetsContainer)

        snippetComponent.addEventListener('snippet-selected', (e: CustomEvent) => {
          this.snippetClicked(e)
        })
      })
    }
  }

  snippetClicked(e: CustomEvent) {
    const snippetId: number = Number.parseInt(e.detail)

    alert(e.detail)
    console.log('snippet with id ' + snippetId + ' clicked!')
  }
}

customElements.define(Library, LibraryElement)
