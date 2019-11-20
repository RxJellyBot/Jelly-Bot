$(function () {
    $('div[data-toggle="tooltip"]').tooltip();
    $('div.tooltip-hide[data-toggle="tooltip"]').tooltip('disable');
});

$(document).ready(function () {
    initEvents();
    initLayout();
});

function keyEventHandle() {
    $(window).keydown(function (event) {
        if (event.which === 13 && !$(document.activeElement).is("input#arTagKeyword, textarea")) {
            $("form#arForm").submit();
            return false;
        }
    });
}

function initLayout() {
    $("div#respGroup1").removeClass("d-none");
}

let responseCount = 1;
let regId = "arMember";

function initEvents() {
    initProperties();
    initResponsesSection();
    initTextAreas();
    initRegSelection();
    formSubmitHandle();
}

function regPanelSwitch() {
    $("div[data-btn-id]").addClass("d-none");
    $("div[data-btn-id=" + regId + "]").removeClass("d-none");
}

function initProperties() {
    $("div.btn-div").click(function () {
        if (!$(this).hasClass("disabled")) {
            let input_target = $("input#" + $(this).data("input"));

            input_target.val(reverseVal(input_target.val()));
            $(this).toggleClass("active");
        }
    });
    $("input#arCoolDownRange").on("input", function () {
        $("input#arCoolDown").val($(this).val());
    });
}

function initResponsesSection() {
    $("button.arRespBtnAdd").click(function () {
        responseCount++;

        $("div#respGroup" + responseCount).removeClass("d-none");

        if (responseCount >= $("b#respProp").data("max")) {
            $(this).prop("disabled", true);
        }
        $("button.arRespBtnDel").prop("disabled", false);
    });
    $("button.arRespBtnDel").click(function () {
        $("div#respGroup" + responseCount).addClass("d-none");

        responseCount--;

        if (responseCount <= 1) {
            $(this).prop("disabled", true);
        }
        $("button.arRespBtnAdd").prop("disabled", false);
    });
}

function initTextAreas() {
    $("div.txtarea-count").each(function () {
        let parent = $(this);
        let txtArea = $(this).find("textarea");
        let id = "[data-count=" + txtArea.attr("id") + "]";
        $(this).init(function () {
            $(this).find("span[data-type=current]" + id).text(0);
        }).on("input", function () {
            updateTextAreaPercentBar($(this), txtArea, id);

            // submitBtnDisable(percentage > 100);
        });

        txtArea.on("blur", function () {
            validateTextArea(parent, txtArea);
        });

        $(this).find("select.ar-type").change(function () {
            validateTextArea(parent, txtArea);
        })
    })
}

function updateTextAreaPercentBar(area_base, txtArea, id) {
    let currentCount = txtArea.val().length;
    let progBar = area_base.find("div[data-type=progress]" + id);

    let percentage = currentCount / parseFloat(progBar.attr("aria-valuemax")) * 100;

    area_base.find("span[data-type=current]" + id).text(currentCount);
    progBar.attr("aria-valuenow", currentCount).css("width", percentage + "%");

    if (percentage > 100) {
        progBar.addClass("bg-danger");
    } else {
        progBar.removeClass("bg-danger");
    }
}

function validateTextArea(parent, txtArea) {
    validateContent(parent.find("select.ar-type option:selected").val(), txtArea.val(), function (success, result) {
        hideAllValidClasses(txtArea);
        let valid = success && result;

        if (valid) {
            txtArea.addClass("is-valid");
        } else {
            txtArea.addClass("is-invalid");
        }
    })
}

function initRegSelection() {
    $("label.arRegister").change(function () {
        regId = $(this).attr("id");

        regPanelSwitch();
    });
    $("button#arChannelCheck").click(function () {
        validateChannelInfo();
    });
    $("select#arChannel").change(function () {
        onChannelMemberSelected($(this).children("option:selected"));
    });
}

function onChannelMemberSelected(option) {
    if (option.val() === "default") {
        $("span#channelName").text("-");
        $("span#channelPlatform").text("-");
        $("input#channelPlatCode").val("");
        $("code#channelToken").text("-");
        $("code#channelId").text("-");
        enablePinnedModuleAccess(false);
    } else {
        $("span#channelName").text(option.data("cname"));
        $("span#channelPlatform").text(option.data("cplat"));
        $("input#channelPlatCode").val(option.data("cplatcode"));
        $("code#channelToken").text(option.data("ctoken"));
        $("code#channelId").text(option.data("cid"));
        checkAccessPinnedPermission(option.data("cid"));
    }
}

