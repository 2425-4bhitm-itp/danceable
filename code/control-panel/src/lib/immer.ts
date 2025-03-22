/** small replacement for immer.js
 * @see https://immerjs.github.io/immer/
 * (c) Christian Aberger (2025)
 * @author Christian Aberger
 * https://www.aberger.at
 */

type WriteableDraft<T> = { -readonly [P in keyof T]: WriteableDraft<T[P]> }

function produce<T>(baseState: T, recipe: (draft: WriteableDraft<T>) => void) {
    const clone = structuredClone(baseState)
    recipe(clone)
    return clone
}

export { produce, WriteableDraft }