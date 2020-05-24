$(document).ready(() => {
    $("input#color").keyup(onColorKeyup);
    $("input#name").keyup(onNameKeyup);
    onColorKeyup();
});

function onColorKeyup() {
    const inputElem = $("input#color");

    // Force first character to be #
    if (!inputElem.val().startsWith("#")) {
        inputElem.val(`#${inputElem.val()}`);
    }

    // Apply color sample
    const validColor = inputElem.val().length === 7;
    if (validColor) {
        $("span#colorSample").show().css("background-color", inputElem.val());
    } else {
        $("span#colorSample").hide();
    }

    enableSubmit(validColor);
}

function onNameKeyup() {
    checkNameValidity($("input#channelOid").val(), $(this).val(), pass => {
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