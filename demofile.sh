
mkdir templates 
python3 scaffold.py user username password email phone country_id:references pic:file
python3 scaffold.py country name
python3 scaffold.py scores user_id time_signature key_signature mytext:staff pic
python3 scaffold.py mysunglassesphoto  pic:sunglasses user_id
python3 scaffold.py maquillephoto  pic:maquille user_id
python3 scaffold.py reconnaitphoto user_id:recognize_face pic:file face_recognized
