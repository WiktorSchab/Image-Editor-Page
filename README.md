# Image Editor Page

This is a web application built using Flask that allows users to upload images and apply various filters and modifications to them.

## Features

- Upload images (jpg and png formats are supported).
- Apply filters: black & white, real black & white, contour, blur, emboss, color filtering.
- Draw mode: allows users to draw on images and save the modifications.
- Reset changes: revert the image back to the original.
- Download modified images in different formats (jpg, png, tiff, gif).
- Image Management: Users can save, delete, and utilize images stored on the server.
- Login & Registration: Accessing the program necessitates user registration and subsequent login.
- Custom Profile: Users can personalize their profiles by uploading custom profile pictures.


## Examples
### Filters:
- Black & white  
![Black white](https://github.com/WiktorSchab/Image-Editor-Page/assets/73139165/4a86f330-f7cc-4c13-8726-0ca6a1dfa692)  

- Real Black & white  
![RealBlack white](https://github.com/WiktorSchab/Image-Editor-Page/assets/73139165/d564bc6c-e0fa-4ffa-b60c-5b4e543db4b2)  

- Contour  
![Contour](https://github.com/WiktorSchab/Image-Editor-Page/assets/73139165/afc7620b-6f7b-4513-8281-90f95a9c6ef2)  

- Emboss  
![emboss](https://github.com/WiktorSchab/Image-Editor-Page/assets/73139165/d742d08a-a1ab-4c75-8d8d-7e6fd9f56303)  

- Blur  
![Blur](https://github.com/WiktorSchab/Image-Editor-Page/assets/73139165/8e08451f-211a-4f8f-8b33-17aea7901fb8)  

- Colorize  
![colorize](https://github.com/WiktorSchab/Image-Editor-Page/assets/73139165/575ade18-b1f5-4927-a0ec-34a8cd6d5df5)  

- Only white (color filter)   
![white](https://github.com/WiktorSchab/Image-Editor-Page/assets/73139165/7d108d44-cb5d-4c48-b06a-db57228cbf13)  

- Only white, blue, green (color filters)  
![White_Blue_Green](https://github.com/WiktorSchab/Image-Editor-Page/assets/73139165/4a16ed79-1ccc-4092-a1ba-032f28c9100a)  

## Instalation  
### Step 1:  
- Clone repository from github or download files.  
### Step 2:  
- Install libraries in requirements.txt.  
`pip install -r requirements.txt`  
### Step 3:  
- Open colorize/models/link_to_file.txt and with link download files *pts_in_hull.npy*, *colorization_release_v2.caffemodel*, *colorization_deploy_v2.prototxt*.  
### Step 4:
- Create file config.py in db directory.
### Step 5:
- Create two variables in config.py.  
`SQLALCHEMY_DATABASE_URI = *Path_db`  
`Secret_key = *Password`  
*First variable needs to be set according to to https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/    
*Second one needs to be random long bytes or str according to flask creators.    

## First run  
Run main.py to run app, then enter a link that will be given in the console. On first run, there is a need to go to subpage '**/init**'.  
All tables will be created and admin account will be generated. Password to admin will be given in the console.  


## Author
- Wiktor Schab (https://github.com/WiktorSchab)
