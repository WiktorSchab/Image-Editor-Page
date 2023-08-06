// Cookies functions
function setCookie(name, value, daysToLive){
    const date = new Date();
    date.setTime(date.getTime() + daysToLive * 24 * 60 * 60 * 1000); // Setting how many millisecond cookie have to live
    let expires = "expires=" + date.toUTCString();

    // Setting cookie with given values in default for cookies path ('/')
    document.cookie = `${name}=${value}; ${expires}; path=/`;
}

function deleteCookie(name){
    setCookie(name,null,null);
}

function getCookie(name){
    const cDecoded = decodeURIComponent(document.cookie); // Decoding values of cookies
    const cArray = cDecoded.split('; '); // Splitting cookies
    let result = null;

    cArray.forEach(element => {
        if(element.indexOf(name) == 0){
            result = element.substring(name.length + 1) // Separating value of cookie
        }
    })
    return result; // Returning value of cookie if it exists otherwise null
}

// Function to remember scroll position of object
function scroll_rem(child){
    position_of_scroll = $(".position").scrollTop();
    setCookie('position_cookie',position_of_scroll,1);
}

// Function to add clicked button id to cookie file if its not there otherwise delete id from the file
function color_button(id){
    cookie = getCookie('Color_buttons');

    if (cookie === null){  // Checking if cookie exist and its correctly created
        setCookie('Color_buttons','Id:',1);
    } else{
        if(cookie.includes(id)){
            if (cookie.length === 5){ // Deleting cookie if there is only one obj (5 bcs id: id)
                deleteCookie('Color_buttons');
            }else{
                // Deleting id of clicked button from cookie
                cookie = cookie.replace(id,'');
                setCookie('Color_buttons',cookie,1);
            }
        }else{
            // Adding id of button to cookie
            cookie = cookie +' ' +id;
            setCookie('Color_buttons',cookie,1);
        }
    }
}
// Setting scroll position of object
$(".position").scrollTop(getCookie('position_cookie'));

//colors to buttons
list_of_color = ['#9c31bd','#eb98d7','#cf0e27','#fa8c16','#ebf227','#28c916','#1ea1e3','#c0cbd1']


for (let i = 0; i < (list_of_color.length); i++) {
    cookie = getCookie('Color_buttons');
    // Checking if cookie exists and have numer button id
    if (cookie !== null && cookie.includes(i)){
        color_id = '#color_id' + i;

        // Setting styles for color_id
        $(color_id).css({"background": list_of_color[i]});
        $(color_id).css({"border-color": list_of_color[i]});
        $(color_id).css({"color": "white"});
    }
}


