$(document).ready(function () {

    const csftoken = Cookies.get('csrftoken');
    // const csftoken = document.querySelector('{name=csrfmiddlewaretoken}').value
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!(/^http:.*/.test(settings.url))) {
                xhr.setRequestHeader("X-CSRFToken", csftoken)
            }
        }
    })

    // ====================================================
    // Get wallet ballance 
    // +++++++++++++++++++++++++++++++++++++++++++++++++++++

    let load_balance_data = {
        'load_balance': 'load_balance'
    }
    $.get("/bot", load_balance_data,
        function (data, ) {
            $(".wallet_one").html("$ " + data.wallet_one)
            $(".wallet_two").html("$ " + data.wallet_two)
        },
        "json"
    );

    // ====================================================
    // Statbilized wallet balance for next bet 
    // +++++++++++++++++++++++++++++++++++++++++++++++++++++

    $(".stabilized").click(function (e) {
        e.preventDefault();
        $.ajax({
            type: "post",
            url: '/bot',
            data: {
                'stabilize_balance': 'balance'
            },
            dataType: "json",
            success: function (response) {
                alert(response.result)
            }
        });
    });





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

            $.post("/bot", data,
                function (data, ) {
                    $("#form").hide()
                    alert(data.result)
                    // $(".terminal").removeClass("d-none")
                    // $(".terminal").html(data)


                },
                "json"
            );
        });

        // 
    });



    // stop server


    $(".stopserver").click(function (e) {
        e.preventDefault();
        $(this).html("processing ..")
        let data = {
            'stop_thread': 'stop_thread'
        }
        $.post("/bot", data,
            function (data, ) {
                alert(data.result)
                location.reload()
            },
            "json"
        );
    });

    // ====================================================
    // check server statuc
    // +++++++++++++++++++++++++++++++++++++++++++++++++++++

    $(".checkserver").click(function (e) {
        e.preventDefault();
        $(this).html("checking ...")
        let data = {
            'thread_running': 'thread'
        }
        $.post("/bot", data,
            function (data, ) {
                if (data.result === "down") {
                    location.reload()
                } else {
                    $(".checkserver").html("check server status")
                    alert(data.result)
                }
            },
            "json"
        );
    });

    // ====================================================
    // show logs 
    // +++++++++++++++++++++++++++++++++++++++++++++++++++++


    $(".showdetails").click(function (e) {
        e.preventDefault();
        let data = {
            'fetch_logs': 'fetch_logs'
        }
        $(this).hide()
        $(".terminal2").removeClass("d-none")
        $('.clearint').removeClass("d-none")
        $(".spinwerlogs").hide()

        let x = setInterval(() => {
            $.get("/bot", data,
                function (data, ) {
                    if (data.result === "server_off") {
                        alert('Logs is empty')
                        clearInterval(x)
                        $(this).addClass(" d-none")
                        $(".terminal2").addClass(" d-none")
                        $(".showdetails").show()
                    } else {
                        $('.terminal2').scrollTop($('.terminal2')[0].scrollHeight);
                        $(".terminal2").append(data.result)

                        $(".clearint").click(function (e) {
                            e.preventDefault();
                            clearInterval(x)
                            $(this).addClass(" d-none")
                            $(".terminal2").addClass(" d-none")
                            $(".showdetails").show()
                        });

                    }


                },
                "json"
            );

        }, 5000);


    });
    // ====================================================
    // Clear logs 
    // +++++++++++++++++++++++++++++++++++++++++++++++++++++
    $(".clearLogs").click(function (e) {
        e.preventDefault();
        $(this).html("clearing logs...")
        let data = {
            "clear_logs": "clear_logs"
        }
        $.get("/bot", data,
            function (data, ) {
                $(".clearLogs").html("clear logs")
                alert(data.result)
            },
            "json"
        );
    });
});