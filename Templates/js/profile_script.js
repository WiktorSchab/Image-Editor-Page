var header = $('header');

// Adding style to picture in history
function mouse_on_history_pic(id){
    // Adding dark filter on image
    $('#image_' + id).addClass('dark_filter');
    $('#button_history_' + id).css('visibility', 'visible');
}

// Removing style from picture in history
function mouse_off_history_pic(id){
    $('#image_' + id).removeClass('dark_filter');
    $('#button_history_' + id).css('visibility', 'hidden');
}

var bg = $('#profile_change_window_bg');
var profile_window = $('#profile_change_window');

// Id of obj where mouse is
var where_mouse = '';


// Returning user to profile
function return_to_prof(user_nick){
    if (where_mouse == 'profile_change_window_bg'){
        window.location.href = '/profile/' + user_nick;
    }
}

// Tracking on what obj mouse is
document.addEventListener('mouseover', showElementId);
function showElementId(event) {
    where_mouse = event.target.id;
}


// Scripts that will run when DOM will be fully loaded
$(document).ready(function() {
    // Removing header
    if (header){
        header.remove();
    }
});