$(document).ready(function(){

  if(typeof jQuery!=='undefined'){
    console.log('jQuery Loaded');
  }
  else{
    console.log('not loaded yet');
  }


  var MondayBox = $('#Monday-box'),
  TuesdayBox = $('#Tuesday-box'),
  WednesdayBox = $('#Wednesday-box'),
  ThursdayBox = $('#Thursday-box'),
  FridayBox = $('#Friday-box'),
  SaturdayBox = $('#Saturday-box'),
  SundayBox = $('#Sunday-box');
  var delivery24hrBox = $('#delivery-24hr-box'),
  deliveryTime = $('#delivery-time');

  setAcceptingTimeInputVisibility('#Monday-box', '#Monday');
  setAcceptingTimeInputVisibility("#Tuesday-box", '#Tuesday');
  setAcceptingTimeInputVisibility("#Wednesday-box", '#Wednesday');
  setAcceptingTimeInputVisibility("#Thursday-box", '#Thursday');
  setAcceptingTimeInputVisibility("#Friday-box", '#Friday');
  setAcceptingTimeInputVisibility("#Saturday-box", '#Saturday');
  setAcceptingTimeInputVisibility("#Sunday-box", '#Sunday');
  setDeliveryTimeInputVisibility('#delivery-24hr-box','#delivery-time')

  MondayBox.on('click', function() {
    setAcceptingTimeInputVisibility('#Monday-box', '#Monday');
  });
  TuesdayBox.on('click', function() {
    setAcceptingTimeInputVisibility("#Tuesday-box", '#Tuesday');
  });
  WednesdayBox.on('click', function() {
    setAcceptingTimeInputVisibility("#Wednesday-box", '#Wednesday');
  });
  ThursdayBox.on('click', function() {
    setAcceptingTimeInputVisibility("#Thursday-box", '#Thursday');
  });
  FridayBox.on('click', function() {
    setAcceptingTimeInputVisibility("#Friday-box", '#Friday');
  });
  SaturdayBox.on('click', function() {
    setAcceptingTimeInputVisibility("#Saturday-box", '#Saturday');
  });
  SundayBox.on('click', function() {
    setAcceptingTimeInputVisibility("#Sunday-box", '#Sunday')
  });
  delivery24hrBox.on('click', function() {
    setDeliveryTimeInputVisibility('#delivery-24hr-box','#delivery-time')
  });

});

function setAcceptingTimeInputVisibility(checkbox, timeInput) {
  if($(checkbox).is(':checked')) {
    $(timeInput).removeClass('d-none');
    $(timeInput + ' :input').attr("disabled", false);
  } else {
    $(timeInput).addClass('d-none');
    $(timeInput + ' :input').attr("disabled", true);
  }
}

function setDeliveryTimeInputVisibility(checkbox, timeInput) {
  if(!$(checkbox).is(':checked')) {
    $(timeInput).removeClass('d-none');
    $(timeInput + ' :input').attr("disabled", false);
  } else {
    $(timeInput).addClass('d-none');
    $(timeInput + ' :input').attr("disabled", true);
  }
}
