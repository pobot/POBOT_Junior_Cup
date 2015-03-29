/**
 * Created by eric on 6/15/14.
 */

$(document).ready(function() {
    "use strict";

    var PAGE_LENGTH = 10;
    var page_start = 1;
    var teams_count = $("div.team-row").length;

    function paginate() {
        $("div.team-row").hide();

        var i;
        for (i = page_start; i < page_start + PAGE_LENGTH ; i++) {
            $("div#team-row_" + i).show();
        }

        if (page_start > 1) {
            $("#page-up").removeClass("disabled");
        } else {
            $("#page-up").addClass("disabled");
        }
        if (page_start < teams_count - PAGE_LENGTH) {
            $("#page-down").removeClass("disabled");
        } else {
            $("#page-down").addClass("disabled");
        }
    }
    paginate();

    $("li#page-up a").click(function(){
        if (page_start > PAGE_LENGTH) {
            page_start -= PAGE_LENGTH;
        }
        paginate();
    });


    $("li#page-down a").click(function(){
        if (page_start < teams_count - PAGE_LENGTH) {
            page_start += PAGE_LENGTH;
        }
        paginate();
    });

   $("#registration").validate({
        submitHandler: function(form) {
            $.ajax({
                url: document.location.href,
                type: 'POST',
                data: $(form).serialize(),
                success: function(data) {
                    jSuccess("Modifications enregistrées.");
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    jError(
                        "Erreur pendant l'enregistrement des modifications : <br>" + textStatus,
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

});
