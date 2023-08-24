// Cookies functions
function setCookie(name, value, daysToLive) {
    const date = new Date();
    date.setTime(date.getTime() + daysToLive * 24 * 60 * 60 * 1000); // Setting how many millisecond cookie have to live
    let expires = 'expires=' + date.toUTCString();

    // Setting cookie with given values in default for cookies path ('/')
    document.cookie = `${name}=${value}; ${expires}; path=/`;
}

function deleteCookie(name){
    setCookie(name,null,null); //setting date of live of cookie to null so he will die immediately
}

function getCookie(name){
    const cDecoded = decodeURIComponent(document.cookie); // Decoding values of cookies
    const cArray = cDecoded.split('; '); // Splitting cookies
    let result = null;

    cArray.forEach(element => {
        if(element.indexOf(name) == 0) {
            result = element.substring(name.length + 1) // Separating value of cookie
        }
    });
    return result; // Returning value of cookie if it exists otherwise null
}


// Function to remember scroll position of object after clicking on <a> obj
$('a').on('click', function() {
    // Remembering scroll of window
    setCookie('positionCookieWindow', window.scrollY, 1);

    // Remembering scroll of color filters
    positionScrollWindowColor = $(".position_color").scrollTop();
    setCookie('positionCookieColor', positionScrollWindowColor, 1);

    // Remembering scroll of color filters
    positionScrollWindowFilter = $(".position_filter").scrollTop();
    setCookie('positionCookieFilter', positionScrollWindowFilter, 1);
});


// Function to add clicked button id to cookie file if its not there otherwise delete id from the file
function colorButton(id) {
    cookie = getCookie('colorButtons');

    if (cookie === null) {  // Checking if cookie exist and its correctly created
        setCookie('colorButtons', 'Id:', 1);
        cookie = getCookie('colorButtons');
    }

    if(cookie.includes(id)) {
        if (cookie.length === 5) { // Deleting cookie if there is only one obj (5 bcs id: id)
            deleteCookie('colorButtons');
        } else {
            // Deleting id of clicked button from cookie
            cookie = cookie.replace(id,'');
            setCookie('colorButtons',cookie,1);
        }
    }else{
        // Adding id of button to cookie
        cookie = cookie +' ' +id;
        setCookie('colorButtons',cookie,1);
    }
}


// Function to for closing modal
function modalClosing() {
    // User click on dokument
    $(document).on('click', function(event) {
        // If that click outside of modal, on cancel button or on 'x' button user will be redirect to index
        if (!$(event.target).closest('.modal-content').length || $(event.target).hasClass('cancel'))  {
                window.location.href = '/';
        }
    });
}


// Function to display history cart
function historyShow(){
    if (history_status == 0){

        historyContent.removeClass('fade-out');
        historyContent.addClass('fade-in');

        // Showing content
        historyContent.css({'visibility':'visible'});

    }else{

        historyContent.removeClass('fade-in');
        historyContent.addClass('fade-out');

        // Hiding content after 3s because animation need to be finished first
        setTimeout(function () {
            historyContent.css({'visibility':'hidden'});
        }, 3000);
    }

    historyButton.toggle();
    // 1 --> 0, 0 --> 1
    history_status = (history_status + 1) % 2
}
// Script for that add link to profile
document.getElementById('profile_link').href = '{{ url_for('profile', user_nick=session.get('user')) }}';

//colors to buttons
colorList = ['#9c31bd','#eb98d7','#cf0e27','#fa8c16','#ebf227','#28c916','#1ea1e3','#c0cbd1'];

var imgMain = $('#img_main')[0];

// Path to static
var staticPath = "{{ url_for('static', filename='') }}";

// History content &
var historyContent = $('#history_content');

// Value that is saying if history is showed or not
history_status = 0

// Button to open history
var historyButton = $('#history_button');

for (let i = 0; i < (colorList.length); i++) {
    cookie = getCookie('colorButtons');
    // Checking if cookie exists and have numer button id
    if (cookie !== null && cookie.includes(i)){
        colorId = '#colorId' + i;

        // Setting styles for colorId
        $(colorId).css({"background": colorList[i]});
        $(colorId).css({"border-color": colorList[i]});
        $(colorId).css({"color": "white"});
    }
}


$(document).ready(function() {
    // Setting scroll position of window
    window.scrollTo(0, getCookie('positionCookieWindow'));

    // Setting scroll position of color filters
    $(".position_color").scrollTop(getCookie('positionCookieColor'));

    // Setting scroll position of filters
    $(".position_filter").scrollTop(getCookie('positionCookieFilter'));


    // Showing modals (they will be on page only if user click specific button)
    $('#confirmModal').modal('show');
    $('#downloadModal').modal('show');

    imgMain.src ="{{url_for('static',filename='download/modified/'+file_name)}}";

    // Checking if user is in correct location
    if(window.location.href.includes('http://127.0.0.1:5000/reset_change_confirm/')) {
        // function to close modal
        modalClosing();
    }

    // Checking if user is in correct location
    if(window.location.href.includes('http://127.0.0.1:5000/download/')) {
        // Function to close modal
        modalClosing();
    }
});