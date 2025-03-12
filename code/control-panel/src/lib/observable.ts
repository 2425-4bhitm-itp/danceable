/** small replacement for RxJs
 * @see https://reactivex.io/
 * @author Christian Aberger
 * (c) Christian Aberger (2025)
 * https://www.aberger.at
 */

type Subscription<T> = (model: T) => void

export class Observable<T extends object> implements ProxyHandler<T> {
    private readonly subscriptions = new Set<Subscription<T>>()
    private proxy: T
  
    constructor(initialState: T) {
        this.proxy = new Proxy(initialState, this)
    }
    get(target: T, property: string | symbol, receiver: any): any {
        return Reflect.get(target, property, receiver)
    }
    set(target: T, property: string | symbol, newValue: any, receiver: any) {
        const wasSet = Reflect.set(target, property, newValue, receiver)
        if (wasSet) {
            this.subscriptions.forEach(subscription => subscription(target))   
        }
        return wasSet
    }
    subscribe(subscription: Subscription<T>): void {
        this.subscriptions.add(subscription)
        subscription(this.proxy)
    }
    get value() {
        return this.proxy
    }
}


type Comparator<T> = (prev: T, cur: T) => boolean
function distinctUntilChanged<T>(comp: Comparator<T>) {
    return false
}