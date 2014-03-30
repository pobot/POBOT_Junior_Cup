$(document).ready(function() {
    var feedback = $('#feedback');
    feedback.hide();

    $("#editor").validate({
        submitHandler: function(form) {
            var row_in_error = null;
            var error = null;

            feedback.hide();
            $("#validation_errors").html('');

            if (typeof check_row !== "undefined") {
                $("div.team-row").each(function(index) {
                    var row = $(this);
                    row.removeClass('has-error');
                    error = check_row(index + 1, row);
                    if (error !== null) {
                        row_in_error = row;
                        return false;
                    }
                });
            }

            if (row_in_error === null) {
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

            } else {
                row_in_error.addClass('has-error');
                $("#validation_errors").html(error);
            }

        },
        errorPlacement: function(error, element) {
            $("#validation_errors").html(error);
        }
    });

    $("#cancel").click(function(event){
        event.preventDefault();
        document.location.href = "/";
    });
});