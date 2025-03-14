import { html, render } from 'lib/pure-html'
import { AppMenu } from 'components/menu'

class ApplicationElement extends HTMLElement {
  connectedCallback() {
    this.render()
  }

  render() {
    render(
      html`
        <${AppMenu}></${AppMenu}>
      `,
      this
    )
  }
}

export const App = 'application-component'

customElements.define(App, ApplicationElement)