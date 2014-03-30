$(document).ready(function() {
    var feedback = $('#feedback');

    feedback.hide();

    $("#tvsettings").validate({
        submitHandler: function(form) {
            /* check if the sequence is not empty */
            $("#sequence-error").html();
            var checked = 0;
            $(".sequence").each(function(index){
                if (this.checked) checked++;
            });
            if (checked == 0) {
                $("#sequence-error").html("La séquence doit contenir au moins une page.");
                return;
            }

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
                        .text("Erreur pendant l'enregistrement des modifications : " + errorThrown)
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