$(document).ready(function () {
    $("button.star-btn").click(onStarBtnClick);
    $("a.detach-profile").click(onDetachClick);
});

function onStarBtnClick() {
    $(this).toggleClass("active");

    changeStar($(this).data("cid"), $(this).hasClass("active"));
}

function onDetachClick() {
    if (confirm(detachConfirmMesage($(this).data("pname")))) {
        detachProfile($(this).data("poid"));
    }
}