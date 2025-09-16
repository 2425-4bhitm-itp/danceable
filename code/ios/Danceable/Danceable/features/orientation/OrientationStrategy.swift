import SwiftUI
import Combine

// Have to use class because otherwise it can't be observable
//.portrait default assignment for Preview workaround, could be set to .unkown but wouldn't change much
class OrientationStrategy: ObservableObject {
    @Published var orientation: InterfaceOrientation = .portrait
}

enum InterfaceOrientation: Equatable {
    case portrait
    case landscape
    case unknown
}
