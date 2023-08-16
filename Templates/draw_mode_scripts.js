// Setting size of canvas to size of image and using image as background */
function load_image() {
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

        // Getting 2d render of context of canvas
        var ctx = canvas.getContext('2d');

        // Drawing loaded render of given image
        ctx.drawImage(img, 0, 0, width, height);
    };
};


// Drawing functions
// Setting current tool
function setTool(toolReference){
    // Deleting border if current_tool is not null
    if (current_tool){
            current_tool.css({'border':'none',
            'background-color':'transparent',
            'padding':'0px'});
    }

    // Checking if clicked tool is the same as it was
    if (current_tool !== null && toolReference === current_tool.attr('id')){
        current_tool = null;
    }else{
        // Setting new tool as current one
        current_tool = $('#'+toolReference);

        // Setting border to new tool
        current_tool.css(chosen_tool_style)
    }
}


// Placing the circles in the place where the pressed mouse is
function drawCircle(x,y) {
    // Starting drawing path
    context.beginPath()

    // Drawing circle with set color and size. Color is filling circle
    context.arc(x, y, size, 0, Math.PI * 2);
    context.fillStyle = color;
    context.fill();
}

// Drawing line between circles (that appear when user draw fast)
function drawLine(x1, y1, x2, y2) {

    // Starting drawing path
    context.beginPath();

    // Setting start point
    context.moveTo(x1,y1);

    // Setting line from start point to point with x2, y2 cords
    context.lineTo(x2,y2);

    // Setting properties of drawing
    context.strokeStyle = color;
    context.lineWidth = size * 2;

    // Drawing line
    context.stroke();
    a = context;
}


