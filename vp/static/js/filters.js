$(".tiles").hover(function() {
	$(this).addClass('hoverBg');
}, function() {
	$(this).removeClass('hoverBg');
});

$("input:checkbox").click(function() {
	var ischecked = $(this).is(':checked');
	if (!ischecked) {
		$("label[for='" + $(this).attr('id') + "']").removeClass('hoverBg');
	}
});

function mapDayValue(num) {
	if (num == 1)
		document.querySelector('#day_output').value = "Sat";
	else if (num == 2)
		document.querySelector('#day_output').value = "Sun";
	else if (num == 3)
		document.querySelector('#day_output').value = "Mon";
	else if (num == 4)
		document.querySelector('#day_output').value = "Tues";
	else if (num == 5)
		document.querySelector('#day_output').value = "Wed";
	else if (num == 6)
		document.querySelector('#day_output').value = "Thurs";
	else if (num == 7)
		document.querySelector('#day_output').value = "Fri";
}

$(function() {
	var HOURS_IN_DAY = 24, MINUTES_IN_HOUR = 60;
	var MIN_HOUR = 8, MAX_HOUR = 3 + HOURS_IN_DAY;

	var throttledFetchData = _.debounce(fetchData, 100);

	var initializeFilters = function() {
		var timeFilter = $('#time');
		timeFilter[0].step = MINUTES_IN_HOUR / 2;
		timeFilter[0].min = MIN_HOUR * MINUTES_IN_HOUR;
		timeFilter[0].max = MAX_HOUR * MINUTES_IN_HOUR;

		timeFilter.on('input', function(event){
			var totalMinutes = parseInt(timeFilter[0].value);
			var hours = totalMinutes / MINUTES_IN_HOUR;
			if(hours > 24) hours -= 24;
			var minutes = totalMinutes % MINUTES_IN_HOUR;
			var time = moment({hours: hours, minutes: minutes});

			$('#time_output').text(time.format("hh:mm A"))
			throttledFetchData(moment(time).format("HH:mm"));
		});
	}

	initializeFilters();
})
