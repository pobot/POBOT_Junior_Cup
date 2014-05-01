$(document).ready(function() {
    var feedback = $('#feedback');

    feedback.hide();

    $("#system_settings").validate({
        submitHandler: function(form) {
            /* check if the sequence is not empty */
            $("#msg_date").html();
            $("#msg_time").html();

            $.ajax({
                url: document.location.href,
                type: 'POST',
                data: $(form).serialize(),
                success: function(data) {
                    feedback
                        .text("Modifications enregistrées.")
                        .addClass('alert-success')
                        .removeClass('alert-danger')
                        .show();
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    feedback
                        .text("Erreur pendant la mise à jour des paramètres : " + errorThrown)
                        .addClass('alert-danger')
                        .removeClass('alert-success')
                        .show();
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