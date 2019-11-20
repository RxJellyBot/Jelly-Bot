$(document).ready(function() {
    $("button#loginGoogle").click(function () {
        googleSignIn();
    });
});

// noinspection JSUnusedGlobalSymbols
function onSignInHandle(idToken, defaultRedirectUrl) {
    let xhr = new XMLHttpRequest();
    xhr.open('POST', window.location.href);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.setRequestHeader('X-CSRFToken', $("input[name=csrfmiddlewaretoken]").val());
    xhr.onload = function () {
        if (xhr.responseText === "PASS") {
            window.location.replace(getRedirectUrl(defaultRedirectUrl));
        } else {
            generateAlert("danger", xhr.responseText);
        }
    };
    // noinspection JSUnresolvedFunction, JSUnresolvedVariable
    xhr.send('idtoken=' + idToken);
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