"use strict";
// Compatibility for the module lookup API used by the shipped agents.
// Frida 17 exposes lookups on module instances and global exports separately.
if (typeof Module.findExportByName !== "function") {
    Module.findExportByName = function (name, symbol) {
        if (name === null) return Module.findGlobalExportByName(symbol);
        const mod = Process.findModuleByName(name);
        return mod ? mod.findExportByName(symbol) : null;
    };
    Module.getExportByName = function (name, symbol) {
        const address = Module.findExportByName(name, symbol);
        if (address === null) throw new Error(`Missing export: ${name}!${symbol}`);
        return address;
    };
    Module.enumerateExports = function (name) {
        const mod = Process.findModuleByName(name);
        return mod ? mod.enumerateExports() : [];
    };
}
