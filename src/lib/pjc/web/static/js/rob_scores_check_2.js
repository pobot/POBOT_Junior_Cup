function check_row(team_num, row) {
    var total_time = $("#total_time_" + team_num).val();
    var installed = parseInt($("#installed_" + team_num).val(), 10);
    var empty_areas = parseInt($("#empty_areas_" + team_num).val(), 10);
    var homogeneous_areas = parseInt($("#homogeneous_areas_" + team_num).val(), 10);

    if ((total_time === '0:00') &&
        (installed !== 0 || empty_areas !== 0 || homogeneous_areas !== 0)) {
       return "Temps total manquant";
    }

    if (total_time !== '0:00') {
        if (empty_areas + homogeneous_areas > 4) {
            return "Décomptes des zones non cohérents";
        }

        if (empty_areas + installed < 4) {
            return "Décompte des zones vides non cohérent";
        }

        if (homogeneous_areas > 0) {
            if (installed < homogeneous_areas + 4 - empty_areas) {
                return "Décompte des zones homogènes et vides non cohérent";
            }
        }
    }

    return null;
}

