const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');

const root = path.join(__dirname, '../src/enma/agents');
const runtime = fs.readFileSync(path.join(root, '_runtime.js'), 'utf8');
const pointer = value => ({
    toInt32: () => value, toUInt32: () => value, toString: () => String(value),
    isNull: () => value === 0, readUtf8String: () => String(value),
    readByteArray: size => Uint8Array.from({length: size}, (_, i) => i).buffer,
});

function execute(filename, overrides = {}) {
    const messages = [], hooks = new Map(), timers = [], observers = [];
    const context = {
        Process: {
            platform: 'darwin', arch: 'arm64', enumerateModules: () => [],
            findModuleByName: () => null,
            attachModuleObserver(observer) { observers.push(observer); return {detach() {}}; },
        },
        Module: {findGlobalExportByName: () => null},
        Interceptor: {attach(address, callbacks) { hooks.set(String(address), callbacks); }},
        send: message => messages.push(message),
        setInterval: callback => timers.push(callback),
        setTimeout: () => {}, setImmediate: callback => callback(),
        ObjC: {available: false},
        ...overrides,
    };
    // Native iOS paths must never try to initialize Java.
    Object.defineProperty(context, 'Java', {get() { throw Error('Java used on iOS'); }});
    vm.runInNewContext(runtime + '\n' + fs.readFileSync(path.join(root, filename), 'utf8'), context);
    return {messages, hooks, timers, observers, context};
}

function moduleWith(exports) {
    return {findExportByName: name => exports.includes(name) ? name : null};
}

function lastData(result, filename) {
    result.timers.forEach(callback => callback());
    const message = result.messages.findLast(message => message.name === filename);
    assert.ok(message, `Missing ${filename}`);
    return JSON.parse(JSON.stringify(message.data));
}

test('all shipped agents parse as JavaScript', () => {
    for (const dir of fs.readdirSync(root, {withFileTypes: true}).filter(d => d.isDirectory())) {
        for (const filename of fs.readdirSync(path.join(root, dir.name)).filter(f => f.endsWith('.js'))) {
            new vm.Script(fs.readFileSync(path.join(root, dir.name, filename), 'utf8'));
        }
    }
});

test('Frida 17 module compatibility handles global, module and missing exports', () => {
    const context = {Module: {findGlobalExportByName: name => name === 'open' ? 42 : null},
        Process: {findModuleByName: name => name === 'lib' ? {findExportByName: () => 7} : null}};
    vm.runInNewContext(runtime, context);
    assert.equal(context.Module.findExportByName(null, 'open'), 42);
    assert.equal(context.Module.findExportByName('lib', 'symbol'), 7);
    assert.equal(context.Module.findExportByName('missing', 'symbol'), null);
    assert.throws(() => context.Module.getExportByName(null, 'missing'), /Missing export/);
});

test('iOS app snapshot emits bundle metadata and Mach-O modules', () => {
    const bundle = {bundleIdentifier: () => 'com.example.app', bundlePath: () => '/App.app',
        infoDictionary: () => ({objectForKey_: key => ({CFBundleName: 'App', CFBundleVersion: '42'})[key]})};
    const result = execute('ios/ios_app_agent.js', {
        ObjC: {available: true, classes: {NSBundle: {mainBundle: () => bundle}}},
        Process: {arch: 'arm64', enumerateModules: () => [
            {name: 'App', path: '/App.app/App', base: pointer(4096), size: 512},
        ]},
    });
    const data = lastData(result, 'ios_app.json');
    assert.equal(data.bundle_id, 'com.example.app');
    assert.equal(data.name, 'App');
    assert.equal(data.build, '42');
    assert.equal(data.modules[0].base, '4096');
});

test('NSURLSession request hook emits the shared HTTP artifact schema', () => {
    const selector = '- dataTaskWithRequest:completionHandler:';
    const result = execute('ios/ios_http_agent.js', {ObjC: {
        available: true, classes: {NSURLSession: {[selector]: {implementation: 'request'}}},
        Object: function(value) { return value; },
    }});
    result.hooks.get('request').onEnter([null, null, {
        URL: () => ({absoluteString: () => 'https://example.com/api'}), HTTPMethod: () => 'POST',
    }]);
    const data = lastData(result, 'http_traffic.json');
    assert.equal(data[0].url, 'https://example.com/api');
    assert.equal(data[0].method, 'POST');
});

test('CommonCrypto reads correct key argument positions for both signatures', () => {
    const result = execute('ios/ios_crypto_agent.js');
    result.observers[0].onAdded(moduleWith(['CCCrypt', 'CCCryptorCreateWithMode']));
    const regular = [pointer(0), pointer(0), pointer(0), pointer(123), pointer(16)];
    const withMode = [pointer(0), pointer(2), pointer(0), pointer(0), pointer(0), pointer(123), pointer(16)];
    result.hooks.get('CCCrypt').onEnter(regular);
    result.hooks.get('CCCryptorCreateWithMode').onEnter(withMode);
    const data = lastData(result, 'crypto_keys.json');
    assert.equal(data.length, 2);
    assert.equal(data[0].algorithm, 'AES');
    assert.equal(data[1].key_hex, '000102030405060708090a0b0c0d0e0f');
    regular[4] = pointer(513);
    result.hooks.get('CCCrypt').onEnter(regular);
    assert.equal(lastData(result, 'crypto_keys.json').length, 2);
});

test('native iOS SQLite records SQL without a Java runtime, including late modules', () => {
    const result = execute('storage/sqlite_agent.js');
    result.observers[0].onAdded(moduleWith(['sqlite3_exec']));
    result.hooks.get('sqlite3_exec').onEnter([pointer(4096), pointer('SELECT 1')]);
    const data = lastData(result, 'sqlite_log.json');
    assert.equal(data[0].sql, 'SELECT 1');
    assert.equal(data[0].db, '4096');
});

test('native iOS file monitoring uses global libc exports and container paths', () => {
    const result = execute('storage/fileio_agent.js', {
        Module: {findGlobalExportByName: name => ['open', 'write', 'unlink'].includes(name) ? name : null},
    });
    const open = result.hooks.get('open'), write = result.hooks.get('write');
    const state = {};
    open.onEnter.call(state, [pointer('/private/var/mobile/Containers/Data/Application/id/Documents/a')]);
    open.onLeave.call(state, pointer(7));
    const writeState = {};
    write.onEnter.call(writeState, [pointer(7), pointer(0), pointer(20)]);
    write.onLeave.call(writeState);
    const data = lastData(result, 'fileio_log.json');
    assert.equal(data[0].op, 'native_open');
    assert.equal(data[1].op, 'native_write');
    assert.equal(data[1].size, 20);
});

test('IL2CPP observes a late UnityFramework load on iOS without Java', () => {
    const result = execute('dump/il2cpp_agent.js');
    const mod = {...moduleWith(['il2cpp_domain_get']), name: 'UnityFramework', base: pointer(4096), size: 8};
    result.observers[0].onAdded(mod);
    assert.ok(result.messages.some(message => message.name === 'UnityFramework' && message.event === 'file'));
});
