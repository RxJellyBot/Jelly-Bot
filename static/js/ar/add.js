$(function () {
    $('[data-toggle="tooltip"]').tooltip();
    $('.tooltip-hide[data-toggle="tooltip"]').tooltip('disable');
});

// Show tooltips on content type change

$(document).ready(function () {
    initEvents();
    initLayout();
});

function initLayout() {
    $("#respGroup1").removeClass("d-none");
}

let responseCount = 1;
let regId = "arToken";

function initEvents() {
    propertySetting();
    responsesManaging();
    initTextArea();
    initRegSelection();
    formSubmitHandle();
}

function regPanelSwitch() {
    $("[data-btn-id]").addClass("d-none");
    $("[data-btn-id=" + regId + "]").removeClass("d-none");
}

function regSubmitBtnControl() {
    if (regId === "arChannel") {
        checkChannelInfo();
    } else {
        $(".arSubmit").prop("disabled", false);
    }
}

function propertySetting() {
    $(".btn-div").click(function () {
        if (!$(this).hasClass("disabled")) {
            let input_target = $("#" + $(this).data("input"));

            input_target.val(reverseVal(input_target.val()));
            $(this).toggleClass("active");
        }
    });
    $("#arCoolDownRange").on("input", function () {
        $("#arCoolDown").val($(this).val());
    });
}

function responsesManaging() {
    $(".arRespBtnAdd").click(function () {
        responseCount++;

        $("#respGroup" + responseCount).removeClass("d-none");

        if (responseCount >= $("#respProp").data("max")) {
            $(this).prop("disabled", true);
        }
        $(".arRespBtnDel").prop("disabled", false);
    });
    $(".arRespBtnDel").click(function () {
        $("#respGroup" + responseCount).addClass("d-none");

        responseCount--;

        if (responseCount <= 1) {
            $(this).prop("disabled", true);
        }
        $(".arRespBtnAdd").prop("disabled", false);
    });
}

function initTextArea() {
    $(".txtarea-count").each(function () {
        let txtArea = $(this).find("textarea");
        let id = "[data-count=" + txtArea.attr("id") + "]";
        $(this).init(function () {
            $(this).find("[data-type=current]" + id).text(0);
        }).on("input", function () {
            let currentCount = txtArea.val().length;
            let progBar = $(this).find("[data-type=progress]" + id);

            let percentage = currentCount / parseFloat(progBar.attr("aria-valuemax")) * 100;

            $(this).find("[data-type=current]" + id).text(currentCount);
            progBar.attr("aria-valuenow", currentCount).css("width", percentage + "%");

            if (percentage > 100) {
                progBar.addClass("bg-danger");
            } else {
                progBar.removeClass("bg-danger");
            }
        })
    })
}

function initRegSelection() {
    $("label.arRegister").change(function () {
        regId = $(this).attr("id");

        regPanelSwitch();
        regSubmitBtnControl();
    });
    $("#arChannelCheck").click(function () {
        checkChannelInfo();
    })
}

function formSubmitHandle() {
    $(".ar").submit(function (event) {
        let pass = true;

        if (!validateForm()) {
            pass = false;
        }

        if (!pass) {
            hideAllSubmitMsg();
            $("#inputFailed").removeClass("d-none").addClass("d-inline");
        } else {
            if (regId === "arToken" || regId === "arChannel") {
                submitData(onSubmitCallback);
            } else {
                console.error(`The registration method ${regId} is not handled.`);
            }
            $(".arSubmit").prop("disabled", true);
        }
        event.preventDefault(); // Because of Ajax form submission
    })
}

function validateForm() {
    let ret = true;

    // Validate content lengths
    $(".content-check:not(.d-none)").each(function () {
        let txtArea = $(this).find("textarea");
        let ctLen = txtArea.val().length;
        let maxLen = parseFloat($(this).find("[data-type=progress][data-count=" + txtArea.attr("id") + "]").attr("aria-valuemax"));

        if (maxLen < ctLen || ctLen === 0) {
            let elem = $(this).find(".tooltip-hide[data-toggle=tooltip]");
            elem.tooltip('enable').tooltip('show').tooltip('disable');
            ret = false;
            $("#arCode").text("-");
        }
    });

    return ret;
}

function checkChannelInfo() {
    let arPlatVal = $("#arPlatform option:selected").val();
    let arChannelID = $("#arChannelID").val();

    checkChannelExistence(arPlatVal, arChannelID, function (outcomeCode) {
        let result = outcomeCode > 0;
        $(".arSubmit").prop("disabled", result);

        let elem = $("#arChannelID");
        elem.removeClass("is-valid is-invalid");
        if (typeof outcomeCode !== "undefined" && outcomeCode < 0) {
            elem.addClass("is-valid");
        } else {
            elem.addClass("is-invalid");
        }
    })
}

function hideAllSubmitMsg() {
    $("#inputFailed, #submitFailed, #submitSuccess").removeClass("d-inline").addClass("d-none");
}

function onSubmitCallback(response) {
    $(".arSubmit").prop("disabled", false);

    hideAllSubmitMsg();

    if (response.success) {
        $("#submitSuccess").removeClass("d-none").addClass("d-inline");
        displayToken(response);

        resetForm();
    } else {
        $("#submitFailed").removeClass("d-none").addClass("d-inline");
    }
    console.log(response);
}

function resetForm() {
    // CLEAR all <textarea>
    $(".content-check:not(.d-none)").find("textarea").each(function () {
        $(this).val("");
    });
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





