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

// Scripts that will run when DOM will be fully loaded
$(document).ready(function() {
    // Removing header
    if (header){
        header.remove();
    }
});