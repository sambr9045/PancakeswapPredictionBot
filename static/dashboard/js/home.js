$(document).ready(function () {
    $('.alert').alert()

    $(".readLater").click(function (e) {
        e.preventDefault()
        let article_id = $(this).attr("article_id")
        let data = "&article_id=" + article_id

        $.post("/dashboard/read-later", data,
            function (data, ) {

                if (data === "200") {

                    $(".saved_article_alert").removeClass("alert-danger").addClass("show alert-success")
                    $(".alert-Text").html(' Article saved successfully')

                } else if (data === "500") {
                    $(".saved_article_alert").removeClass("alert-success").addClass("show alert-danger")
                    $(".alert-Text").html('This article is already saved')

                } else {
                    $(".saved_article_alert").removeClass("alert-success").addClass("show alert-danger")
                    $(".alert-Text").html('Invalide article id . Please try again later')
                }

                setTimeout(() => {
                    $('.saved_article_alert').removeClass("show")
                }, 3000);
            },
            "html"

        );
    })
});