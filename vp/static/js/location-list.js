$(document).ready(function() {
    var lastUpdatedFields = $('.last-updated');
    var thirtyDaysAgo = moment().subtract(30, 'days');
    for (var i = 0; i < lastUpdatedFields.length; i++) {
        if (moment($(lastUpdatedFields[i]).text(), 'MM/DD/YYYY').isBefore(thirtyDaysAgo)) {
            $(lastUpdatedFields[i]).css('background-color', '#e74c3c');
        };
    }
});