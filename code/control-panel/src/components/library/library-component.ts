import { html, render, renderAppendChild } from 'lib/pure-html'
import { addLinks } from 'lib/router'
import { set, subscribe } from 'model/model'
import { clear } from 'lib/util'

import { SnippetComponent, SnippetElement } from 'components/snippet/snippet-component'
import { DanceFilter } from 'model/dance-filter/dance-filter'
import { Snippet } from 'model/snippet/snippet'
import { Dance } from 'model/dance/dance'
import { produce } from 'lib/immer'

export const Library = 'library-component'
export const libraryRoute = 'library'

class LibraryElement extends HTMLElement {
  static observedAttributes = ['hidden']

  constructor() {
    super()
  }

  async connectedCallback() {
    subscribe(model => {
      this.renderDanceFilters(model.danceFilters, model.dances)
    })

    this.render()

    subscribe(
      (model) => {
        const enabledDanceFilterIds = model.danceFilters
          .filter(f => f.isEnabled)
          .map(f => f.danceId)

        if (enabledDanceFilterIds.length == 0) {
          this.renderSnippets(model.snippets)
        } else {
          this.renderSnippets(
            model.snippets.filter(s =>
              s.song &&
              s.song.dances
                .some(d => enabledDanceFilterIds.includes(d.id)),
            ),
          )
        }
      },
    )
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

  renderDanceFilters(danceFilters: DanceFilter[], dances: Dance[]) {
    const danceFilterContainer: HTMLElement = this.querySelector('#danceFilters')

    if (danceFilterContainer && Array.isArray(danceFilters)) {
      clear(danceFilterContainer)

      danceFilters.forEach(filter => {
        const dance = dances.find(d => d.id === filter.danceId)

        const filterElement = renderAppendChild(
          html`
            <span
              class="p-0.5 px-3 select-none cursor-pointer ${filter.isEnabled ? 'bg-gray-300' : 'bg-gray-100'} rounded-full">
              ${dance.name}
            </span>
          `, danceFilterContainer,
        )

        filterElement.addEventListener('click', (e) => {
          this.filterClicked(filter)
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
    const snippetElements = this.querySelector('#snippets').childNodes as NodeListOf<SnippetElement>

    snippetElements.forEach(s => {
      if (s.state.id !== snippet.state.id) {
        s.openOrCloseOptions(false)
      }
    })
  }

  private filterClicked(filter: DanceFilter) {
    set(model => {
      model.danceFilters = model.danceFilters.map(danceFilter => {
          if (danceFilter.danceId === filter.danceId) {
            return produce(danceFilter, draft => {
              draft.isEnabled = !draft.isEnabled
            })
          } else {
            return danceFilter
          }
        },
      )
    })
  }
}

customElements.define(Library, LibraryElement)
