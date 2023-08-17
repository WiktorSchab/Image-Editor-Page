// Setting size of canvas to size of image and using image as background */
function imageLoad() {
    var canvas = $('#canvas')[0];

    // Creating new image obj //
    var img = new Image();

    // Setting source of image to file given by user with use of Flask function to locate img //
    img.src = "{{url_for('static',filename='download/modified/'+file_name)}}";

    // Waiting img to fully load
    img.onload = function() {
        // Declaring original proportion of image to ratio variable
        imageLoaded = true;
        var ratio = img.height / img.width;

        // Setting size of image with height 512 and width that its 512/original image ratio
        var height = 512;
        var width  = height / ratio;

        // Setting size of canvas as the same size as image have
        canvas.width = width;
        canvas.height = height;

        // Getting 2d render of ctx of canvas
        var ctx = canvas.getContext('2d');

        // Drawing loaded render of given image
        ctx.drawImage(img, 0, 0, width, height);
    };
};


// Drawing functions
// Setting current tool
function setTool(toolReference){
    // Deleting border if toolCurrent is not null
    if (toolCurrent){
            toolCurrent.css({'border':'none',
            'background-color':'transparent',
            'padding':'0px'});
    }

    // Checking if clicked tool is the same as it was
    if (toolCurrent !== null && toolReference === toolCurrent.attr('id')){
        toolCurrent = null;
    }else{
        // Setting new tool as current one
        toolCurrent = $('#'+toolReference);

        // Setting border to new tool
        toolCurrent.css(toolCurrentStyle)
    }
}


