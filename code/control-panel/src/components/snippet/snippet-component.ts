import { html, render } from 'lib/pure-html'
import { addLinks } from 'lib/router'

import { Snippet } from 'model/snippet/snippet'
import { store } from 'model/model'
import { Song } from 'model/song/song'
import { distinctUntilChanged } from 'lib/observable'
import { Dance } from 'model/dance/dance'

export const SnippetComponent = 'snippet-component'

export class SnippetElement extends HTMLElement {
  static observedAttributes = ['hidden']

  state: Snippet

  isOptionsOpen: boolean = false

  constructor(state: Snippet) {
    super()
  }

  connectedCallback() {
    store
      .pipe(
        distinctUntilChanged(
          (prev, cur) => prev.snippets == cur.snippets && prev.dances == prev.dances
        )
      )
      .subscribe((model) => {
        this.state = model.snippets.find((s) => s.id === this.state.id)

        this.render(model.songs, model.dances)
      })
  }

  render(allSongs: Song[], allDances: Dance[]) {
    const song = allSongs.find((s) => s.id === this.state.songId)

    if (song) {
      const danceMap = new Map(allDances.map((dance) => [dance.id, dance]))

      const dances: Dance[] = song.danceIds.flatMap((id): Dance | [] => danceMap.get(id) ?? [])

      render(
        html`
          <div
            class="flex w-full items-center gap-5 border-t-2 border-t-gray-100 py-1.5 select-none"
          >
            <span> ${this.state.fileName} (${this.state.songSnippetIndex}) </span>
            <span class="text-gray-400"> ${song.speed} bpm </span>
            <div class="flex flex-1 flex-row-reverse gap-2">
              ${dances
                .map(
                  (dance) =>
                    '<span class="p-0.5 px-3 bg-gray-100 rounded-full">' + dance.name + '</span>'
                )
                .join('')}
            </div>
            <div class="relative w-8">
              <modal
                hidden
                class="snippet-options absolute top-0 right-8 flex min-w-12 flex-col rounded-md bg-white p-1 text-nowrap shadow"
              >
                <span class="rounded px-2 py-1 text-purple-500 hover:bg-gray-100">analyse</span>
                <span class="rounded px-2 py-1 hover:bg-gray-100">edit song</span>
                <span class="rounded px-2 py-1 text-red-400 hover:bg-gray-100">remove snippet</span>
              </modal>
              <div
                class="snippet-options-button flex aspect-square w-full items-center justify-center rounded-md hover:bg-gray-100"
              >
                <img class="w-full" src="/public/svgs/options-icon-dark.svg" alt="options button" />
              </div>
            </div>
          </div>
        `,
        this
      )

      this.querySelector('.snippet-options-button').addEventListener('click', (e: MouseEvent) =>
        this.optionsClicked()
      )

      addLinks(this)
    }
  }

  optionsClicked() {
    this.dispatchEvent(new CustomEvent('snippet-option-clicked', { detail: this.state }))

    this.openOrCloseOptions(!this.isOptionsOpen)
  }

  openOrCloseOptions(changeOptionsTo: boolean) {
    this.isOptionsOpen = changeOptionsTo

    const optionsElement = this.querySelector('modal.snippet-options')

    if (optionsElement) {
      if (this.isOptionsOpen) {
        optionsElement.removeAttribute('hidden')
      } else {
        optionsElement.setAttribute('hidden', '')
      }
    }
  }
}

customElements.define(SnippetComponent, SnippetElement)
