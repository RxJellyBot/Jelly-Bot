// noinspection JSUnusedGlobalSymbols
function onSignInHandle(googleUser, defaultRedirectUrl) {
    let xhr = new XMLHttpRequest();
    xhr.open('POST', window.location.href);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.setRequestHeader('X-CSRFToken', $("[name=csrfmiddlewaretoken]").val());
    xhr.onload = function () {
        if (xhr.responseText === "PASS") {
            window.location.replace(getRedirectUrl(defaultRedirectUrl));
        } else {
            $("#msg").removeClass("d-none").text(" " + xhr.responseText);
        }
    };
    // noinspection JSUnresolvedFunction, JSUnresolvedVariable
    xhr.send('idtoken=' + googleUser.getAuthResponse().id_token);
}

function getRedirectUrl(defaultUrl) {
    let url = getUrlParam("next", "");
    if (url === "") {
        url = defaultUrl;
    }
    return url
}

function getUrlVars() {
    let vars = {};
    window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
        vars[key] = value;
    });
    return vars;
}

function getUrlParam(parameter, defaultVal) {
    let urlParameter = defaultVal;
    if (window.location.href.indexOf(parameter) > -1) {
        urlParameter = getUrlVars()[parameter];
    }
    return urlParameter;
}