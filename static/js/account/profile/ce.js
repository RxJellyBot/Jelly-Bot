$(document).ready(function () {
    $("input#color").keyup(onColorKeyup);
    $("input#name").keyup(onNameKeyup);
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

function onNameKeyup() {
    checkNameValidity($("input#channelOid").val(), $(this).val(), function(pass) {
        enableSubmit(pass);

        $("input#name").removeClass("is-valid is-invalid").addClass(pass ? "is-valid" : "is-invalid");
    });
}

function enableSubmit(enable) {
    if (enable) {
        $("button#submit").attr("disabled", false);
    } else {
        $("button#submit").attr("disabled", true);
    }
}