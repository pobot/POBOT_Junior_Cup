$(document).ready(function() {
    var feedback = $('#feedback');

    feedback.hide();

    $("#planning").validate({
        submitHandler: function(form) {
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
                        .text("Erreur pendant l'enregistrement des modifications : " + textStatus)
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


});