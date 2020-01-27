function logout() {
    var url = "{% url 'logout' %}";
    $.get(
        url,
        function (data) {
            $('#popup').html('<div style="visibility: visible; width: 100vw; height: 100vh; display: flex; flex-direction: column; position: fixed; float: none; z-index: 999; background-color: #0008;'
                + 'justify-content: center; align-items: center;"><a href="javascript:refresh()" style="text-decoration: none;"><div style="display: flex; flex-direction: column; justify-content: center; align-items: center; width: 80vw; height: 20vh;'
                + 'border-radius: 0.5rem; background-color: #000b; color: #888;">Logout Success.</div></a></div>');
        }
    );
}

function refresh() {
    location.reload();
}