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
  var accepting24hrBox = $('#accepting-24hr-box'),
  acceptingTime = $('#accepting-time');

  // setDeliveryTimeInputVisibility('#Monday-box', '#Monday');
  // setDeliveryTimeInputVisibility("#Tuesday-box", '#Tuesday');
  // setDeliveryTimeInputVisibility("#Wednesday-box", '#Wednesday');
  // setDeliveryTimeInputVisibility("#Thursday-box", '#Thursday');
  // setDeliveryTimeInputVisibility("#Friday-box", '#Friday');
  // setDeliveryTimeInputVisibility("#Saturday-box", '#Saturday');
  // setDeliveryTimeInputVisibility("#Sunday-box", '#Sunday');
  setAcceptingTimeInputVisibility('#accepting-24hr-box','#accepting-time')
  //
  // MondayBox.on('click', function() {
  //   setDeliveryTimeInputVisibility('#Monday-box', '#Monday');
  // });
  // TuesdayBox.on('click', function() {
  //   setDeliveryTimeInputVisibility("#Tuesday-box", '#Tuesday');
  // });
  // WednesdayBox.on('click', function() {
  //   setDeliveryTimeInputVisibility("#Wednesday-box", '#Wednesday');
  // });
  // ThursdayBox.on('click', function() {
  //   setDeliveryTimeInputVisibility("#Thursday-box", '#Thursday');
  // });
  // FridayBox.on('click', function() {
  //   setDeliveryTimeInputVisibility("#Friday-box", '#Friday');
  // });
  // SaturdayBox.on('click', function() {
  //   setDeliveryTimeInputVisibility("#Saturday-box", '#Saturday');
  // });
  // SundayBox.on('click', function() {
  //   setDeliveryTimeInputVisibility("#Sunday-box", '#Sunday')
  // });
  accepting24hrBox.on('click', function() {
    setAcceptingTimeInputVisibility('#accepting-24hr-box','#accepting-time')
  });

});

function setDeliveryTimeInputVisibility(checkbox, timeInput) {
  if($(checkbox).is(':checked')) {
    $(timeInput).removeClass('d-none');
    $(timeInput + ' :input');
  } else {
    $(timeInput).addClass('d-none');
    $(timeInput + ' :input');
  }
}

function setAcceptingTimeInputVisibility(checkbox, timeInput) {
  if(!$(checkbox).is(':checked')) {
    $(timeInput).removeClass('d-none');
    $(timeInput + ' :input');
  } else {
    $(timeInput).addClass('d-none');
    $(timeInput + ' :input');
  }
}
