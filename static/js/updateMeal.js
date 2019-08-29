function updateMeal() {
    console.log('edit/update meal function called');
    //console.log(id);
    var request = new XMLHttpRequest();
    var formData = new FormData();

    // Pull current meal information
    var meal_options_elem = document.getElementById('edit-option-items');
    var meal_options = meal_options_elem.options[meal_options_elem.selectedIndex].value;

    var items = {}; //Dictionary
    var options = []; //array

    for (var i = 1; i <= meal_options; i++) { //For loop for each option in meal
        var name_id = 'edit_meal_option'.concat(i, '_name'); //Meal Name
        var qty_id = 'edit_meal_option'.concat(i, '_qty'); //  Number of options in meal
        var item_name = document.getElementById(name_id).value; //
        var item_qty_id = document.getElementById(qty_id);
        var item_qty = item_qty_id.options[item_qty_id.selectedIndex].value;
        var obj = {}
        obj["title"] = item_name
        obj["qty"] = item_qty
        options.push(obj);
    }

    items['meal_items'] = options //populates array of meal_items
        //    console.log(items);

    // Bind the FormData object and the form element
    formData.append('name', document.getElementById('edit_meal_mealname').value)
    formData.append('items', JSON.stringify(items))
    formData.append('price', document.getElementById('edit_meal_price').value)


    var edit_meal_btn = document.getElementById('edit-meal-btn');

    var meal_id = document.getElementById('edit_meal_mealid').value;
    var old_photo = edit_meal_btn.getAttribute("data-meal_photo");
    var new_photo = document.getElementById('edit_meal_image').files[0];

    if (new_photo != null) {
        formData.append('photo', new_photo);
    } else {
        formData.append('photo', old_photo);
    }

    console.log(formData);

    // The data sent is what the user provided in the form
    //async has to be false because the webpage will refresh before the
    //database can be updated                          Here
    request.open("POST", "/kitchens/meals/" + meal_id, false);
    console.log(meal_id);
    request.send(formData);
}


function uploadButton(event) {
    //    console.log("on uploadButton new img called");
    event.value = '';

}

function uploadNewPhoto(Files) {
    //    console.log("upload new img called");

    $("#edit_img_preview").attr('src', URL.createObjectURL(Files[0]));
}
