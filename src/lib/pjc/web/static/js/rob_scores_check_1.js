function check_row(team_num, row) {
    var total_time = $("#total_time_" + team_num).val();
    var alignments = $("#alignments_" + team_num).val();
    var dockings = $("#dockings_" + team_num).val();
    var hits = $("#hits_" + team_num).val();

    if ((total_time == '00:00') &&
        (alignments != 0 || dockings != 0 || hits != 0)) {
       return "Temps total manquant"
    }

    return null;
}

