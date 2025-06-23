#if os(iOS)
import UIKit
import Combine

class iOSOrientationStrategy: OrientationStrategy {
    private var cancellable: AnyCancellable?
    
    override init() {
        super.init()
        UIDevice.current.beginGeneratingDeviceOrientationNotifications()
        orientation = Self.convert(UIDevice.current.orientation)
        
        cancellable = NotificationCenter.default
            .publisher(for: UIDevice.orientationDidChangeNotification)
            .sink { [weak self] _ in
                self?.orientation = Self.convert(UIDevice.current.orientation)
            }
    }
    
    deinit {
        UIDevice.current.endGeneratingDeviceOrientationNotifications()
        cancellable?.cancel()
    }
    
    private static func convert(_ deviceOrientation: UIDeviceOrientation) -> InterfaceOrientation {
        switch deviceOrientation {
        case .portrait, .portraitUpsideDown:
            return .portrait
        case .landscapeLeft, .landscapeRight:
            return .landscape
        default:
            return .unknown
        }
    }
}
#endif
