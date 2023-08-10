// setting size of canvas to size of image and using image as background */
function load_image(){
    var canvas = $('#canvas')[0];

    // creating new image obj //
    var img = new Image();

    // setting source of image to file given by user with use of Flask function to locate img //
    img.src = "{{url_for('static',filename='download/modified/'+file_name)}}";

    // waiting img to fully load
    img.onload = function() {
        // declaring original proportion of image to ratio variable
        var ratio = img.height / img.width;

        // setting size of image with height 512 and width that its 512/original image ratio
        var height = 512;
        var width  = height / ratio;

        // setting size of canvas as the same size as image have
        canvas.width = width;
        canvas.height = height;

        // getting 2d render of context of canvas
        var ctx = canvas.getContext('2d');

        // Drawing loaded render of given image
        ctx.drawImage(img, 0, 0, width, height);
    };
};

// loading canvas with img background if page is generated
$(document).ready(function() {
    load_image();
});


// drawing functions
if((window.location.href).includes('http://127.0.0.1:5000/draw_mode/')){
    // assigning object from html to variables
    var canvas = $('#canvas');
    var buttonClear = $('#buttonClear');
    var sizeInput = $('.size');
    var colorInput = $('#color_tool');

    // creating context to allow user drawing and assigning it to context var
    var context = $('#canvas')[0].getContext("2d");

    //  setting default variables
    var isMouseDown = false;
    var color = "#000";
    var size = 10;
    var x,y;


    // placing the circles in the place where the pressed mouse is
    function drawCircle(x,y){
        // starting drawing path
        context.beginPath()

        // drawing circle with set color and size. Color is filling circle
        context.arc(x, y, size, 0, Math.PI * 2);
        context.fillStyle = color;
        context.fill();
    }

    // drawing line between circles (that appear when user draw fast)
    function drawLine(x1, y1, x2, y2){
        // starting drawing path
        context.beginPath();

        // setting start point
        context.moveTo(x1,y1);

        // setting line from start point to point with x2, y2 cords
        context.lineTo(x2,y2);

        // setting properties of drawing
        context.strokeStyle = color;
        context.lineWidth = size * 2;

        // drawing line
        context.stroke();
    }

    // function that assign position of mouse to x,y if user click
    canvas.on("mousedown", function (e){
        isMouseDown = true;

        // setting mouse position to variable
        x = e.offsetX;
        y = e.offsetY;
    });

    // drawing line that follow user mouse move
    canvas.on("mousemove", function (e){
        // returning from funct if user stop pressing mouse
        if (!isMouseDown) return;

        // assigning actual position of mouse to variables
        var x2 = e.offsetX;
        var y2 = e.offsetY;

        // function to create circle in actual mouse position
        drawCircle(x2,y2);
        // function that creates line between old and new mouse position
        drawLine(x, y ,x2, y2);

        // assigning actual position of mouse to x and y, so they can be used as old one in next function call
        x = x2;
        y = y2;
    });

    /* stopping drawing if user stop pressing mouse */
    canvas.on("mouseup", function (e){
        isMouseDown = false;

        /* setting variables that holds position of mouse to null */
        x = null;
        y = null;
    })

    // buttons
    // cleaning button
    buttonClear.on("click", function (e){
       // cleaning canvas from everything
       context.clearRect(0, 0, canvas.width, canvas.height);

       // loading image as background again
       load_image();
    });

    // size of tool
    sizeInput.on("input", function() {
        size = $(this).val();

        // making sure that user dont enter value higher than max
        if (size > 20){
            size = 20
        }

        // changing displaying size on input number and input change
        $(".size").val(size);
    });

    // color of tool
    colorInput.on("change", function (e){
        color = $(this).val()
    });
}