"use strict";
// Bundle metadata and loaded Mach-O images, using Frida's Objective-C bridge.
function snapshot() {
    const data = {
        platform: "ios", arch: Process.arch,
        modules: Process.enumerateModules().map(mod => ({
            name: mod.name, path: mod.path, base: mod.base.toString(), size: mod.size,
        })),
    };
    if (ObjC.available) {
        const bundle = ObjC.classes.NSBundle.mainBundle();
        const info = bundle.infoDictionary();
        const value = key => {
            const object = info.objectForKey_(key);
            return object ? object.toString() : null;
        };
        data.bundle_id = bundle.bundleIdentifier()?.toString() ?? null;
        data.bundle_path = bundle.bundlePath().toString();
        data.name = value("CFBundleDisplayName") || value("CFBundleName");
        data.version = value("CFBundleShortVersionString");
        data.build = value("CFBundleVersion");
    }
    send({ event: "json", name: "ios_app.json", data });
}
setImmediate(snapshot);

