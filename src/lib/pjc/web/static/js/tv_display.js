$(document).ready(function() {
    var display_container = $("#display-content");
    var clock_container = $("#clock");
    var error_container = $("#error-message");
    error_container.hide();

    var current_display = "";
    var current_page = 0;

    function update_display() {
        var display_delay = 5; // seconds

        var url = document.location.href;
        if (url.substr(-1, 1) != '/') url += '/';
        url += 'content';
        $.ajax({
            url: url,
            data: {
                current_display: current_display,
                current_page: current_page
            },
            dataType: "json",
            timeout: 5000,
            success: function(data) {
                // received data is a dictionary with the following entries:
                // - display_name : the symbolic name of the returned display
                // - current_page : the number of the current page (>= 1) for paginated displays
                // - content (string) : the HTML code to be displayed in the content division
                // - delay (int) : the delay (in seconds) before requesting next display
                // - clock (string) : the server clock at display time
                current_display = data.display_name;
                current_page = data.current_page;
                display_delay = data.delay;

                clock_container.html(data.clock);
                display_container.html(data.content);
                error_container.hide();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                if (textStatus == "error") {
                    error_container.show();
                    // reset the sequence for restarting cleanly when communication will be back
                    current_display = "";
                    current_page = 0;
                }
            },
            complete: function(jqXHR, textStatus) {
                setTimeout(update_display, display_delay * 1000);
            }
        });
    }
    update_display();
});