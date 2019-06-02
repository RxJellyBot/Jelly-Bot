$(function () {
    $('[data-toggle="tooltip"]').tooltip();
    $('.tooltip-hide[data-toggle="tooltip"]').tooltip('disable');
});

// Show tooltips on content type change

$(document).ready(function () {
    initEvents();
    initLayout();
}).keypress(function (event) {
    let keycode = (event.keyCode ? event.keyCode : event.which);
    if (keycode == '13') {
        $(".ar").submit();
    }
});

let responseCount = 1;

function initEvents() {
    formSubmitHandle();
    propertySetting();
    responsesManaging();
    initTextArea();
    initRegSelection();
    submitHandle();
}

function initLayout() {
    $("#respGroup1").removeClass("d-none");
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
        let id = $(this).attr("id");

        $("[data-btn-id]").addClass("d-none");
        $("[data-btn-id=" + id + "]").removeClass("d-none");
    });
}

function submitHandle() {
    $(".arSubmit").click(function () {
        $(".ar").submit();
    })
}

function formSubmitHandle() {
    $(".ar").submit(function (event) {
        if (!validateForm()) {
            event.preventDefault();
        }

        // FIXME: Get submit method
    })
}

function validateForm() {
    let ret = true;

    // Validate content lengths
    $(".txtarea-count:not(.d-none)").each(function () {
        let txtArea = $(this).find("textarea");
        let ctLen = txtArea.val().length;
        let maxLen = parseFloat($(this).find("[data-type=progress][data-count=" + txtArea.attr("id") + "]").attr("aria-valuemax"));

        if (maxLen < ctLen) {
            let elem = $(this).find(".tooltip-hide[data-toggle=tooltip]");
            elem.tooltip('enable').tooltip('show').tooltip('disable');
            ret = false;
        }
    });

    // Validate Channel
    // TODO: Add form - Validate Channel (js)

    let xhr = new XMLHttpRequest();


    // FIXME: Validate Form - All Valid will returns True
    //


    return false;
    // TEMP: return ret;
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





