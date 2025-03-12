/** Map files ending with -template.html to your loader.
 * (c) Christian Aberger (2025)
 * @author Christian Aberger
 * https://www.aberger.at
 */

declare module "*-template.html" {
    const value: (content?: any) => HTMLTemplateElement
    export default value
}
