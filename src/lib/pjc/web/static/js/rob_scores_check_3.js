function check_row(team_num, row) {
    "use strict";

    var total_time = $("#total_time_" + team_num).val();
    var moved = parseInt($("#moved_" + team_num).val(), 10);

    if ((total_time === '0:00') && (moved !== 0)) {
       return "Temps total manquant";
    }

    return null;
}

