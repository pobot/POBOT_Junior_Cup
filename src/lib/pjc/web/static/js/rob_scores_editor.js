$(document).ready(function() {
    $("#editor").validate({
        submitHandler: function(form) {
            var row_in_error = null;
            var error = null;

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
                        jSuccess("Modifications enregistrées.");
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

    var scroller = $('div.score-editor-scroller');

    function resize_scroller() {
        var window_height = $(window).height();
        scroller.height(window_height - 320);
    }

    $(window).resize(resize_scroller);
    resize_scroller();
});