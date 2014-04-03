$(document).ready(function() {
    Date.prototype.toHHMMSS = function () {
        var hours   = this.getHours();
        var minutes = this.getMinutes();
        var seconds = this.getSeconds();

        if (hours   < 10) {hours   = "0"+hours;}
        if (minutes < 10) {minutes = "0"+minutes;}
        if (seconds < 10) {seconds = "0"+seconds;}
        var time    = hours+':'+minutes+':'+seconds;
        return time;
    }

    /*
    setInterval(function() {
        var now = new Date();
        $("#clock").text(now.toHHMMSS());
    }, 1000);
    */

    var display_container = $("#display-content");
    var clock_container = $("#clock");
    var error_container = $("#error-message");
    error_container.hide();

    var current_display = "";

    function update_display() {
        var display_delay = 5; // seconds

        var url = document.location.href;
        if (url.substr(-1, 1) != '/') url += '/';
        url += 'content';
        $.ajax({
            url: url,
            data: {
                current_display: current_display
            },
            dataType: "json",
            timeout: 5000,
            success: function(data) {
                // received data is a dictionary with the following entries:
                // - display_name : the symbolic name of the returned display
                // - content (string) : the HTML code to be displayed in the content division
                // - delay (int) : the delay (in seconds) before requesting next display
                // - clock (string) : the server clock at display time
                current_display = data.display_name;
                display_delay = data.delay;

                clock_container.html(data.clock);
                display_container.html(data.content);
                error_container.hide();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                if (textStatus == "error") {
                    error_container.show();
                }
            },
            complete: function(jqXHR, textStatus) {
                setTimeout(update_display, display_delay * 1000);
            }
        });
    }
    update_display();
});