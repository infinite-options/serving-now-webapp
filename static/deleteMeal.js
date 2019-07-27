function deleteMeal(id) {
    var request = new XMLHttpRequest();

    //async has to be false because the webpage will refresh before the
    //database can be updated                          Here
    request.open("GET", '/api/v1/meals/' + id, /* async = */ false);
    request.send();
    window.location = "/kitchens/" + id;
}
