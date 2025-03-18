import { html, render, renderAppendChild } from 'lib/pure-html'
import { addLinks } from 'lib/router'
import { subscribe } from 'model/model'
import { clear } from 'lib/util'

import { SnippetComponent, SnippetElement } from 'components/snippet/snippet-component'
import { DanceFilter } from 'model/dance-filter/dance-filter'
import { Snippet } from 'model/snippet/snippet'

export const Library = 'library-component'
export const libraryRoute = 'library'

class LibraryElement extends HTMLElement {
  static observedAttributes = ['hidden']

  constructor() {
    super()
  }

  async connectedCallback() {
    subscribe(model => {
      this.renderDanceFilters(model.danceFilters)
    })

    this.render()

    subscribe((model) => this.renderSnippets(model.snippets))
  }

  render() {
    render(html`
      <div class="h-full overflow-y-auto">
        <div class="text-3xl pt-9 pb-2 px-2">Library</div>
        <div id="danceFilters" class="flex gap-2 flex-wrap p-2">
        </div>
        <div id="snippets" class="w-full flex flex-col items-center"></div>
      </div> `, this)

    addLinks(this)
  }

  renderDanceFilters(danceFilters: DanceFilter[]) {
    const danceFilterContainer: HTMLElement = this.querySelector('#danceFilters')

    if (danceFilterContainer && Array.isArray(danceFilters)) {
      clear(danceFilterContainer)

      danceFilters.forEach(filter => {
        const filterElement = renderAppendChild(
          html`
            <span
              class="p-0.5 px-3 select-none cursor-pointer ${filter.isEnabled ? 'bg-gray-300' : 'bg-gray-100'} rounded-full">
              ${filter.dance.name}
            </span>
          `, danceFilterContainer,
        )

        filterElement.addEventListener('click', (e) => {
          this.filterClicked(filter, filterElement)
        })
      })
    }
  }

  renderSnippets(snippets: Snippet[]) {
    const snippetsContainer: HTMLElement = this.querySelector('#snippets')
    clear(snippetsContainer)

    if (Array.isArray(snippets)) {
      snippets.forEach(snippet => {
        const snippetElement = document.createElement(SnippetComponent) as SnippetElement
        snippetElement.classList.add(...['w-full', 'px-4'])
        snippetElement.state = snippet

        snippetsContainer.appendChild(snippetElement)

        snippetElement.addEventListener(
          'snippet-option-clicked', (e: CustomEvent) => this.snippetOptionsClicked(snippetElement, e),
        )
      })
    }
  }

  private snippetOptionsClicked(snippet: SnippetElement, e: CustomEvent) {
    const snippetId: number = Number.parseInt(e.detail)

    alert(e.detail)
    console.log('snippet with id ' + snippetId + ' options clicked!')
  }

  private filterClicked(filter: DanceFilter, filterElement: HTMLElement) {
    console.log(filter.dance.name + ' clicked')
    filter.isEnabled = !filter.isEnabled
    console.log(filter.isEnabled)
  }
}

customElements.define(Library, LibraryElement)
