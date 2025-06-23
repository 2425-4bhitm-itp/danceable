#if os(watchOS)
class WatchOSOrientationStrategy: OrientationStrategy {
    override init() {
        super.init()
        orientation = .portrait // fixed portrait
    }
}
#endif
