$(document).ready(() => $("button#loginGoogle").click(() => googleSignIn()));

// noinspection JSUnusedGlobalSymbols
function onSignInHandle(idToken, defaultRedirectUrl) {
    xhrPostRequest(window.location.href, `idtoken=${idToken}`, xhr => {
        const response = xhr.response["text"];
        if (response === "PASS") {
            window.location.replace(getRedirectUrl(defaultRedirectUrl));
        } else {
            generateAlert("danger", response);
        }
    }, xhr => xhr.setRequestHeader('X-CSRFToken', $("input[name=csrfmiddlewaretoken]").val()));
}

function getRedirectUrl(defaultUrl) {
    let url = getUrlParam("next", "");
    if (url === "") {
        url = defaultUrl;
    }
    return decodeURIComponent(url)
}

function getUrlVars() {
    const vars = {};
    window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, (m, key, value) => {
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