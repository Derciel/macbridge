// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "hello-macbridge",
    platforms: [.iOS(.v15)],
    targets: [
        .executableTarget(
            name: "hello-macbridge",
            path: "Sources"
        )
    ]
)
