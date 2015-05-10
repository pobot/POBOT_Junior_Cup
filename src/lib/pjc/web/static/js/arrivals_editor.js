/**
 * Created by eric on 6/15/14.
 */

$(document).ready(function () {
    "use strict";

    $("#registration").validate({
        submitHandler: function (form) {
            $.ajax({
                url: document.location.href,
                type: 'POST',
                data: $(form).serialize(),
                success: function (data) {
                    jSuccess("Modifications enregistrées.");
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    jError(
                        "Erreur pendant l'enregistrement des modifications : <br>" + textStatus,
                        {
                            HideTimeEffect: 500
                        }
                    );
                }
            });
        },
        errorPlacement: function (error, element) {
            $("#msg_" + element.attr('id')).html(error);
        }
    });

    $("#cancel").click(function (event) {
        event.preventDefault();
        document.location.href = "/";
    });

});
