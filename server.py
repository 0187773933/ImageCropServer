#!/usr/bin/env python3
import sys
import uuid
import time
import json
import base64
from pathlib import Path
from pprint import pprint
import tempfile
import shutil

import pytz
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from PIL import Image

from sanic import Sanic
from sanic import Blueprint
from sanic.response import html as sanic_html
from sanic.response import raw as sanic_raw
from sanic.response import json as sanic_json
from sanic.response import file as sanic_file
from sanic.response import file_stream as sanic_file_stream
from sanic.response import stream as sanic_stream
from sanic.request import Request

time_zone = pytz.timezone( "US/Eastern" )
app = Sanic( __name__ )

@app.route( "/" , methods=[ "GET" ] )
async def home( request: Request ):
	return sanic_html( f'''<!DOCTYPE html>
<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>Image Crop Server</title>
</head>
<body>
	<h1>Upload Image and Crop at Bounding Box</h1>
	<h3>Use <a href="https://www.photopea.com">PhotoPea</a> Info Button to View Mouse Pixel Coordinate Location</h3>
	<form id="our-form" enctype="multipart/form-data" action="/crop" method="POST" onsubmit="on_submit();">
		<input type="file" id="powerpoint" name="file"><br><br>
		<span>Top-Left X-Coordinate</span>&nbsp&nbsp<input type="text" id="x1" name="x1" placeholder="0"><br></br>
		<span>Top-Left Y-Coordinate</span>&nbsp&nbsp<input type="text" id="y1" name="y1" placeholder="0"><br></br>
		<span>Bottom-Right X-Coordinate</span>&nbsp&nbsp<input type="text" id="x2" name="x2" placeholder="0"><br></br>
		<span>Bottom-Right Y-Coordinate</span>&nbsp&nbsp<input type="text" id="y2" name="y2" placeholder="0"><br></br>
		<input type="submit" value="Upload">
	</form>
	<br><br>
	<center><img src="https://39363.org/IMAGE_BUCKET/1647623386468-839855800.png" style="zoom:67%;"/></center>
	<script type="text/javascript">
		function on_submit() {{
			let form = document.getElementById( "our-form" );
			let x1 = form.elements[ "x1" ].value || "0";
			let y1 = form.elements[ "y1" ].value || "0";
			let x2 = form.elements[ "x2" ].value || "0";
			let y2 = form.elements[ "y2" ].value || "0";
			x1 = x1.trim();
			y1 = y1.trim();
			x2 = x2.trim();
			y2 = y2.trim();
			let form_action = "/crop/" + x1 + "/" + y1 + "/" + x2 + "/" + y2;
			console.log( form_action );
			form.action = form_action;
			form.submit();
		}}
	</script>
</body>
</html>''')

def convert_photoshop_bounding_box_to_pil_crop_bounding_box( photoshop_bounding_box , input_image_size ):
	try:
		if "bottom_left" in photoshop_bounding_box and "top_right" in photoshop_bounding_box:
			return False
		elif "top_left" in photoshop_bounding_box and "bottom_right" in photoshop_bounding_box:
			# https://github.com/brcosm/Image-Cropper/blob/master/crop.py
			x1 = photoshop_bounding_box[ "top_left" ][ 0 ]
			y1 = photoshop_bounding_box[ "top_left" ][ 1 ]
			x_distance = ( photoshop_bounding_box[ "bottom_right" ][ 0 ] - x1 )
			y_distance = ( photoshop_bounding_box[ "bottom_right" ][ 1 ] - y1 )
			origin = ( x1 , y1 )
			x2 = min( x_distance , input_image_size[ 0 ] )
			y2 = min( y_distance , input_image_size[ 1 ] )
			size = ( x2 , y2 )
			region = origin + ( origin[0] + size[0] , origin[1] + size[1] )
			return region
		else:
			return False
	except Exception as e:
		print( e )
		return False

@app.post( "/crop/<x1:str>/<y1:str>/<x2:str>/<y2:str>" , stream=False )
async def crop( request: Request , x1:str , y1:str , x2:str , y2:str ):
	try:
		# print( request.files[ "file" ][ 0 ].name )
		# print( request.files[ "file" ][ 0 ].type )
		# print( x1 , y1 , x2 , y2 )
		with tempfile.TemporaryDirectory() as temp_dir:
			temp_dir_posix = Path( temp_dir )
			input_file_path = temp_dir_posix.joinpath( request.files[ "file" ][ 0 ].name )
			print( "Uploading Test File" )
			with open( input_file_path , 'wb' ) as f:
				f.write( request.files[ "file" ][ 0 ].body )

			output_image_path = temp_dir_posix.joinpath( f"{input_file_path.stem} - CROPPED{input_file_path.suffix}" )
			input_image = Image.open( str( input_file_path ) )
			# print( input_image.size )
			# input_image.show()
			pil_cropped_bounding_box = convert_photoshop_bounding_box_to_pil_crop_bounding_box({
				"top_left": [ int( x1 ) , int( y1 ) ] ,
				"bottom_right": [ int( x2 ) , int( y2 ) ]
			} , input_image.size )
			if pil_cropped_bounding_box == False:
				return sanic_json( dict( failed="couldn't crop image" ) , status=200 )
			cropped_image = input_image.crop( pil_cropped_bounding_box )
			# cropped_image.show()
			cropped_image.save( str( output_image_path ) )
			return await sanic_file(
				str( output_image_path ) ,
				mime_type=request.files[ "file" ][ 0 ].type ,
				filename=output_image_path.name
			)
	except Exception as e:
		print( e )
		return sanic_json( dict( failed=str( e ) ) , status=200 )

if __name__ == "__main__":
	app.run( host="0.0.0.0" , port="9375" )