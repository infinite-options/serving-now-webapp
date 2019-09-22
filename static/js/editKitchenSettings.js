const BASE_URL = 'http://localhost:8080/kitchens';
const ENDPOINT = 'settings';

function updateRegistration(id) {
  var un = $('#username').val();
  var pw = $('#password').val();
  var vpw = $('#verify-password').val();

  if (pw !== vpw || pw === "") return;

  var uri = `${BASE_URL}/${id}/${ENDPOINT}`;
  var body = {
      type: 'registration',
      payload: {
          username: un,
          password: pw
      }
  };

  $.ajax({
      url: uri,
      type: 'POST',
      crossDomain: true,
      data: body,
      dataType: 'json',
      success: function(result) {
          console.log(result);
      }
  })
}

function updatePersonal(id) {
  var fn = $('#first_name').val();
  var ln = $('#last_name').val();
  var s = $('#street').val();
  var c = $('#city').val();
  var sta = $('#state').val();
  var zc = $('#zip_code').val();
  var pn = $('#phone_number').val();
  var e = $('#email').val();

  var uri = `${BASE_URL}/${id}/${ENDPOINT}`;
  var body = {
      type: 'personal',
      payload: {
          first_name: fn,
          last_name: ln,
          street: s,
          city: c,
          state: sta,
          zipcode: zc,
          phone_number: pn,
          email: e
      }
  };

  $.ajax({
      url: uri,
      type: 'POST',
      crossDomain: true,
      data: body,
      dataType: 'json',
      success: function(result) {
          console.log(result);
      }
  })
}

function updateKitchen(id) {
  var n = $('#kitchen_name').val();
  var d = $('#description').val();
  var ot = $('#open_time').val();
  var ct = $('#close_time').val();
  var dot = $('#delivery_open_time').val();
  var dct = $('#delivery_close_time').val();
  var dev = $('#delivery').is(':checked') ? true : false;
  var pic = $('#pickup').is(':checked') ? true : false;
  var reu = $('#reusable').is(':checked') ? true : false;
  var dis = $('#disposable').is(':checked') ? true : false;
  var cao = $('#can_cancel').is(':checked') ? true : false;

  var uri = `${BASE_URL}/${id}/${ENDPOINT}`;
  var body = {
      type: 'kitchen',
      payload: {
          kitchen_name: n,
          description: d,
          open_time: ot,
          close_time: ct,
          delivery_open_time: dot,
          delivery_close_time: dct,
          delivery: dev,
          pickup: pic,
          reusable: reu,
          disposable: dis,
          cancellation_option: cao
      }
  };

  $.ajax({
      url: uri,
      type: 'POST',
      crossDomain: true,
      data: body,
      dataType: 'json',
      success: function(result) {
          console.log(result);
      }
  })
}
