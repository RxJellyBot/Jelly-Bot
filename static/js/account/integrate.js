const submitBtnElem = $("button#execodeSubmit");

$(document).ready(() => submitBtnElem.click(onSubmitClick));

function onSubmitClick() {
    const execode = $("input#execode").val();
    if (execode === undefined || execode.length === 0) {
        updateSubmitMessage("submitMsgNoExecode");
        return;
    }

    submitBtnElem.prop("disabled", true);
    sendExecodeAjax(execode, data => {
        console.log(data);
        updateSubmitMessage("submitMsgFailed");
    }, () => {
        $("input#execode").val("");
        updateSubmitMessage("submitMsgOK");
    }, () => submitBtnElem.prop("disabled", false));
}

function updateSubmitMessage(showId) {
    $("div.submit-msg").addClass("d-none");
    $(`div#${showId}`).removeClass("d-none");
}