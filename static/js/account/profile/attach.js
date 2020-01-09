$(document).ready(function () {
    $("button.attach").click(onAttachClick);
});

function onAttachClick() {
    attachProfile($(this).data("poid"), $(this).data("cid"), function () {
        location.reload();
    });
}