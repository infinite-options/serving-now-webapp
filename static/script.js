
//String.prototype.format = function() {
//	a = this;
//	for (k in arguments) {
//		a = a.replace("{" + k + "}", arguments[k])
//	}
//	return a
//}

String.prototype.format = String.prototype.f = function() {
	var s = this,
		i = arguments.length;

	while (i--) {
		s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
	}
	return s;
};


var mealOptionsSelected = 1;
var mealOptions = [];


$(document).ready(function () {
//	console.log($("#meal-options option:selected").text());


	$("#option-item1").show();
	$("#option-item2").hide();
	$("#option-item3").hide();
	$("#option-item4").hide();
	$("#option-item5").hide();


	$("#meal-options").change(function () {
		mealOptionsSelected = $(this).children("option:selected").val();

		if (mealOptionsSelected == 1) {
			$("#option2-setup").hide();
			$("#option2-title").hide();
			$("#option3-setup").hide();
			$("#option3-title").hide();
		} else if (mealOptionsSelected == 2) {
			$("#option2-setup").show();
			$("#option2-title").show();

			$("#option3-setup").hide();
			$("#option3-title").hide();
		} else if (mealOptionsSelected == 3) {
			$("#option2-setup").show();
			$("#option2-title").show();

			$("#option3-setup").show();
			$("#option3-title").show();
		}
	});

	$("#option-items").change(function () {
		var totalItems = $(this).children("option:selected").val();

		if (totalItems == 1) {
			$("#option-item1").show();
			$("#option-item2").hide();
			$("#option-item3").hide();
			$("#option-item4").hide();
			$("#option-item5").hide();
		} else if (totalItems == 2) {
			$("#option-item1").show();
			$("#option-item2").show();
			$("#option-item3").hide();
			$("#option-item4").hide();
			$("#option-item5").hide();
		} else if (totalItems == 3) {
			$("#option-item1").show();
			$("#option-item2").show();
			$("#option-item3").show();
			$("#option-item4").hide();
			$("#option-item5").hide();
		} else if (totalItems == 4) {
			$("#option-item1").show();
			$("#option-item2").show();
			$("#option-item3").show();
			$("#option-item4").show();
			$("#option-item5").hide();
		} else if (totalItems == 5) {
			$("#option-item1").show();
			$("#option-item2").show();
			$("#option-item3").show();
			$("#option-item4").show();
			$("#option-item5").show();
		}
	});



//	console.log($("#meal-form"));
	$("#sendData").click(function () {
//		$("#option1-item1").children("td").children("select").children("option:selected").val()
		$("#meal-form").append($("#option-item1").children("td").children("select").children("option:selected").val());
		console.log($("#meal-form"));
	});




})