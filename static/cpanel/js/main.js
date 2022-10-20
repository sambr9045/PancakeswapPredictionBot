$(document).ready(function () {

    // ====================================================
    // start server
    // +++++++++++++++++++++++++++++++++++++++++++++++++++++

    $(".startarbitrage").click(function (e) {
        e.preventDefault();
        $(this).html("Starting ...")
        $(this).hide()
        $(".info").removeClass("d-none")

        $(".continuer").click(function (e) {
            e.preventDefault();
            let data = $("#form").serialize()
            $(this).html("starting prediciton bot ...")

            $.post("/start", data,
                function (data, ) {
                    $("#form").hide()
                    $(".terminal").removeClass("d-none")
                    $(".terminal").html(data)
                    value = $(".terminal").html()

                },
                "html"
            );
        });

        // 
    });

    // ====================================================
    // check server statuc
    // +++++++++++++++++++++++++++++++++++++++++++++++++++++

    $(".checkserver").click(function (e) {
        e.preventDefault();
        $(this).html("checking ...")
        let data = "&data=" + 's'
        $.post("/fetchlogs", data,
            function (data, ) {
                if (data === "down") {
                    location.reload()
                } else {
                    $(".checkserver").html("check server status")
                    alert(data)
                }
            },
            "html"
        );
    });

    // ====================================================
    // show logs 
    // +++++++++++++++++++++++++++++++++++++++++++++++++++++


    $(".showdetails").click(function (e) {
        e.preventDefault();
        let data = "&showlogs=" + "logging"
        $(this).hide()
        $(".terminal2").removeClass("d-none")

        setInterval(() => {
            $.post("/showlogs", data,
                function (data, ) {

                    $('.the3').scrollTop($('.the3')[0].scrollHeight);

                    $(".the3").empty().append(data)

                },
                "html"
            );

        }, 5000);

    });
    // ====================================================
    // Clear logs 
    // +++++++++++++++++++++++++++++++++++++++++++++++++++++
    $(".clearLogs").click(function (e) {
        e.preventDefault();
        $(this).html("clearing logs")
        let data = "&clearLogs=" + 'logs'
        $.post("/clearlogs", data,
            function (data, ) {
                $(".clearLogs").html("clear logs")
            },
            "html"
        );
    });
});