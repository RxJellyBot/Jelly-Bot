$(document).ready(function () {
    $("input#color").keyup(onColorKeyup);
    onColorKeyup();
});

function onColorKeyup() {
    let inputElem = $("input#color");

    // Force first character to be #
    if (!inputElem.val().startsWith("#")) {
        inputElem.val("#" + inputElem.val());
    }

    // Apply color sample
    let validColor = inputElem.val().length === 7;
    if (validColor) {
        $("span#colorSample").show().css("background-color", inputElem.val());
    } else {
        $("span#colorSample").hide();
    }

    enableSubmit(validColor);
}

function enableSubmit(enable) {
    if (enable) {
        $("button#submit").attr("disabled", false);
    } else {
        $("button#submit").attr("disabled", true);
    }
}