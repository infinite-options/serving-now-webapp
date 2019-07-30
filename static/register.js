/*
* @Author: Japan Parikh
* @Date:   2019-05-24 21:51:33
* @Last Modified by:   Japan Parikh
* @Last Modified time: 2019-05-25 13:38:29
*/


function registerKitchen() {
	var formData = new FormData();
	var request = new XMLHttpRequest();

	var name = document.getElementById("name").value;
	var description = document.getElementById("description").value;
	var username = document.getElementById("username").value;
	var password = document.getElementById("password").value;
	var verifyPassword = document.getElementById("verify-password").value;
	var firstName = document.getElementById("first_name").value;
	var lastName = document.getElementById("last_name").value;
	var street = document.getElementById("street").value;
	var state = document.getElementById("state").value;
	var city = document.getElementById("city").value;
	var zipCode = document.getElementById("zip_code").value;
	var phoneNumber = document.getElementById("phone_number").value;
	var closeTime = document.getElementById("close_time").value;
	var openTime = document.getElementById("open_time").value;
  var email = document.getElementById("email").value;
  var deliveryOpenTime = document.getElementById("delivery_open_time").value;
  var deliveryCloseTime = document.getElementById("delivery_close_time").value;
  var pickup = false;
  if (document.getElementById("pickup").checked) {
    pickup = true;
  }
  var delivery = false;
  if (document.getElementById("delivery").checked) {
    delivery = true;
  }
  var reusable = false;
  if (document.getElementById("reusable").checked) {
    reusable = true;
  }
  var disposable = false;
  if (document.getElementById("disposable").checked) {
    disposable = true;
  }
  var can_cancel = false;
  if (document.getElementById("can_cancel").checked) {
    can_cancel = true;
  }

  if (Date.parse(closeTime) < Date.parse(openTime)) {
    window.alert("Please enter vaild accepting hours")
    return false;
  }

  if (Date.parse(deliveryCloseTime) < Date.parse(deliveryOpenTime)) {
    window.alert("Please enter vaild delivery hours")
    return false;
  }


	// if (name == "" || username == "" || password == "" ||
	// 	verifyPassword == "" || firstName == "" || lastName == "" ||
	// 	address == "" || city == "" || state == "" ||
	// 	phoneNumber == "" || zipcode == "" || closeTime == "" ||
	// 	openTime == "" || email == "") {

	// 	console.log("fields are empty");

	// } else {
  formData.append("description", description);

	formData.append("name", name);
	formData.append("username", username);
	formData.append("password", password);
	formData.append("verify-password", verifyPassword);
	formData.append("first_name", firstName);
	formData.append("last_name", lastName);
	formData.append("street", street);
	formData.append("state", state);
	formData.append("city", city);
	formData.append("zip_code", zipCode);
	formData.append("phone_number", phoneNumber);
	formData.append("close_time", closeTime);
	formData.append("open_time", openTime);
	formData.append("email", email);
	formData.append("delivery_open_time", delivery_open_time);
	formData.append("delivery_open_time", delivery_close_time);
	formData.append("pickup", pickup);
	formData.append("delivery", delivery);
	formData.append("reusable", reusable);
	formData.append("disposable", disposable);
	formData.append("can_cancel", can_cancel);

	request.open("POST", "/accounts/register", true);

  request.onload = function() {
      if (request.readyState === request.DONE) {
          if (request.status === 400) {
              window.location = "register"
          }
          if (request.status === 200) {
              window.location = "login"
          }
      }
  }

	request.send(formData);

	// }
}
