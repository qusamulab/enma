"use strict";
// Observe CommonCrypto calls. Output matches the Android crypto analyzer schema.
const keys = [];
const hooked = new Set();
const algorithms = ["AES", "DES", "3DES", "CAST", "RC4", "RC2", "Blowfish"];
const moduleObserver = Process.attachModuleObserver({
    onAdded(mod) {
        for (const symbol of ["CCCrypt", "CCCryptorCreate", "CCCryptorCreateWithMode"]) {
            const address = mod.findExportByName(symbol);
            if (address === null || hooked.has(address.toString())) continue;
            hooked.add(address.toString());
            Interceptor.attach(address, {
                onEnter(args) {
                    if (keys.length >= 2000) return;
                    try {
                        const withMode = symbol === "CCCryptorCreateWithMode";
                        const algorithm = args[withMode ? 2 : 1].toInt32();
                        const key = args[withMode ? 5 : 3];
                        const size = args[withMode ? 6 : 4].toUInt32();
                        if (size === 0 || size > 512 || key.isNull()) return;
                        keys.push({ ts: Date.now(), api: symbol,
                            algorithm: algorithms[algorithm] || `CommonCrypto:${algorithm}`,
                            operation: args[0].toInt32(),
                            key_hex: Array.from(new Uint8Array(key.readByteArray(size)))
                                .map(byte => byte.toString(16).padStart(2, "0")).join("") });
                    } catch (_) {}
                },
            });
        }
    },
});
function flush() {
    if (keys.length) send({ event: "json", name: "crypto_keys.json", data: keys });
}
setInterval(flush, 10000);
