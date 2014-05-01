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
    function update_clock() {
        $("#clock").text(new Date().toHHMMSS());
    }
    update_clock();
    setInterval(update_clock, 1000);

    $.extend($.validator.messages, {
        required: "Ce champ est obligatoire",
        digits: "Entrez une valeur entière positive ou nulle",
        min: "Entrez une valeur supérieure ou égale à {0}",
        max: "Entrez une valeur inférieure ou égale à {0}"
    });

    $.validator.addMethod("HHMM",
        function(value, element) {
            return /^([0-1][0-9]|2[0-3]):([0-5][0-9])?$/.test(value);
        },
        "Heure invalide (format attendu: HH:MM)"
    );

    $.validator.addMethod("DDMMYY",
        function(value, element) {
            return moment(value, "DD/MM/YY").isValid();
        },
        "Date invalide (format attendu: JJ/MM/AA)"
    );

    $.validator.addMethod("match-duration",
        function(value, element) {
            return /^[0-2]:[0-5][0-9]$/.test(value) ;
        },
        "Entrez une durée comprise entre 0:00 et 2:30"
    );

    $.validator.setDefaults({
        highlight: function(element) {
            $(element).closest('.form-group').addClass('has-error');
        },
        unhighlight: function(element) {
            $(element).closest('.form-group').removeClass('has-error');
        },
        errorElement: 'span'
    });


});