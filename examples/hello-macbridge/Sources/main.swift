import Foundation

#if canImport(UIKit)
import UIKit
print("Hello from MacBridge on a real Mac (UIKit available: \(UIDevice.current.systemName))")
#else
print("Hello from MacBridge on a real Mac (toolchain Apple, sem UIKit neste target)")
#endif
