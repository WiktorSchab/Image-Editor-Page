/* drawing functions */
if((window.location.href).includes('http://127.0.0.1:5000/draw_mode/')){
    /* assigning object from html to variables */
    var canvas = $('#canvas')[0];
    var buttonClear = $('#buttonClear')[0];
    var sizeInput = $('#size')[0];
    var colorInput = $('#color_tool')[0];

    /* creating context to allow user drawing and assigning it to context var*/
    var context = canvas.getContext("2d");

    /*  setting default variables */
    var isMouseDown = false;
    var color = "#000";
    var size = 10;
    var x,y;

    /* placing the circles in the place where the pressed mouse is */
    function drawCircle(x,y){
        /* starting drawing path */
        context.beginPath()

        /* drawing circle with set color and size. Color is filling circle */
        context.arc(x, y, size, 0, Math.PI * 2);
        context.fillStyle = color;
        context.fill();
    }

    /* drawing line between circles (that appear when user draw fast)*/
    function drawLine(x1, y1, x2, y2){
        /* starting drawing path */
        context.beginPath();

        /* setting start point */
        context.moveTo(x1,y1);

        /* setting line from start point to point with x2, y2 cords */
        context.lineTo(x2,y2);

        /* setting properties of drawing */
        context.strokeStyle = color;
        context.lineWidth = size * 2;

        /* drawing line */
        context.stroke();
    }

    /* function that assign position of mouse to x,y if user click */
    canvas.addEventListener("mousedown", function (e){
        isMouseDown = true;

        /* setting mouse position to variable */
        x = e.offsetX;
        y = e.offsetY;
    });

    /* drawing line that follow user mouse move */
    canvas.addEventListener("mousemove", function (e){
        /* returning from funct if user stop pressing mouse */
        if (!isMouseDown) return;

        /* assigning actual position of mouse to variables */
        var x2 = e.offsetX;
        var y2 = e.offsetY;

        /* function to create circle in actual mouse position */
        drawCircle(x2,y2);
        /* function that creates line between old and new mouse position*/
        drawLine(x, y ,x2, y2);

        /* assigning actual position of mouse to x and y, so they can be used as old one in next function call */
        x = x2;
        y = y2;
    });

    /* stopping drawing if user stop pressing mouse */
    canvas.addEventListener("mouseup", function (e){
        isMouseDown = false;

        /* setting variables that holds position of mouse to null */
        x = null;
        y = null;
    })

    /* buttons */
    /* cleaning button */
    buttonClear.addEventListener("click", function (e){
       /* cleaning canvas from everything */
       context.clearRect(0, 0, canvas.width, canvas.height);

       /* loading image as background again */
       load_image();
    });

    /* size of tool */
    sizeInput.addEventListener("change", function (e){
        /* overwriting variable that have size of drawn line */
        size = $('#size').val();
    });

    /* color of tool */
    colorInput.addEventListener("change", function (e){
        /* overwriting variable that have color of drawn line */
        color = $('#color_tool').val();
    });
}