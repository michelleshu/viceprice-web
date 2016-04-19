//Must match DAYS_OF_WEEK in constants.py; todo: unify constants.py DAYS_OF_WEEK and enter-happy-hour.js getDaysOfWeek
var DAYS_OF_WEEK = [
	null, //1-based indexing
	'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
]

var HOURS_IN_DAY = 24, MINUTES_IN_HOUR = 60;
var MIN_HOUR = 8, MAX_HOUR = 3 + HOURS_IN_DAY;

$(function() {
	var selectedTime = moment();
	var selectedDay = _.indexOf(DAYS_OF_WEEK, selectedTime.format("dddd")); //momentjs day of week indexes do not match ours; map to our index
	var throttledFetchData = _.debounce(function() {
		if(selectedTime.format("HH") == moment().format("HH") && selectedDay == _.indexOf(DAYS_OF_WEEK, selectedTime.format("dddd")))
			$('.now').text("( Now )");
		else
			$('.now').text(" ");
		fetchData(selectedTime.format("HH:mm"), selectedDay);
	}, 100);

	var initializeTimeFilter = function() {
		var timeFilter = $('#time');
		timeFilter.attr('step', MINUTES_IN_HOUR / 2);
		timeFilter.attr('min', MIN_HOUR * MINUTES_IN_HOUR);
		timeFilter.attr('max', MAX_HOUR * MINUTES_IN_HOUR);

		var now = selectedTime;
		var nowTotalMinutes = now.hours() * MINUTES_IN_HOUR + now.minutes();
		if(nowTotalMinutes < timeFilter.attr('min')) nowTotalMinutes += HOURS_IN_DAY * MINUTES_IN_HOUR;
		timeFilter.val(nowTotalMinutes);

		timeFilter.on('input', function(event){
			var totalMinutes = timeFilter.val();
			var hours = totalMinutes / MINUTES_IN_HOUR;
			if(hours > 24) hours -= 24;
			var minutes = totalMinutes % MINUTES_IN_HOUR;
			selectedTime = moment({hours: hours, minutes: minutes});

			$('#time_output').text(selectedTime.format("hh:mm A"))
			throttledFetchData();
		});
		timeFilter.trigger('input');
	};

	var initializeDayFilter = function() {
		var dayFilter = $('#day');
		dayFilter.val(selectedDay);

		dayFilter.on('input', function(event) {
			selectedDay = dayFilter.val();

			$('#day_output').val(DAYS_OF_WEEK[selectedDay]);
			throttledFetchData();
		});
		dayFilter.trigger('input');
	};

	initializeDayFilter();
	initializeTimeFilter();
	
})
