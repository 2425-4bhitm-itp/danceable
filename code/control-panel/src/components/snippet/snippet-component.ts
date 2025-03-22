import { html, render } from 'lib/pure-html'
import { addLinks } from 'lib/router'

import { Snippet } from 'model/snippet/snippet'

export const SnippetComponent = 'snippet-component'

export class SnippetElement extends HTMLElement {
  static observedAttributes = ['hidden']

  state: Snippet

  isOptionsOpen: boolean = false

  constructor(state: Snippet) {
    super()
  }

  connectedCallback() {
    this.render()

    this.querySelector('img.snippet-options-button').addEventListener(
      'click',
      (e: MouseEvent) => this.optionsClicked(),
    )
  }

  render() {
    render(html`
      <div class="w-full py-1.5 flex gap-5 items-center select-none border-t-gray-100 border-t-2"
           data-id="${this.state.id}">
        <span>
          ${this.state.fileName}
            (${this.state.songSnippetIndex})
        </span>
        <span class="text-gray-400">
          ${this.state.speed} bpm
        </span>
        <div class="flex-1 flex flex-row-reverse gap-2">
          ${this.state.song.dances.map(
            dance => '<span class="p-0.5 px-3 bg-gray-100 rounded-full">' + dance.name + '</span>',
          ).join('')}
        </div>
        <div class="w-8 relative">
          <modal hidden class="snippet-options p-3 bg-white shadow absolute top-0 right-8 rounded-md">
            <span class="hover:underline">rename</span>
            <span class="hover:underline">edit</span>
            <span class="hover:underline text-red-500">remove</span>
          </modal>
          <img class="snippet-options-button w-full" src="/public/svgs/options-icon-dark.svg" alt="options button">
        </div>
        <!--        position a popup exaclty here (it are options to edit and delete)-->
      </div>
    `, this)

    addLinks(this)
  }

  optionsClicked() {
    this.isOptionsOpen = !this.isOptionsOpen
    this.openOrCloseOptions()
    // this.dispatchEvent(
    //   new CustomEvent('snippet-option-clicked', { detail: this.state }),
    // )
  }

  openOrCloseOptions() {
    const optionsElement = this.querySelector('modal.snippet-options')

    if (optionsElement) {
      if (!optionsElement.checkVisibility()) {
        optionsElement.removeAttribute('hidden')
      } else {
        optionsElement.setAttribute('hidden', '')
      }
    }
  }
}

customElements.define(SnippetComponent, SnippetElement)
