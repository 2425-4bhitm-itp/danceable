import { html, render } from 'lib/pure-html'
import { addLinks } from 'lib/router'

export const Analysis = 'analysis-component'
export const analysisRoute = 'analysis'

class AnalysisElement extends HTMLElement {
  static observedAttributes = ["hidden"]

  constructor() {
    super()
  }

  connectedCallback() {
    this.render()
  }

  render() {
    render(html` analysis `, this)
    addLinks(this)
  }
}

customElements.define(Analysis, AnalysisElement)
