$(document).ready(function () {
    $(".likepost").click(function (e) {
        e.preventDefault();
        let title = $(this).attr("article_title")
        let id = $(this).attr("article_id")
        let url = "/dashboard/article/" + id + "/" + title + "/"
        let data = "&likearticle=" + id

        $.post(url, data,
            function (data, ) {
                if (data == "200") {
                    $(".likearticle").removeClass("mdi mdi-heart-outline").addClass("mdi mdi-heart")
                    $(".likepost").removeClass("bg-light shadow border rounded-1").addClass("btn btn-danger")

                }
            },
            "html"
        );

    });
});