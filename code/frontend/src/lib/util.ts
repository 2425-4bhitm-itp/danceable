function clear(element: HTMLElement | ShadowRoot | undefined) {
    while(element?.firstChild) {
        element.firstChild.remove()
    }
}
function addOrRemoveElementClass(forClass: string, element: HTMLElement, add: boolean) {
    function addRemove() {
        if (element) {
            if (add) {
                element.classList.add(forClass)
            } else {
                element.classList.remove(forClass)
            }
        }
    }
    setTimeout(addRemove, 0)
}
function truncate(text: string, numberOfCharacters: number){
    return text.length > numberOfCharacters ? text.slice(0, numberOfCharacters-1) + '&hellip;' : text
}
export { clear, addOrRemoveElementClass, truncate }
