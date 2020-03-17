$(document).ready(function () {
    $("button.attach").click(onAttachClick);
});

function onAttachClick() {
    attachProfile(
        $(this).data("poid"),
        $(this).data("cid"),
        $("select#target option:selected").data("oid"));
}