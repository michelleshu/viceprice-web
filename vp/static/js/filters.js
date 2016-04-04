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

function time_format(d) {
	hours = format_two_digits(d.getHours());
	minutes = format_two_digits(d.getMinutes());
	seconds = format_two_digits(d.getSeconds());
	return hours + ":" + minutes + ":" + seconds;
}

function setData() {
		 var d = new Date();
		 var formatted_time = time_format(d);
		 fetchData(formatted_time);
}
function format_two_digits(n) {
	return n < 10 ? '0' + n : n;
}
setData();

$(function() {
	var HOURS_IN_DAY = 24, MINUTES_IN_HOUR = 60;
	var MIN_HOUR = 8, MAX_HOUR = 3 + HOURS_IN_DAY;
	var initializeFilters = function() {
		var timeFilter = $('#time');
		timeFilter[0].step = MINUTES_IN_HOUR / 2;
		timeFilter[0].min = MIN_HOUR * MINUTES_IN_HOUR;
		timeFilter[0].max = MAX_HOUR * MINUTES_IN_HOUR;
		timeFilter.on('input', function(event){
			var totalMinutes = parseInt(timeFilter[0].value);
			var hours = totalMinutes / MINUTES_IN_HOUR;
			var minutes = totalMinutes % MINUTES_IN_HOUR;
			var time = new Date();
			time.setHours(hours, minutes);

			$('#time_output').text(moment(time).format("hh:mm A"))
			fetchData(moment(time).format("hh:mm"));
		});
	}

	initializeFilters();
})
