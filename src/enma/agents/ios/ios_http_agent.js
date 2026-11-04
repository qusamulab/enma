"use strict";
// Observe NSURLSession request creation, without changing responses or delegates.
const requests = [];
const hooked = new Set();
function flush() {
    if (requests.length) send({ event: "json", name: "http_traffic.json", data: requests });
}
function record(request) {
    if (requests.length >= 3000) return;
    try {
        const object = new ObjC.Object(request);
        const url = object.URL().absoluteString().toString();
        requests.push({ ts: Date.now(), url, method: object.HTTPMethod()?.toString() || "GET" });
    } catch (_) {}
}
if (ObjC.available) {
    const session = ObjC.classes.NSURLSession;
    if (session) {
        for (const selector of [
            "- dataTaskWithRequest:completionHandler:", "- dataTaskWithRequest:",
            "- downloadTaskWithRequest:completionHandler:", "- downloadTaskWithRequest:",
            "- uploadTaskWithRequest:fromData:completionHandler:",
        ]) {
            const method = session[selector];
            if (!method || hooked.has(method.implementation.toString())) continue;
            hooked.add(method.implementation.toString());
            Interceptor.attach(method.implementation, { onEnter(args) { record(args[2]); } });
        }
        // Convenience APIs receive NSURL rather than NSURLRequest.
        for (const selector of ["- dataTaskWithURL:", "- dataTaskWithURL:completionHandler:",
                                "- downloadTaskWithURL:", "- downloadTaskWithURL:completionHandler:"]) {
            const method = session[selector];
            if (!method || hooked.has(method.implementation.toString())) continue;
            hooked.add(method.implementation.toString());
            Interceptor.attach(method.implementation, {
                onEnter(args) {
                    if (requests.length >= 3000) return;
                    try {
                        requests.push({ ts: Date.now(), method: "GET",
                            url: new ObjC.Object(args[2]).absoluteString().toString() });
                    } catch (_) {}
                },
            });
        }
    }
}
setInterval(flush, 10000);

