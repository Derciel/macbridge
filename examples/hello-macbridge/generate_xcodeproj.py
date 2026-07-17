"""Gera um .xcodeproj minimalista (Hello World UIKit) sem precisar do Xcode.

Prova que da pra criar um projeto iOS valido via linha de comando -- exatamente
o que o macbridge faz quando aponta para um Mac real: o usuario escreve em qualquer
lugar, o build acontece num Mac com toolchain Apple.
"""
from __future__ import annotations

import argparse
from pathlib import Path

# IDs 24-hex estaveis (formato pbxproj)
P = "A1" + "0" * 22
IDS = {
    "root":        P + "01",
    "project":     P + "02",
    "mainGroup":   P + "03",
    "products":    P + "04",
    "target":      P + "05",
    "srcPhase":    P + "06",
    "fwPhase":     P + "07",
    "resPhase":    P + "08",
    "mainFile":    P + "09",
    "appFile":     P + "0A",
    "cfgListProj": P + "0B",
    "cfgListTgt":  P + "0C",
    "cfgDebug":    P + "0D",
    "cfgRelease":  P + "0E",
    "grpSources":  P + "0F",
}


def pbxproj(name: str) -> str:
    return f"""// !$*UTF8*$!
{{
	archiveVersion = 1;
	classes = {{}};
	objectVersion = 56;
	objects = {{

/* Begin PBXBuildFile section */
		{IDS['mainFile']} /* main.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {IDS['mainFile']} /* main.swift */; }};
/* End PBXBuildFile section */

/* Begin PBXFileReference section */
		{IDS['mainFile']} /* main.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = main.swift; sourceTree = "<group>"; }};
		{IDS['appFile']} /* {name}.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = {name}.app; sourceTree = BUILT_PRODUCTS_DIR; }};
/* End PBXFileReference section */

/* Begin PBXFrameworksBuildPhase section */
		{IDS['fwPhase']} /* Frameworks */ = {{
			isa = PBXFrameworksBuildPhase;
			buildActionMask = 2147483647;
			files = (
			);
			runOnlyForDeploymentPostprocessing = 0;
		}};
/* End PBXFrameworksBuildPhase section */

/* Begin PBXGroup section */
		{IDS['mainGroup']} = {{
			isa = PBXGroup;
			children = (
				{IDS['grpSources']},
				{IDS['products']},
			);
			sourceTree = "<group>";
		}};
		{IDS['grpSources']} = {{
			isa = PBXGroup;
			children = (
				{IDS['mainFile']},
			);
			path = Sources;
			sourceTree = "<group>";
		}};
		{IDS['products']} = {{
			isa = PBXGroup;
			children = (
				{IDS['appFile']},
			);
			name = Products;
			sourceTree = "<group>";
		}};
/* End PBXGroup section */

/* Begin PBXNativeTarget section */
		{IDS['target']} /* {name} */ = {{
			isa = PBXNativeTarget;
			buildConfigurationList = {IDS['cfgListTgt']} /* Build configuration list for PBXNativeTarget "{name}" */;
			buildPhases = (
				{IDS['srcPhase']} /* Sources */,
				{IDS['fwPhase']} /* Frameworks */,
				{IDS['resPhase']} /* Resources */,
			);
			buildRules = (
			);
			dependencies = (
			);
			name = {name};
			productName = {name};
			productReference = {IDS['appFile']} /* {name}.app */;
			productType = "com.apple.product-type.application";
		}};
/* End PBXNativeTarget section */

/* Begin PBXProject section */
		{IDS['project']} /* Project object */ = {{
			isa = PBXProject;
			attributes = {{
				BuildIndependentTargetsInParallel = 1;
				LastSwiftUpdateCheck = 1500;
				LastUpgradeCheck = 1500;
				TargetAttributes = {{
					{IDS['target']} = {{
						CreatedOnToolsVersion = 15.0;
					}};
				}};
			}};
			buildConfigurationList = {IDS['cfgListProj']} /* Build configuration list for PBXProject "{name}" */;
			compatibilityVersion = "Xcode 14.0";
			developmentRegion = en;
			hasScannedForEncodings = 0;
			knownRegions = (
				en,
				Base,
			);
			mainGroup = {IDS['mainGroup']};
			productRefGroup = {IDS['products']} /* Products */;
			projectDirPath = "";
			projectRoot = "";
			targets = (
				{IDS['target']} /* {name} */,
			);
		}};
/* End PBXProject section */

/* Begin PBXResourcesBuildPhase section */
		{IDS['resPhase']} /* Resources */ = {{
			isa = PBXResourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
			);
			runOnlyForDeploymentPostprocessing = 0;
		}};
/* End PBXResourcesBuildPhase section */

/* Begin PBXSourcesBuildPhase section */
		{IDS['srcPhase']} /* Sources */ = {{
			isa = PBXSourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
				{IDS['mainFile']} /* main.swift in Sources */,
			);
			runOnlyForDeploymentPostprocessing = 0;
		}};
/* End PBXSourcesBuildPhase section */

/* Begin XCBuildConfiguration section */
		{IDS['cfgDebug']} /* Debug */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
				ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
				CODE_SIGNING_ALLOWED = NO;
				"CODE_SIGN_IDENTITY[sdk=macosx*]" = "-";
				CURRENT_PROJECT_VERSION = 1;
				ENABLE_USER_SCRIPT_SANDBOXING = YES;
				GENERATE_INFOPLIST_FILE = YES;
				INFOPLIST_KEY_UIApplicationSceneManifest_Generation = YES;
				INFOPLIST_KEY_UIApplicationSupportsIndefinitePointerException = YES;
				IPHONEOS_DEPLOYMENT_TARGET = 15.0;
				LD_RUNPATH_SEARCH_PATHS = (
					"$(inherited)",
					"@executable_path/Frameworks",
				);
				MARKETING_VERSION = 1.0;
				PRODUCT_BUNDLE_IDENTIFIER = "com.macbridge.{name}";
				PRODUCT_NAME = "$(TARGET_NAME)";
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_VERSION = 5.0;
				TARGETED_DEVICE_FAMILY = "1,2";
			}};
			name = Debug;
		}};
		{IDS['cfgRelease']} /* Release */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
				ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
				CODE_SIGNING_ALLOWED = NO;
				"CODE_SIGN_IDENTITY[sdk=macosx*]" = "-";
				CURRENT_PROJECT_VERSION = 1;
				ENABLE_USER_SCRIPT_SANDBOXING = YES;
				GENERATE_INFOPLIST_FILE = YES;
				INFOPLIST_KEY_UIApplicationSceneManifest_Generation = YES;
				INFOPLIST_KEY_UIApplicationSupportsIndefinitePointerException = YES;
				IPHONEOS_DEPLOYMENT_TARGET = 15.0;
				LD_RUNPATH_SEARCH_PATHS = (
					"$(inherited)",
					"@executable_path/Frameworks",
				);
				MARKETING_VERSION = 1.0;
				PRODUCT_BUNDLE_IDENTIFIER = "com.macbridge.{name}";
				PRODUCT_NAME = "$(TARGET_NAME)";
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_VERSION = 5.0;
				TARGETED_DEVICE_FAMILY = "1,2";
			}};
			name = Release;
		}};
/* End XCBuildConfiguration section */

/* Begin XCConfigurationList section */
		{IDS['cfgListProj']} /* Build configuration list for PBXProject "{name}" */ = {{
			isa = XCConfigurationList;
			buildConfigurations = (
				{IDS['cfgDebug']} /* Debug */,
				{IDS['cfgRelease']} /* Release */,
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		}};
		{IDS['cfgListTgt']} /* Build configuration list for PBXNativeTarget "{name}" */ = {{
			isa = XCConfigurationList;
			buildConfigurations = (
				{IDS['cfgDebug']} /* Debug */,
				{IDS['cfgRelease']} /* Release */,
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		}};
/* End XCConfigurationList section */
	}};
	rootObject = {IDS['root']} /* Project object */;
}}
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="HelloMacBridge")
    ap.add_argument("--out", default="HelloMacBridge.xcodeproj")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "project.pbxproj").write_text(pbxproj(args.name), encoding="utf-8")
    print(f"[gen] {out/'project.pbxproj'} ({len(pbxproj(args.name))} bytes)")


if __name__ == "__main__":
    main()
