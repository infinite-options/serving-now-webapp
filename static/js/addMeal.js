function postMeal() {
    console.log('post meal function called');
    var request = new XMLHttpRequest();
    var formData = new FormData();

    var validate_price = document.getElementById('add_meal_price').value;
    var meal_name = document.getElementById('add_meal_mealname').value;

    console.log(validate_price);
    console.log(meal_name);

    if (validate_price == "" || validate_price[0] == "-" || meal_name == "") {
        window.alert('Please enter valid value');
        return false;
    }

    var meal_options_elem = document.getElementById('option-items');
    var meal_options = meal_options_elem.options[meal_options_elem.selectedIndex].value;

    var items = {};
    var options = [];

    for (var i = 1; i <= meal_options; i++) {
        var name_id = 'add_meal_option'.concat(i, '_name');
        var qty_id = 'add_meal_option'.concat(i, '_qty');
        var item_name = document.getElementById(name_id).value;
        var item_qty_id = document.getElementById(qty_id);
        var item_qty = item_qty_id.options[item_qty_id.selectedIndex].value;
        var obj = {}
        obj["title"] = item_name
        obj["qty"] = item_qty
        options.push(obj);
    }

    items['meal_items'] = options
    console.log(document.getElementById('add_meal_image').files[0]);

    // Bind the FormData object and the form element
    formData.append('name', document.getElementById('add_meal_mealname').value)
    formData.append('items', JSON.stringify(items))
    formData.append('price', document.getElementById('add_meal_price').value)
    formData.append('photo', document.getElementById('add_meal_image').files[0]);

    // The data sent is what the user provided in the form
    //async has to be false because the webpage will refresh before the
    //database can be updated                          Here
    request.open("POST", "/kitchens/meals/create", false);
    request.send(formData);

    console.log("finshed POST, Before refresh")
}

function readURL(input) {
  console.log("in readURL")
  if (input.files && input.files[0]) {
    var reader = new FileReader();

    reader.onload = function(e) {
      debugger;
      $('#img-upload').attr('src', e.target.result);
        var canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;
        canvas.getContext("2d").drawImage(this, 0, 0, width, height);

        //Causing Infinite Loop in your code
        //img.src = e.target.result;

        // Get dataURL of resized image from canvas
        show.src = canvas.toDataURL('image/png');

    }
    reader.readAsDataURL(input.files[0]);

  }
}

// function previewFile() {
//     var preview = document.querySelector('.img-bg'); //selects the query named img
//     var file = document.querySelector('input[type=file]').files[0]; //sames as here
//     var reader = new FileReader();
//
//     reader.onloadend = function() {
//         preview.src = reader.result;
//     }
//     if (file) {
//         reader.readAsDataURL(file); //reads the data as a URL
//     } else {
//         preview.src = "Upload Photo";
//     }
// }
// previewFile();
