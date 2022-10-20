$(document).ready(function () {
    $(".second_perido").addClass("periode_activate")

    total_price = $(".periode").find(".periode_activate").attr("total_price")
    periode_val = $(".periode").find("h3").attr("periode_val")
    plan = $(".periode").find("h3").attr("plan")
    update(total_price, periode_val, plan)

    $(".periode").click(function (e) {
        e.preventDefault();
        $(".periode").find(".card").removeClass("periode_activate")
        $(this).find(".card").addClass("periode_activate")

        total_price = $(this).find("h4").attr("total_price")
        periode_val = $(this).find("h3").attr("periode_val")
        plan = $(this).find("h3").attr("plan")

        update(total_price, periode_val, plan)

    });

    function update(total_price, periode_val, plan) {
        $(".total, .subtotal").html("$ " + total_price)
        $("#periode_total").val(total_price)
        $("#periode").val(periode_val)
        $("#plan").val(plan)
    }

});