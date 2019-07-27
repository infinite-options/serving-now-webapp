$(document).ready(function() {

    $('#editMeal').on('shown.bs.modal', function(event) {
        //console.log('edit meal js called');
        var meal_id = event.relatedTarget.dataset.meal_id; // assigns meal ID from Kitchens.html
        var meal_name = event.relatedTarget.dataset.meal_name;
        var meal_photo = event.relatedTarget.dataset.meal_photo;
        var meal_price = event.relatedTarget.dataset.meal_price;
        var meal_description = event.relatedTarget.dataset.meal_description;

        $('#edit_meal_mealid').val(meal_id);
        $('#edit_meal_mealname').val(meal_name);
        $('#edit_meal_price').val(meal_price);

        var image = document.getElementById("edit_img_preview");
        image.src = meal_photo;

        //        $('#edit_img_preview').src(meal_photo)


        var meal_options_old = meal_description.split(",");
        //        console.log(meal_options_old);
        //        console.log(meal_options_old.length);

        var mealOptionsSelected = meal_options_old.length;
        var mealOptions = [];

        $('#edit-option-items').val(mealOptionsSelected);

        if (mealOptionsSelected == 1) {
            $("#edit-option-item1").show();
            $("#edit-option-item2").hide();
            $("#edit-option-item3").hide();
            $("#edit-option-item4").hide();
            $("#edit-option-item5").hide();

        } else if (mealOptionsSelected == 2) {
            $("#edit-option-item1").show();
            $("#edit-option-item2").show();
            $("#edit-option-item3").hide();
            $("#edit-option-item4").hide();
            $("#edit-option-item5").hide();

        } else if (mealOptionsSelected == 3) {
            $("#edit-option-item1").show();
            $("#edit-option-item2").show();
            $("#edit-option-item3").show();
            $("#edit-option-item4").hide();
            $("#edit-option-item5").hide();

        } else if (mealOptionsSelected == 4) {
            $("#edit-option-item1").show();
            $("#edit-option-item2").show();
            $("#edit-option-item3").show();
            $("#edit-option-item4").show();
            $("#edit-option-item5").hide();

        } else if (mealOptionsSelected == 5) {
            $("#edit-option-item1").show();
            $("#edit-option-item2").show();
            $("#edit-option-item3").show();
            $("#edit-option-item4").show();
            $("#edit-option-item5").show();

        }

        for (i = 0; i < mealOptionsSelected; i++) {
            $("#edit-option-item" + (i + 1)).show();
            var opt_item_qty_name = meal_options_old[i].trim();

            //    If there is number in name
            if (!isNaN(opt_item_qty_name.split(" ")[0])) {
                var opt_name = opt_item_qty_name.substr(opt_item_qty_name.indexOf(" ") + 1);
                $('#edit_meal_option' + (i + 1) + '_name').val(opt_name);

                $('#edit_meal_option' + (i + 1) + '_qty').val(opt_item_qty_name.split(" ")[0]);
            } else { // No number in name
                $('#edit_meal_option' + (i + 1) + '_name').val(opt_item_qty_name);
                $('#edit_meal_option' + (i + 1) + '_qty').val(1);

            }
        }
    });



    $("#edit-option-items").change(function() {
        var totalItems = $(this).children("option:selected").val();

        if (totalItems == 1) {
            $("#edit-option-item1").show();

            $("#edit-option-item2").hide();
            $('#edit_meal_option2_name').val("");
            $('#edit_meal_option2_qty').val(1);

            $("#edit-option-item3").hide();
            $('#edit_meal_option3_name').val("");
            $('#edit_meal_option3_qty').val(1);

            $("#edit-option-item4").hide();
            $('#edit_meal_option4_name').val("");
            $('#edit_meal_option4_qty').val(1);

            $("#edit-option-item5").hide();
            $('#edit_meal_option5_name').val("");
            $('#edit_meal_option5_qty').val(1);

        } else if (totalItems == 2) {
            $("#edit-option-item1").show();
            $("#edit-option-item2").show();

            $("#edit-option-item3").hide();
            $('#edit_meal_option3_name').val("");
            $('#edit_meal_option3_qty').val(1);

            $("#edit-option-item4").hide();
            $('#edit_meal_option4_name').val("");
            $('#edit_meal_option4_qty').val(1);

            $("#edit-option-item5").hide();
            $('#edit_meal_option5_name').val("");
            $('#edit_meal_option5_qty').val(1);

        } else if (totalItems == 3) {
            $("#edit-option-item1").show();
            $("#edit-option-item2").show();
            $("#edit-option-item3").show();

            $("#edit-option-item4").hide();
            $('#edit_meal_option4_name').val("");
            $('#edit_meal_option4_qty').val(1);

            $("#edit-option-item5").hide();
            $('#edit_meal_option5_name').val("");
            $('#edit_meal_option5_qty').val(1);

        } else if (totalItems == 4) {
            $("#edit-option-item1").show();
            $("#edit-option-item2").show();
            $("#edit-option-item3").show();
            $("#edit-option-item4").show();

            $("#edit-option-item5").hide();
            $('#edit_meal_option5_name').val("");
            $('#edit_meal_option5_qty').val(1);

        } else if (totalItems == 5) {
            $("#edit-option-item1").show();
            $("#edit-option-item2").show();
            $("#edit-option-item3").show();
            $("#edit-option-item4").show();
            $("#edit-option-item5").show();
        }
    });
});
