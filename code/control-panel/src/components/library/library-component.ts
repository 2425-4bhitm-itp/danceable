import { html, render, renderAppendChild } from 'lib/pure-html'
import { addLinks } from 'lib/router'
import { set, store } from 'model/index'
import { clear } from 'lib/util'

import { SnippetComponent, SnippetElement } from 'components/snippet/snippet-component'
import { DanceFilter } from 'model/dance-filter/dance-filter'
import { Snippet } from 'model/snippet/snippet'
import { Dance } from 'model/dance/dance'
import { produce } from 'lib/immer'
import { distinctUntilChanged } from 'lib/observable'
import { Song } from 'model/song/song'

export const Library = 'library-component'
export const libraryRoute = 'library'

class LibraryElement extends HTMLElement {
  static observedAttributes = ['hidden']

  constructor() {
    super()
  }

  async connectedCallback() {
    store
      .pipe(
        distinctUntilChanged(
          (prev, cur) => prev.dances === cur.dances && prev.danceFilters === cur.danceFilters
        )
      )
      .subscribe((model) => {
        this.renderDanceFilters(model.danceFilters, model.dances)
      })

    this.render()

    store
      .pipe(
        distinctUntilChanged(
          (prev, cur) =>
            prev.snippets === cur.snippets &&
            prev.danceFilters === cur.danceFilters &&
            prev.songs === cur.songs
        )
      )
      .subscribe((model) => {
        this.renderedFilteredSnippets(model.snippets, model.danceFilters, model.songs)
      })
  }

  render() {
    render(
      html`
        <div class="h-full overflow-y-auto">
          <div class="px-2 pt-9 pb-2 text-3xl">Library</div>
          <div id="danceFilters" class="flex flex-wrap gap-2 p-2"></div>
          <div id="snippets" class="flex w-full flex-col items-center"></div>
        </div>
      `,
      this
    )

    addLinks(this)
  }

  renderDanceFilters(danceFilters: DanceFilter[], dances: Dance[]) {
    const danceFilterContainer: HTMLElement = this.querySelector('#danceFilters')

    if (danceFilterContainer && Array.isArray(danceFilters)) {
      clear(danceFilterContainer)

      danceFilters.forEach((filter) => {
        const dance = dances.find((d) => d.id === filter.danceId)

        const filterElement = renderAppendChild(
          html`
            <span
              class="${filter.isEnabled
                ? 'bg-gray-300'
                : 'bg-gray-100'} cursor-pointer rounded-full p-0.5 px-3 select-none"
            >
              ${dance.name}
            </span>
          `,
          danceFilterContainer
        )

        filterElement.addEventListener('click', (e) => {
          this.filterClicked(filter)
        })
      })
    }
  }

  renderedFilteredSnippets(snippets: Snippet[], danceFilters: DanceFilter[], songs: Song[]) {
    const enabledDanceFilterIds = danceFilters.filter((f) => f.isEnabled).map((f) => f.danceId)

    if (enabledDanceFilterIds.length == 0) {
      this.renderSnippets(snippets)
    } else {
      this.renderSnippets(
        snippets.filter((s) => {
          const song = songs.find((d) => d.id === s.songId)

          return song && song.danceIds.some((id) => enabledDanceFilterIds.includes(id))
        })
      )
    }
  }

  renderSnippets(snippets: Snippet[]) {
    const snippetsContainer: HTMLElement = this.querySelector('#snippets')
    clear(snippetsContainer)

    if (Array.isArray(snippets)) {
      snippets.forEach((snippet) => {
        const snippetElement = document.createElement(SnippetComponent) as SnippetElement
        snippetElement.classList.add(...['w-full', 'px-4'])
        snippetElement.state = snippet

        snippetsContainer.appendChild(snippetElement)

        snippetElement.addEventListener('snippet-option-clicked', (e: CustomEvent) =>
          this.snippetOptionsClicked(snippetElement, e)
        )
      })
    }
  }

  private snippetOptionsClicked(snippet: SnippetElement, e: CustomEvent) {
    const snippetElements = this.querySelector('#snippets').childNodes as NodeListOf<SnippetElement>

    snippetElements.forEach((s) => {
      if (s.state.id !== snippet.state.id) {
        s.openOrCloseOptions(false)
      }
    })
  }

  private filterClicked(filter: DanceFilter) {
    set((model) => {
      model.danceFilters = model.danceFilters.map((danceFilter) => {
        if (danceFilter.danceId === filter.danceId) {
          return produce(danceFilter, (draft) => {
            draft.isEnabled = !draft.isEnabled
          })
        } else {
          return danceFilter
        }
      })
    })
  }
}

customElements.define(Library, LibraryElement)
