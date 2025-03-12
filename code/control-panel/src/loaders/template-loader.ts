/** a webpack loader to load html-templates.
  * (c) Christian Aberger (2025)
 * @author Christian Aberger
 * https://www.aberger.at
 */

function template<T>(content: T) {
    const code = `
        function template(model) {
            const templateElement = document.createElement("template")
            templateElement.innerHTML = \`${content}\`
            return templateElement
        }
    `
    const exportString = "module.exports = " + code
    return exportString
}
export default template