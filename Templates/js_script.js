//cookies functions
function setCookie(name, value, daysToLive){
    const date = new Date();
    date.setTime(date.getTime() + daysToLive * 24 * 60 * 60 * 1000);
    let expires = "expires=" + date.toUTCString();

    document.cookie = `${name}=${value}; ${expires}; path=/`;
}

function deleteCookie(name){
    setCookie(name,null,null);
}

function getCookie(name){
    const cDecoded = decodeURIComponent(document.cookie);
    const cArray = cDecoded.split('; ');
    let result = null;

    cArray.forEach(element => {
        if(element.indexOf(name) == 0){
            result = element.substring(name.length + 1)
        }
    })
    return result;
}

//function to remember scroll position of object
function scroll_rem(child){
    position_of_scroll = $(".position").scrollTop();
    setCookie('position_cookie',position_of_scroll,1);
}

//function to add clicked button id to cookie file if its not there otherwise delete id from file
function color_button(id){
    cookie = getCookie('Color_buttons');

    if (cookie === null || cookie.length < 0){  //checking if cookie exist and its correctly created
        setCookie('Color_buttons','Id:',1);
    } else{
        if(cookie.includes(id)){
            if (cookie.length === 5){ //deleting cookie if there is only one obj (5 bcs id: id)
                deleteCookie('Color_buttons');
            }else{
                cookie = cookie.replace(id,'');
                setCookie('Color_buttons',cookie,1);
            }
        }else{
            cookie = cookie +' ' +id;
            setCookie('Color_buttons',cookie,1);
        }
    }
}

$(".position").scrollTop(getCookie('position_cookie')); //setting scroll position of object

//colors to buttons
list_of_color = ['#9c31bd','#eb98d7','#cf0e27','#fa8c16','#ebf227','#28c916','#1ea1e3','#c0cbd1']

cookie = getCookie('Color_buttons');

for (let i = 0; i < (list_of_color.length); i++) {
    if (cookie !== null && cookie.includes(i)){
        color_id = '#color_id' + i;

        //setting styles
        $(color_id).css({"background": list_of_color[i]});
        $(color_id).css({"border-color": list_of_color[i]});
        $(color_id).css({"color": "white"});
    }
}