// Placing the circles in the place where the pressed mouse is
function drawCircle(x,y) {
    // Starting drawing path
    ctx.beginPath()

    // Drawing circle with set color and size. Color is filling circle
    ctx.arc(x, y, size, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
}

// Drawing line between circles (that appear when user draw fast)
function drawLine(x1, y1, x2, y2) {

    // Starting drawing path
    ctx.beginPath();

    // Setting start point
    ctx.moveTo(x1,y1);

    // Setting line from start point to point with x2, y2 cords
    ctx.lineTo(x2,y2);

    // Setting properties of drawing
    ctx.strokeStyle = color;
    ctx.lineWidth = size * 2;

    // Drawing line
    ctx.stroke();
    a = ctx;
}


// Functions that work when brush is current tool
function toolBrush(x, y, x2, y2){
    // Function to create circle in actual mouse position
    drawCircle(x2,y2);
    // Function that creates line between old and new mouse position
    drawLine(x, y ,x2, y2);

    // Assigning actual position of mouse to x and y, so they can be used as old one in next function call
    x = x2;
    y = y2;
    return [x,y]
}

// Functions that work when rectangle is current tool
function toolRectangle(x, y, x2, y2){
    // Checking if figure need to be full
    if (checkboxFillValue){
        // Filling rectangle with color given as side color
        ctx.fillStyle = colorSide;
        // Creating filled rectangle with one color
        ctx.fillRect(x2, y2, x - x2, y - y2);
    }

    // Creating empy rectangle
    ctx.strokeRect(x2, y2, x - x2, y - y2);
}

// Functions that work when circle is current tool
function toolCircle(x, y, x2, y2){
    // Checking if figure need to be full
    if (checkboxFillValue){
        ctx.fillStyle = colorSide;
        ctx.fill();
    }

    ctx.beginPath();
    var radius = Math.sqrt(Math.pow((x - x2), 2) + Math.pow((y - y2), 2));
    ctx.arc(x,y, radius, 0, 2 * Math.PI);
    ctx.stroke();
}

// Functions that work when triangle is current tool
function toolTriangle(x, y, x2, y2){
    // Checking if figure need to be full
    if (checkboxFillValue){
        ctx.fillStyle = colorSide;
        ctx.fill();
    }

    ctx.beginPath();
    ctx.moveTo(x, y);

    ctx.lineTo(x2, y2);
    ctx.lineTo(x * 2 - x2, y2)
    ctx.closePath()

    ctx.stroke();
}

// Functions to draw
function drawing(){
    // Deleting added events for canvas
    canvas.off('mousedown mousemove mouseup');
    if (toolCurrent === null){
        return;
    }

    // Function that assign position of mouse to x,y if user click. It runs when user start drawing
    canvas.on('mousedown', function (e){
            isMouseDown = true;

            // Getting current state of image
            snapshot = ctx.getImageData(0,0, canvas[0].width, canvas[0].height);

            // Starting cords
            x = e.offsetX;
            y = e.offsetY;
    });

    // Stopping drawing if user stop pressing mouse. It runs when user stops drawing
    canvas.on("mouseup", function (e) {
            isMouseDown = false;

            // Giving as last elements of cordTempArray info about size and color of brush so they will be remembered
            cordTempArray.push(colorSide, checkboxFillValue, snapshot, toolCurrent.attr('id'), ctx.lineWidth, ctx.strokeStyle)

            // Giving cordTempArray to main storing array as one group of cords
            cordArray.push(cordTempArray);

            // Clearing array
            cordTempArray = [];

            // Setting variables that holds position of mouse to null //
            x = null;
            y = null;
        });

    // Functions that make drawing by following mouse move. It runs when user is drawing
    canvas.on('mousemove', function (e) {
        // Returning from funct if user stop pressing mouse
        if (!isMouseDown) return;

        // Setting properties of drawing
        ctx.strokeStyle = color;
        ctx.lineWidth = size * 2;

        // Assigning actual position of mouse to variables
        var x2 = e.offsetX;
        var y2 = e.offsetY;

        // Sending cords of move to array that collects info
        cordTempArray.push([x,y,x2,y2]);

        // Function when current tool is brush
        if (toolCurrent.attr('id') === 'brush') {
            // Calling brush function and assigning new cords as the old one
            [x, y] = toolBrush(x, y, x2, y2);
            return;
        }

        // Putting remembered image to ctx (figures could be now empty)
        ctx.putImageData(snapshot, 0, 0);

        // Function when current tool is rectangle
        if (toolCurrent.attr('id') === 'rectangle'){
           toolRectangle(x, y, x2, y2);
        }

        // Function when current tool is circle
        if (toolCurrent.attr('id') === 'circle'){
            toolCircle(x, y, x2, y2);
        }

        // Function when current tool is triangle
        if (toolCurrent.attr('id') === 'triangle'){
            toolTriangle(x, y, x2, y2);
        }
    });
}

// Waiting for document to fully load up
$(document).ready(function() {
    // Loading image that user send as background for canvas
    imageLoad();

    // Setting border to default chosen tool
    toolCurrent.css(toolCurrentStyle);

    // Starting drawing function
    drawing();
});


// Button to save draw
var buttonSave = $('#save_changes_button');

// Buttons & inputs on draw menu
// On left
var buttonClear = $('#buttonClear');
var buttonBack = $('#buttonBack');
var sizeInput = $('.size');
var checkboxFill = $('#checkbox_fill');
var checkboxFillImg = $('#checkbox_fill_img');

// On right
// Tools to draw
var rectangle = $('#rectangle_tool');
var brush = $('#brush');
var toolObjects = $('.tool');

// Button to swap colors
var colorSwap = $('#color_change');
// Inputs to choose color
var colorInputMain = $('#color_tool_main');
var colorInputSide = $('#color_tool_side');

// Assigning object from html to variables
var canvas = $('#canvas');

// Creating ctx to allow user drawing and assigning it to ctx var
var ctx = $('#canvas')[0].getContext('2d');

//  Setting default variables
var isMouseDown = false;
var checkboxFillValue = false;
var color = '#000';
var colorSide = '#F5E3E0';
var size = 10;
var x,y,x2,y2,snapshot;

// Default tool is brush
var toolCurrent = $('#brush');

//Arrays & dict
// Declaring array that will be contain cords of mouse drawing (one draw)
var cordTempArray = [];
// Declaring aray will holds cordTempArrays values as values (one cordTempArray == one value)
var cordArray = [];

// Style for the chosen tool
var toolCurrentStyle = {'border':'3px solid #c3d9ce',
        'background-color':'white',
        'padding':'13px',
        'border-radius':'13px'}

// Css parameters for checkboxFillValue
var checkboxLink = {false: '{{ url_for("static", filename="icons/checkbox_false_icon.png") }}',
    true:'{{ url_for("static", filename="icons/checkbox_true_icon.png") }}'};
var checkboxTitle = {false: 'Click to have filled figures', true: 'Click to have empty figures'}


// Going to drawing function when user click on some tool
toolObjects.on('click', function (e) {
    // Function check what tool was clicked and give specific events for mouse on canvas
    drawing();
});


// Functions to objects on toolbar
// Cleaning canvas
buttonClear.on('click', function (e) {
   // Cleaning canvas from everything
   ctx.clearRect(0, 0, canvas.width, canvas.height);

   // Loading image as background again
   imageLoad();

   // Deleting array drawing cords
   cordArray = [];
});

// Deleting user last draw
buttonBack.on('click', function (e){
    /* Setting imageLoaded to false so other part of function will start if image will be fully loaded.
    imageLoaded is changing by the end of imageLoad function. */
    imageLoaded = false;

    /* Deleting last group of cord array (in other words deleting last drawing from user from canvas ) */
    cordArray.pop();

    /* Loading up canvas (only image as background) */
    imageLoad();

    // Setting interval that will be looking if image is fully loaded
    var checkImageLoaded = setInterval(function() {
        // imageLoaded is true if Image is fully loaded
        if (imageLoaded) {
            // Clearing Interval (so it will stop checking)
            clearInterval(checkImageLoaded);

            /* Restoring drawing on image without last move
            Iteration by group of array in cordArray (one array is one drawing without letting mouse off) */
            for (var i = 0; i < cordArray.length; i++) {

                // Assigning one array to cordGroup variable
                var cordGroup = cordArray[i];


                //Setting color of brush that was used to paint drawing
                color = cordGroup[cordGroup.length - 1];
                // Setting size of brush that was used to paint drawing
                size = cordGroup[cordGroup.length - 2]/2 ;
                // Setting used tool
                tool = cordGroup[cordGroup.length - 3];
                // Setting snapshot
                snapshot = cordGroup[cordGroup.length - 4];
                // Setting checkboxFillValue
                checkboxFillValue = cordGroup[cordGroup.length - 5];
                // Setting side color_value
                colorSide = cordGroup[cordGroup.length - 6];

                /* Iteration by array with all cords in group (known as x1, y1, x2, y2 in other funct)
                Iteration goes without last 6 elements.
                They only hold info about size, color, tool, checkboxFillValue and side color */
                for (var j = 0; j < cordGroup.length - 6; j++) {

                    // Assigning one array to cords
                    [x, y , x2, y2] = cordGroup[j];

                    // Restoring line if tool was brush. Else restoring figure
                    if (tool === 'brush'){
                        // Drawing circle on canvas
                        drawCircle(x2, y2);
                        // Connecting circle on canvas with line
                        drawLine(x, y, x2, y2);
                    }else{
                        /* Restoring figures
                         Putting last image of canvas to make figures empty */
                        ctx.putImageData(snapshot, 0, 0);

                        // Assigning parameters for figures
                        ctx.strokeStyle = color;
                        ctx.lineWidth = size * 2;

                        // Restoring rectangle if tool was rectangle, if else circle, else triangle
                        if (tool === 'rectangle'){
                            // Calling function to draw rectangle
                            toolRectangle(x, y, x2, y2);
                        }else if(tool == 'circle'){
                            toolCircle(x, y, x2, y2);
                        }else{
                            toolTriangle(x, y, x2, y2);
                        }
                    }
                }
            }
            // Changing appearance of checkbox
            checkboxFillImg.attr('src', checkboxLink[checkboxFillValue]);
            // Changing title of checkbox
            checkboxFillImg.attr('title', checkboxTitle[checkboxFillValue]);

            // Changing showing colors on menu to match colors used in certain moment
            colorInputMain.val(color);
            colorInputSide.val(colorSide);
            // Changing showing size on menu to match size of the brush
            $('.size').val(size);
        }
    }, 100); // How often it will be checking (in ms)
});

// Choosing size of tool
sizeInput.on('input', function() {
    size = $(this).val();

    //Making sure that user dont enter value higher than max
    if (size > 20){
        size = 20
    }

    // Changing displaying size on input number and input change
    $('.size').val(size);
});

// Button that works as checkbox (checkbox for fill value of figures)
checkboxFill.on('click',function (e) {


    // Operation not on checkboxFillValue
    checkboxFillValue = checkboxFillValue ? false : true;

    // Changing appearance of checkbox
    checkboxFillImg.attr('src', checkboxLink[checkboxFillValue]);
    // Changing title of checkbox
    checkboxFillImg.attr('title', checkboxTitle[checkboxFillValue]);
});

// Swapping main color and with side color
colorSwap.on('click', function (e){
    // Swapping values in variables
    [color,colorSide] = [colorSide,color];

    // Displaying new values;
    colorInputMain.val(color);
    colorInputSide.val(colorSide);
});


// If user change main color, assign new color to color var
colorInputMain.on('change', function (e) {
    color = $(this).val()
});

// If user change side color, assign new color to color side var
colorInputSide.on('change', function (e) {
    colorSide = $(this).val()
});


// Saving changes & redirect to index.html
buttonSave.on('click', function (e) {
    var dataURI = canvas[0].toDataURL();

    // Ajax request
    $.ajax({
        type: 'POST',  // Method
        url: '{{ url_for("draw_mode_saving") }}',  // Address of flask page where to send data
        data: { image_data_uri: dataURI },  // Data that will be send to server
        success: function(response) {
        console.log('Data was sent.');
        }
    });
});
