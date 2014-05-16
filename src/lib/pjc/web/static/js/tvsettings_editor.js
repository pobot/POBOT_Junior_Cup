$(document).ready(function() {
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
                    jSuccess('Modifications enregistrées');
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    jError(
                        "Erreur pendant l'enregistrement des modifications : <br>" + errorThrown,
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