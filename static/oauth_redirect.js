const hash = window.location.hash;
if(hash.substring(1,13) == "access_token") {
    window.location = "/#auth/" + hash;
}