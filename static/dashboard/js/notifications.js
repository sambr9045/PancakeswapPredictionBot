$(document).ready(function () {
    $(".bellicone").click(function (e) {
        e.preventDefault();
        data = "&notification=" + "true"
        $.post("/dashboard/notification", data,
            function (data, ) {

            },
            "html"
        );
    });
});