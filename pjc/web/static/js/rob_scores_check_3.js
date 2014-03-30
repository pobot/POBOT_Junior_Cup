function check_row(team_num, row) {
    var total_time = $("#total_time_" + team_num).val();
    var buoys_ok = parseInt($("#buoys_ok_" + team_num).val());
    var buoys_wrong = parseInt($("#buoys_wrong_" + team_num).val());

    if ((total_time == '00:00') &&
        (buoys_ok != 0 || buoys_wrong != 0)) {
       return "Temps total manquant"
    }

    var total_buoys = buoys_ok + buoys_wrong;
    if (total_buoys > 6) {
        return $.format("Erreur dans les décomptes de bouées ({0})", total_buoys);
    }

    return null;
}

