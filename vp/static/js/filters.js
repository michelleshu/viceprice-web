$(".tiles").hover(function() {
    $(this).addClass('hoverBg');
  }, function() {
    $(this).removeClass('hoverBg');
  }
);

$("input:checkbox").click(function() {
  var ischecked= $(this).is(':checked');
  if(!ischecked) {
    $("label[for='"+$(this).attr('id')+"']").removeClass('hoverBg');
  }
});

function outputUpdate(num) {
  if(num==1)
    document.querySelector('#day_output').value = "Sat";
  else if (num==2)
    document.querySelector('#day_output').value= "Sun";
  else if (num==3)
    document.querySelector('#day_output').value= "Mon";
  else if (num==4)
    document.querySelector('#day_output').value= "Tues";
  else if (num==5)
    document.querySelector('#day_output').value= "Wed";
  else if (num==6)
    document.querySelector('#day_output').value= "Thurs";
  else if(num==7)
    document.querySelector('#day_output').value= "Fri";
  else if (num==8)
    document.querySelector('#time_output').value= "8:00 AM";
  else if (num==9)
    document.querySelector('#time_output').value= "8:30 AM";
  else if (num==10)
    document.querySelector('#time_output').value= "9:00 AM";
  else if (num==11)
    document.querySelector('#time_output').value= "9:30 AM";
  else if (num==12)
    document.querySelector('#time_output').value= "10:00 AM";
  else if(num==13)
    document.querySelector('#time_output').value= "10:30 AM";
  else if(num==14)
    document.querySelector('#time_output').value= "11:00 AM";
  else if (num==15)
    document.querySelector('#time_output').value= "11:30 AM";
  else if (num==16)
    document.querySelector('#time_output').value= "12:00 PM";
  else if (num==17)
    document.querySelector('#time_output').value= "12:30 PM";
  else if (num==18)
    document.querySelector('#time_output').value= "1:00 PM";
  else if (num==19)
    document.querySelector('#time_output').value= "1:30 PM";
  else if(num==20)
    document.querySelector('#time_output').value= "2:00 PM";
  else if(num==21)
    document.querySelector('#time_output').value= "2:30 PM";
  else if (num==22)
    document.querySelector('#time_output').value= "3:00 PM";
  else if (num==23)
    document.querySelector('#time_output').value= "3:30 PM";
  else if (num==24)
    document.querySelector('#time_output').value= "4:00 PM";
  else if (num==25)
    document.querySelector('#time_output').value= "4:30 PM";
  else if (num==26)
    document.querySelector('#time_output').value= "5:00 PM";
  else if(num==27)
    document.querySelector('#time_output').value= "5:30 PM";
  else if (num==28)
    document.querySelector('#time_output').value= "6:00 PM";
  else if (num==29)
    document.querySelector('#time_output').value= "6:30 PM";
  else if(num==30)
    document.querySelector('#time_output').value= "7:00 PM";
  else if (num==31)
    document.querySelector('#time_output').value= "7:30 PM";
  else if(num==32)
    document.querySelector('#time_output').value= "8:00 PM";
  else if (num==33)
    document.querySelector('#time_output').value= "8:30 PM";
  else if (num==34)
    document.querySelector('#time_output').value= "9:00 PM";
  else if(num==35)
    document.querySelector('#time_output').value= "9:30 PM";
  else if(num==36)
    document.querySelector('#time_output').value= "10:00 PM";
  else if (num==37)
    document.querySelector('#time_output').value= "10:30 PM";
  else if (num==38)
    document.querySelector('#time_output').value= "11:00 PM";
}
