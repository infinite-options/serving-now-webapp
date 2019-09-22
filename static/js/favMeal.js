function favMeal(id) {

    var request = new XMLHttpRequest();

    //async has to be false because the webpage will refresh before the
    //database can be updated                          Here
    request.open("POST", '/api/v1/meals/fav/' + id, /* async = */ true);

    request.onload = function() {
        if (request.readyState === request.DONE) {
            if (request.status === 200) {
                window.location = "/kitchens/" + id;
            }
        }
    }

    request.send();
}
