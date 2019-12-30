$(document).ready(function () {
    $("button.star-btn").click(onStarBtnClick);
});

function onStarBtnClick() {
    $(this).toggleClass("active");

    changeStar($(this).data("cid"), $(this).hasClass("active"));
}