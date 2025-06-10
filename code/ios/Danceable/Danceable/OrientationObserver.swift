import SwiftUI
import Combine

class OrientationObserver: ObservableObject {
    @Published var orientation: UIDeviceOrientation = UIDevice.current.orientation
    
    private var cancellable: AnyCancellable?
    
    init() {
        UIDevice.current.beginGeneratingDeviceOrientationNotifications()
        
        cancellable = NotificationCenter.default
            .publisher(for: UIDevice.orientationDidChangeNotification)
            .sink { _ in
                self.orientation = UIDevice.current.orientation
            }
    }
    
    deinit {
        UIDevice.current.endGeneratingDeviceOrientationNotifications()
        cancellable?.cancel()
    }
}