function formSubmitHandle() {
    $(document).ready(function () {
        keyEventHandle();
        $("button.arSubmit").click(function () {
            $("form#arForm").submit();
        })
    });

    $("form#arForm").submit(function () {
        submitBtnDisable(true);
        updateLastSubmissionTime();

        let pass = true;

        if (formSubmissionChecks()) {
            pass = false;
        }

        if (!pass) {
            hideAllSubmitMsg();
            showInputFailed(true);
            submitBtnDisable(false);
        } else {
            if (regId === "arExecode" || regId === "arChannel" || regId === "arMember") {
                submitData(onSubmitCallback);
            } else {
                console.error(`The registration method ${regId} is not handled.`);
            }
        }

        // noinspection JSDeprecatedSymbols
        event.preventDefault(); // Cancel default submission behavior for Ajax
        return false;
    })
}

function validateChannelInfo() {
    let arPlatVal = $("select#arPlatform option:selected").val();
    let arChannelToken = $("input#arChannelToken").val();

    checkChannelMembershipAsync(arPlatVal, arChannelToken, function (exists) {
        let elem = $("input#arChannelToken");
        elem.removeClass("is-valid is-invalid");
        if (typeof exists !== "undefined" && exists) {
            elem.addClass("is-valid");
        } else {
            elem.addClass("is-invalid");
        }
    })
}

function hideAllValidClasses(elem) {
    elem.removeClass("is-invalid is-valid");
}

function onSubmitCallback(response) {
    hideAllSubmitMsg();
    console.log(response);

    if (response.success) {
        displayExecode(response);

        resetForm();
        showSubmissionSucceed(true);
    } else {
        showSubmissionFailed(true);
    }
    submitBtnDisable(false);
}

function onSubmissionFailed(error) {
    console.log(error);
    showSubmissionFailed(true);
    updateArCode(null);
    submitBtnDisable(false);
}

function resetForm() {
    // Clear all <textarea> and reset percent bar
    $("div.content-check:not(.d-none)").each(function () {
        let txtArea = $(this).find("textarea").first();
        txtArea.val("");
        updateTextAreaPercentBar(
            $(this).find("div.txtarea-count").first(),
            txtArea,
            "[data-count=" + $(this).attr("id") + "]");
    });

    // Hide All
    $("div.txtarea-count").each(function () {
        hideAllValidClasses($(this).find("textarea"));
        $(this).find("span[data-type=current]").text(0);
    });

    hideAllSubmitMsg();
}

function reverseVal(str) {
    if (str === "1") {
        return "0";
    } else if (str === "0") {
        return "1";
    } else {
        return str;
    }
}

function updateArCode(code) {
    let link = $("a#arCodeLink");
    link.attr("href", link.data("prefix") + code);

    if (code) {
        $("code#arCode").text(code);
    } else {
        $("code#arCode").text("-");
    }
}

function hideAllSubmitMsg() {
    $("div#inputFailed, div#submitFailed, div#submitSuccess").removeClass("d-inline").addClass("d-none");
}

function showSubmissionMessage(msgSel, show) {
    if (show) {
        updateLastSubmissionTime();
        $(msgSel).removeClass("d-none").addClass("d-inline");
    } else {
        $(msgSel).addClass("d-none").removeClass("d-inline");
    }
}

function showInputFailed(show) {
    showSubmissionMessage("div#inputFailed", show);
}

function showSubmissionSucceed(show) {
    showSubmissionMessage("div#submitSuccess", show);
}

function showSubmissionFailed(show) {
    showSubmissionMessage("div#submitFailed", show);
}

function updateLastSubmissionTime() {
    $("span#arSubmitTime").text(new Date().toString());
}

function enablePinnedModuleAccess(enable) {
    if (enable) {
        $("div[data-input='arPinned']").removeClass("disabled");
    } else {
        $("div[data-input='arPinned']").addClass("disabled").removeClass("active");
        $("input#arPinned").val("0");
    }
}

function submitBtnDisable(disable) {
    $("button.arSubmit").prop("disabled", disable);
    if (disable) {
        $("div#submitSpin").removeClass("d-none").addClass("d-inline");
    } else {
        $("div#submitSpin").addClass("d-none").removeClass("d-inline");
    }
}