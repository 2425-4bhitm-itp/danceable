/** A function that is called by a subject when something changed */
type Callback<T> = (model: T) => void

/** a function that works on a result */
type PipeFunction<T> = (t: T) => T

/** an element of a pipe */
interface Operator<T> {
  name?: string,
  lastValue?: T,
  apply: PipeFunction<T>
}

/** something that can be subscribed to */
interface Subscribable<T> {
  subscribe: (callback: Callback<T>) => void
  aSubscriptionWasDoneBy: (callback: Callback<T>) => void
}

class Pipe<T extends object> implements Subscribable<T> {
  callback: Callback<T> = t => { }
  operators: Operator<T>[] = []
  parent: Subscribable<T>

  add(operators: PipeFunction<T>[]) {
    for (const cb of operators) {
      const name = this.operators.length.toString()
      const operator: Operator<T> = {
        apply: cb,
        name
      }
      operator.apply = operator.apply.bind(operator)
      this.operators.push(operator)
    }
  }
  addParent(parent: Subscribable<T>) {
    this.parent = parent
    const process = (t: T) => {
      log("Pipe: value received from parent", t)
      let result = t
      for (const op of this.operators) {
        if (result) {
          log("apply operator", op.name, "with", result, "lastValue", op.lastValue)
          result = op.apply(result)
          log("result operator", op.name, "=", result)
        } else {
          log("skip, cause result is", result)
        }
      }
      if (result) {
        log("callback with", result)
        this.callback(result)
      } else {
        log("no callback cause undefined")
      }
    }
    parent.subscribe(process)
  }
  /** register a function that is called when our model changes */
  subscribe(callback: Callback<T>) {
    this.callback = callback
    this.parent.aSubscriptionWasDoneBy(callback)
  }
  aSubscriptionWasDoneBy(callback: Callback<T>) {
    this.parent.aSubscriptionWasDoneBy(callback)
  }
}


/** an Observable that can be subscribed by multiple observers
 */
class Subject<T extends object> implements ProxyHandler<T>, Subscribable<T> {
  protected subscriptions: Callback<T>[] = []
  protected proxy: T
  model: T

  /**
   * @param model the single source of truth model that is observed
   */
  constructor(model: T) {
    this.model = model
    this.proxy = new Proxy(model, this)
  }
  subscribe(callback: Callback<T>) {
    this.subscriptions.push(callback)
    this.aSubscriptionWasDoneBy(callback)
  }
  aSubscriptionWasDoneBy (callback: Callback<T>) {
    callback(this.model)
  }
  get(target: T, property: string | symbol, receiver: any): any {
    return Reflect.get(target, property, receiver)
  }
  set(target: T, property: string | symbol, newValue: any, receiver: any) {
    const wasSet = Reflect.set(target, property, newValue, receiver)
    if (wasSet) {
      this.emit(target)
    }
    return wasSet
  }
  emit(t: T) {
    for (const subscription of this.subscriptions) {
      subscription(t)
    }
  }
  get value() {
    return this.proxy
  }
  /** add operators that are processed before the callback function is called
   */
  pipe(...operators: PipeFunction<T>[]) {
    const pipe = new Pipe<T>()
    pipe.add(operators)
    pipe.addParent(this)
    return pipe
  }
}
/** only do callbacks when the comparator does not say that it is the same.
 */
function distinctUntilChanged<T extends object>(comparator: (prev: T, cur: T) => boolean) {
  function op(this: Operator<T>, t: T) {
    log("in distinctUntilChanged with", t, "with lastvalue=", this.lastValue)
    let result = t
    if (this.lastValue) {
      const isEqual = comparator(this.lastValue, t)
      if (isEqual) {
        result = undefined
        log("no change, lastValue", this.lastValue, "current", t)
      } else {
        this.lastValue = structuredClone(result)
        log("set lastValue", result)
      }
    } else {
      log("distinctUntilChanged: no lastvalue, set lastValue to", result)
      this.lastValue = structuredClone(result)
    }
    log("exit distinctUntilChanged returns", result, "lastValue=", this.lastValue)
    return result
  }
  return op
}
/** only forward when filter function returns true */
function filter<T extends object>(filter: (t: T) => boolean) {
  function op(t: T) {
    let result = filter(t) ? t : undefined
    return result
  }
  return op
}
/** only launch a side effect, e.g. log. */
function peek<T extends object>(sideEffekt: (t: T) => void) {
  function op(t: T) {
    const value = this.model
    sideEffekt(value)
    return t
  }
  return op
}
function apply<T extends object>(subject: Subject<T>, recipe: (store: T) => void) {
  recipe(subject.value)
}
const DEBUG = true
function log(message?: any, ...optionalParams: any[]) {
  if (DEBUG) {
    console.log(message, optionalParams)
  }
}

export { Subject, distinctUntilChanged, filter, peek, apply }