$(document).ready(function () {
    $("button#tokenSubmit").click(onSubmitClick);
});

function onSubmitClick() {
    let token = $("input#token").val();
    if (token === undefined || token.length === 0) {
        updateSubmitMessage("submitMsgNoToken");
        return;
    }

    $("button#tokenSubmit").prop("disabled", true);
    sendTokenAjax(token, function(data) {
        console.log(data);
        updateSubmitMessage("submitMsgFailed");
    }, function() {
        $("input#token").val("");
        updateSubmitMessage("submitMsgOK");
    }, function () {
        $("button#tokenSubmit").prop("disabled", false);
    });
}

function updateSubmitMessage(showId) {
    $("div.submit-msg").addClass("d-none");
    $(`div#${showId}`).removeClass("d-none");
}