$(document).ready(function() {
    var display_container = $("#display-content");
    var clock_container = $("#clock");
    var error_container = $("#error-message");
    error_container.hide();

    var current_display = "";
    var current_page = 0;

    /*
        This function is invoked periodically by auto-rescheduling itself using a timer (see
        end of body).

        It gets the content to be displayed by sending an Ajax request to the server, which replies
        with the HTML code to be put in the content container. Additional data are packaged with the
        returned structure for managing the display sequencing (see success callback of the Ajax call
        for details).
     */
    function update_display() {
        var display_delay = 5; // seconds

        var url = document.location.href;
        if (url.substr(-1, 1) !== '/') { url += '/'; }
        url += 'content';
        $.ajax({
            url: url,
            data: {
                // the Ajax requests uses the current page and display name to determine what
                // must be displayed next time.
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
                if (textStatus === "error") {
                    error_container.show();
                    // reset the sequence for restarting cleanly when the communication will be back
                    current_display = "";
                    current_page = 0;
                }
            },
            complete: function(jqXHR, textStatus) {
                // reschedule ourselves at the end of the display delay
                setTimeout(update_display, display_delay * 1000);
            }
        });
    }

    // bootstraps the first display
    update_display();
});