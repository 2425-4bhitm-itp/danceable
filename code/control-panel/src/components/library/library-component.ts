import { html, render, renderAppendChild } from 'lib/pure-html'
import { addLinks } from 'lib/router'
import { set, store } from 'model/index'
import { clear } from 'lib/util'

import { SnippetComponent, SnippetElement } from 'components/snippet/snippet-component'
import { DanceFilter } from 'model/dance-filter/dance-filter'
import { Snippet } from 'model/snippet/snippet'
import { Dance } from 'model/dance/dance'
import { produce } from 'lib/immer'
import { Song } from 'model/song/song'
import { EditSongElement, EditSongComponent } from 'components/edit-song/edit-song-component'
import {
  SwitchSongElement,
  SwitchSongComponent,
} from 'components/switch-song/switch-song-component'
import { deleteSnippet } from 'model/snippet/snippet-service'

export const Library = 'library-component'
export const libraryRoute = 'library'

class LibraryElement extends HTMLElement {
  async connectedCallback() {
    store.subscribe((model) => {
      this.renderDanceFilters(model.danceFilters, model.dances)
    })

    this.render()

    store.subscribe((model) => {
      this.renderedFilteredSnippets(model.snippets, model.danceFilters, model.songs)
    })
  }

  render() {
    render(
      html`
        <div class="h-full overflow-y-auto">
          <div class="px-2 pt-9 pb-2 text-3xl">Library</div>
          <div class="flex flex-row-reverse px-4"><button id="uploadSnippetButton" class="cursor-pointer py-1 px-5 bg-gray-dark rounded-xl font-medium text-white">upload snippet</button></div>
          <div id="danceFilters" class="flex flex-wrap gap-2 p-2"></div>
          <div id="snippets" class="flex w-full flex-col items-center"></div>
          <${EditSongComponent}></${EditSongComponent}>
          <${SwitchSongComponent}></${SwitchSongComponent}>
        </div>
      `,
      this
    )

    const uploadSnippetButton = document.querySelector('button#uploadSnippetButton')

    uploadSnippetButton?.addEventListener('click', () => {})

    addLinks(this)
  }

  renderDanceFilters(danceFilters: DanceFilter[], dances: Map<number, Dance>) {
    const danceFilterContainer: HTMLElement = this.querySelector('#danceFilters')

    if (danceFilterContainer && Array.isArray(danceFilters)) {
      clear(danceFilterContainer)

      danceFilters.forEach((filter) => {
        const dance = dances.get(filter.danceId)

        const filterElement = renderAppendChild(
          html`
            <button
              class="${filter.isEnabled
                ? 'bg-gray-300'
                : 'bg-gray-100'} cursor-pointer rounded-full p-0.5 px-3 select-none"
            >
              ${dance.name}
            </button>
          `,
          danceFilterContainer
        )

        filterElement.addEventListener('click', (e) => {
          this.filterClicked(filter)
        })
      })
    }
  }

  renderedFilteredSnippets(
    snippets: Snippet[],
    danceFilters: DanceFilter[],
    songs: Map<number, Song>
  ) {
    const enabledDanceFilterIds = danceFilters.filter((f) => f.isEnabled).map((f) => f.danceId)

    if (enabledDanceFilterIds.length == 0) {
      this.renderSnippets(snippets)
    } else {
      this.renderSnippets(
        snippets.filter((s) => {
          const song = songs.get(s.songId)

          return song && enabledDanceFilterIds.includes(song.danceId)
        })
      )
    }
  }

  renderSnippets(snippets: Snippet[]) {
    const snippetsContainer: HTMLElement = this.querySelector('#snippets')
    clear(snippetsContainer)

    if (Array.isArray(snippets)) {
      snippets
        .sort((s1, s2) => s1.id - s2.id)
        .forEach((snippet) => {
          const snippetElement = document.createElement(SnippetComponent) as SnippetElement
          snippetElement.classList.add(...['w-full', 'px-4'])
          snippetElement.snippet = snippet

          snippetsContainer.appendChild(snippetElement)

          snippetElement.addEventListener('snippet-options-clicked', (e: CustomEvent) =>
            this.snippetOptionsClicked(snippetElement, e)
          )

          snippetElement.addEventListener('edit-song', (e: CustomEvent) => {
            this.closeAllSnippetOptions()
            set((model) => {
              model.songToEdit = snippetElement.snippet.songId
            })
            const editSongElement: EditSongElement = document.querySelector(EditSongComponent)
            editSongElement?.show()
          })

          snippetElement.addEventListener('switch-song', (e: CustomEvent) => {
            this.closeAllSnippetOptions()
            set((model) => (model.snippetToSwitchSong = snippetElement.snippet.id))
            const switchSongElement: SwitchSongElement = document.querySelector(SwitchSongComponent)
            switchSongElement?.show()
          })

          snippetElement.addEventListener('delete-snippet', (e: CustomEvent) => {
            deleteSnippet(snippetElement.snippet.id)

            this.closeAllSnippetOptions()
            set((model) => {
              const snippetIndex = model.snippets.findIndex(
                (s) => s.id === snippetElement.snippet.id
              )

              model.snippets.splice(snippetIndex, 1)
              model.snippetToSwitchSong = -1
            })
          })
        })
    }
  }

  private snippetOptionsClicked(snippet: SnippetElement, e: CustomEvent) {
    const snippetElements = this.querySelector('#snippets').childNodes as NodeListOf<SnippetElement>

    snippetElements.forEach((s) => {
      if (s.snippet.id !== snippet.snippet.id) {
        s.openOrCloseOptions(false)
      }
    })
  }

  private closeAllSnippetOptions() {
    const snippetElements = this.querySelector('#snippets').childNodes as NodeListOf<SnippetElement>

    snippetElements.forEach((s) => {
      s.openOrCloseOptions(false)
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
