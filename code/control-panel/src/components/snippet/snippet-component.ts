import { html, render } from 'lib/pure-html'
import { addLinks } from 'lib/router'

import { Snippet } from 'model/snippet/snippet'

export const SnippetComponent = 'snippet-component'

export class SnippetElement extends HTMLElement {
  static observedAttributes = ['hidden']

  state: Snippet

  constructor(state: Snippet) {
    super()
  }

  connectedCallback() {
    this.render()

    this.querySelector('img.snippet-options').addEventListener(
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
        <span class="cursor-pointer w-8">
          <img class="snippet-options w-full" src="/public/svgs/options-icon-dark.svg" alt="options button">
        </span>
      </div>
    `, this)

    addLinks(this)
  }

  optionsClicked() {
    this.dispatchEvent(
      new CustomEvent('snippet-option-clicked', { detail: this.state }),
    )
  }
}

customElements.define(SnippetComponent, SnippetElement)
