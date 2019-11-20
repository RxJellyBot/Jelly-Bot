$(document).ready(function () {
    $("button#execodeSubmit").click(onSubmitClick);
});

function onSubmitClick() {
    let execode = $("input#execode").val();
    if (execode === undefined || execode.length === 0) {
        updateSubmitMessage("submitMsgNoExecode");
        return;
    }

    $("button#execodeSubmit").prop("disabled", true);
    sendExecodeAjax(execode, function(data) {
        console.log(data);
        updateSubmitMessage("submitMsgFailed");
    }, function() {
        $("input#execode").val("");
        updateSubmitMessage("submitMsgOK");
    }, function () {
        $("button#execodeSubmit").prop("disabled", false);
    });
}

function updateSubmitMessage(showId) {
    $("div.submit-msg").addClass("d-none");
    $(`div#${showId}`).removeClass("d-none");
}