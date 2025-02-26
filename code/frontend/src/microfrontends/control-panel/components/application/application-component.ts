import { render, html } from "../../../../lib/pure-html";
import application from "./application-component-template.html";

class ApplicationElement extends HTMLElement {
  connectedCallback() {
    this.render();
  }

  render() {
    render(application(), this);
  }
}

customElements.define("application-component", ApplicationElement);