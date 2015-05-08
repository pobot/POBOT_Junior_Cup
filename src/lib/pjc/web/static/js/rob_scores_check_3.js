function check_row(team_num, row) {
    "use strict";

    var total_time = $("#total_time_" + team_num).val();
    var passengers = parseInt($("#buoys_ok_" + team_num).val(), 10);

    if ((total_time === '00:00') && (passengers !== 0)) {
       return "Temps total manquant";
    }

    return null;
}

