// from https://stackoverflow.com/a/48969580

// noinspection JSUnusedGlobalSymbols
function xhrPostRequest(url, params, onLoad = null, preSend = null) {
    let xhr = new XMLHttpRequest();

    xhr.open("POST", url);

    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    if (preSend) {
        preSend(xhr);
    }

    xhr.responseType = "json";

    xhr.onload = function () {
        if (onLoad) {
            onLoad(xhr);
        }
    };

    xhr.send(params);
}