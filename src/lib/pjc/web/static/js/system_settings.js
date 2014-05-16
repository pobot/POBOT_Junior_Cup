$(document).ready(function() {
    $("button#synchronize").click(function(){
        var now = moment();
        $("input#date").val(now.format("DD/MM/YY"));
        $("input#time").val(now.format("HH:mm"));

        // in case of a previous error display
        $("#msg_date").html("");
        $("#msg_time").html("");
    });

    $("#system_settings").validate({
        submitHandler: function(form) {
            $("#msg_date").html("");
            $("#msg_time").html("");

            $.ajax({
                url: document.location.href,
                type: 'POST',
                data: $(form).serialize(),
                success: function(data) {
                    jSuccess("Modifications enregistrées.");
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    jError(
                        "Erreur pendant la mise à jour des paramètres : <br>" + errorThrown,
                        {
                            HideTimeEffect: 500
                        }
                    );
                }
            });
        },
        errorPlacement: function(error, element) {
            $("#msg_" + element.attr('id')).html(error);
        }
    });

    $("#cancel").click(function(event){
        event.preventDefault();
        document.location.href = "/";
    });

    $("#btn_clear_msg").click(function(event){
        event.preventDefault();
        $("#msg_text").val("");
    });


});