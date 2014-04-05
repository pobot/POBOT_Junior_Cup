function check_row(team_num, row) {
    var total_time = $("#total_time_" + team_num).val();
    var alignments = parseInt($("#alignments_" + team_num).val());
    var dockings = parseInt($("#dockings_" + team_num).val());
    var hits = parseInt($("#hits_" + team_num).val());
    var channels_ok = parseInt($("#channels_ok_" + team_num).val());
    var channels_wrong = parseInt($("#channels_wrong_" + team_num).val());

    if ((total_time == '00:00') &&
        (alignments != 0 || dockings != 0 || hits != 0 || channels_ok != 0 || channels_wrong != 0)) {
       return "Temps total manquant"
    }

    var total_channels = channels_ok + channels_wrong;
    if (total_channels > 2) {
        return $.format("Erreur dans les décomptes de chenaux ({0})", total_channels);
    }

    return null;
}