// Functions that work when brush is current tool
function brush_tool(x, y, x2, y2){
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
function rectangle_tool(x, y, x2, y2){
    // Checking if figure need to be full
    if (checkbox_fill_value){
        // Filling rectangle with color given as side color
        context.fillStyle = color_side;
        // Creating filled rectangle with one color
        context.fillRect(x2, y2, x - x2, y - y2);
    }

    // Creating empy rectangle
    context.strokeRect(x2, y2, x - x2, y - y2);
}

// Functions that work when circle is current tool
function circle_tool(x, y, x2, y2){
    // Checking if figure need to be full
    if (checkbox_fill_value){
        context.fillStyle = color_side;
        context.fill();
    }

    context.beginPath();
    var radius = Math.sqrt(Math.pow((x - x2), 2) + Math.pow((y - y2), 2));
    context.arc(x,y, radius, 0, 2 * Math.PI);
    context.stroke();
}

// Functions that work when triangle is current tool
function triangle(x, y, x2, y2){
    // Checking if figure need to be full
    if (checkbox_fill_value){
        context.fillStyle = color_side;
        context.fill();
    }

    context.beginPath();
    context.moveTo(x, y);

    context.lineTo(x2, y2);
    context.lineTo(x * 2 - x2, y2)
    context.closePath()

    context.stroke();
}

// Functions to draw
function drawing(){
    // Deleting added events for canvas
    canvas.off('mousedown mousemove mouseup');
    if (current_tool === null){
        return;
    }

    // Function that assign position of mouse to x,y if user click. It runs when user start drawing
    canvas.on('mousedown', function (e){
            isMouseDown = true;

            // Getting current state of image
            snapshot = context.getImageData(0,0, canvas[0].width, canvas[0].height);

            // Starting cords
            x = e.offsetX;
            y = e.offsetY;
    });

    // Stopping drawing if user stop pressing mouse. It runs when user stops drawing
    canvas.on("mouseup", function (e) {
            isMouseDown = false;

            // Giving as last elements of cord_wait_room info about size and color of brush so they will be remembered
            cord_wait_room.push(color_side, checkbox_fill_value, snapshot, current_tool.attr('id'), context.lineWidth, context.strokeStyle)

            // Giving cord_wait_room to main storing array as one group of cords
            array_cords.push(cord_wait_room);

            // Clearing array
            cord_wait_room = [];

            // Setting variables that holds position of mouse to null //
            x = null;
            y = null;
        });

    // Functions that make drawing by following mouse move. It runs when user is drawing
    canvas.on('mousemove', function (e) {
        // Returning from funct if user stop pressing mouse
        if (!isMouseDown) return;

        // Setting properties of drawing
        context.strokeStyle = color;
        context.lineWidth = size * 2;

        // Assigning actual position of mouse to variables
        var x2 = e.offsetX;
        var y2 = e.offsetY;

        // Sending cords of move to array that collects info
        cord_wait_room.push([x,y,x2,y2]);

        // Function when current tool is brush
        if (current_tool.attr('id') === 'brush') {
            // Calling brush function and assigning new cords as the old one
            [x, y] = brush_tool(x, y, x2, y2);
            return;
        }

        // Putting remembered image to context (figures could be now empty)
        context.putImageData(snapshot, 0, 0);

        // Function when current tool is rectangle
        if (current_tool.attr('id') === 'rectangle'){
           rectangle_tool(x, y, x2, y2);
        }

        // Function when current tool is circle
        if (current_tool.attr('id') === 'circle'){
            circle_tool(x, y, x2, y2);
        }

        // Function when current tool is triangle
        if (current_tool.attr('id') === 'triangle'){
            triangle(x, y, x2, y2);
        }
    });
}

// Waiting for document to fully load up
$(document).ready(function() {
    // Loading image that user send as background for canvas
    load_image();

    // Setting border to default chosen tool
    current_tool.css(chosen_tool_style);

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
var checkbox_fill = $('#checkbox_fill');
var checkbox_fill_img = $('#checkbox_fill_img');

// On right
// Tools to draw
var rectangle = $('#rectangle_tool');
var brush = $('#brush');
var tool_objects = $('.tool');

// Button to swap colors
var color_change = $('#color_change');
// Inputs to choose color
var colorInputMain = $('#color_tool_main');
var colorInputSide = $('#color_tool_side');

// Assigning object from html to variables
var canvas = $('#canvas');

// Creating context to allow user drawing and assigning it to context var
var context = $('#canvas')[0].getContext('2d');

//  Setting default variables
var isMouseDown = false;
var checkbox_fill_value = false;
var color = '#000';
var color_side = '#F5E3E0';
var size = 10;
var x,y,x2,y2,snapshot;

// Default tool is brush
var current_tool = $('#brush');

//Arrays & dict
// Declaring array that will be contain cords of mouse drawing (one draw)
var cord_wait_room = [];
// Declaring aray will holds cord_wait_rooms values as values (one cord_wait_room == one value)
var array_cords = [];

// Style for the chosen tool
var chosen_tool_style = {'border':'3px solid #c3d9ce',
        'background-color':'white',
        'padding':'13px',
        'border-radius':'13px'}

// Css parameters for checkbox_fill_value
var link_checkbox = {false: '{{ url_for("static", filename="icons/checkbox_false_icon.png") }}',
    true:'{{ url_for("static", filename="icons/checkbox_true_icon.png") }}'};
var title_checkbox = {false: 'Click to have filled figures', true: 'Click to have empty figures'}


// Going to drawing function when user click on some tool
tool_objects.on('click', function (e) {
    // Function check what tool was clicked and give specific events for mouse on canvas
    drawing();
});


// Functions to objects on toolbar
// Cleaning canvas
buttonClear.on('click', function (e) {
   // Cleaning canvas from everything
   context.clearRect(0, 0, canvas.width, canvas.height);

   // Loading image as background again
   load_image();

   // Deleting array drawing cords
   array_cords = [];
});

// Deleting user last draw
buttonBack.on('click', function (e){
    /* Setting imageLoaded to false so other part of function will start if image will be fully loaded.
    imageLoaded is changing by the end of load_image function. */
    imageLoaded = false;

    /* Deleting last group of cord array (in other words deleting last drawing from user from canvas ) */
    array_cords.pop();

    /* Loading up canvas (only image as background) */
    load_image();

    // Setting interval that will be looking if image is fully loaded
    var checkImageLoaded = setInterval(function() {
        // imageLoaded is true if Image is fully loaded
        if (imageLoaded) {
            // Clearing Interval (so it will stop checking)
            clearInterval(checkImageLoaded);

            /* Restoring drawing on image without last move
            Iteration by group of array in array_cords (one array is one drawing without letting mouse off) */
            for (var i = 0; i < array_cords.length; i++) {

                // Assigning one array to cords_group variable
                var cords_group = array_cords[i];


                //Setting color of brush that was used to paint drawing
                color = cords_group[cords_group.length - 1];
                // Setting size of brush that was used to paint drawing
                size = cords_group[cords_group.length - 2]/2 ;
                // Setting used tool
                tool = cords_group[cords_group.length - 3];
                // Setting snapshot
                snapshot = cords_group[cords_group.length - 4];
                // Setting checkbox_fill_value
                checkbox_fill_value = cords_group[cords_group.length - 5];
                // Setting side color_value
                color_side = cords_group[cords_group.length - 6];

                /* Iteration by array with all cords in group (known as x1, y1, x2, y2 in other funct)
                Iteration goes without last 6 elements.
                They only hold info about size, color, tool, checkbox_fill_value and side color */
                for (var j = 0; j < cords_group.length - 6; j++) {

                    // Assigning one array to cords
                    [x, y , x2, y2] = cords_group[j];

                    // Restoring line if tool was brush. Else restoring figure
                    if (tool === 'brush'){
                        // Drawing circle on canvas
                        drawCircle(x2, y2);
                        // Connecting circle on canvas with line
                        drawLine(x, y, x2, y2);
                    }else{
                        /* Restoring figures
                         Putting last image of canvas to make figures empty */
                        context.putImageData(snapshot, 0, 0);

                        // Assigning parameters for figures
                        context.strokeStyle = color;
                        context.lineWidth = size * 2;

                        // Restoring rectangle if tool was rectangle, if else circle, else triangle
                        if (tool === 'rectangle'){
                            // Calling function to draw rectangle
                            rectangle_tool(x, y, x2, y2);
                        }else if(tool == 'circle'){
                            circle_tool(x, y, x2, y2);
                        }else{
                            triangle(x, y, x2, y2);
                        }
                    }
                }
            }
            // Changing appearance of checkbox
            checkbox_fill_img.attr('src', link_checkbox[checkbox_fill_value]);
            // Changing title of checkbox
            checkbox_fill_img.attr('title', title_checkbox[checkbox_fill_value]);

            // Changing showing colors on menu to match colors used in certain moment
            colorInputMain.val(color);
            colorInputSide.val(color_side);
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
checkbox_fill.on('click',function (e) {


    // Operation not on checkbox_fill_value
    checkbox_fill_value = checkbox_fill_value ? false : true;

    // Changing appearance of checkbox
    checkbox_fill_img.attr('src', link_checkbox[checkbox_fill_value]);
    // Changing title of checkbox
    checkbox_fill_img.attr('title', title_checkbox[checkbox_fill_value]);
});

// Swapping main color and with side color
color_change.on('click', function (e){
    // Swapping values in variables
    [color,color_side] = [color_side,color];

    // Displaying new values;
    colorInputMain.val(color);
    colorInputSide.val(color_side);
});


// If user change main color, assign new color to color var
colorInputMain.on('change', function (e) {
    color = $(this).val()
});

// If user change side color, assign new color to color side var
colorInputSide.on('change', function (e) {
    color_side = $(this).val()
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
