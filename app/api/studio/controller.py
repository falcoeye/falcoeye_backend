
from flask_jwt_extended import jwt_required,get_jwt_identity
from flask_restx import Resource

from .dto import MediaDto
from .service import StudioService

api = MediaDto.api
vid_resp = MediaDto.video_resp
img_resp = MediaDto.image_resp


@api.route("/")
class StudioGetMedia(Resource):
    @api.doc(
        "Get a user media",
        responses={
            200: ("User media successfully sent"),
            404: "User not found!",
        },
        security="apikey"
    )
    @jwt_required()
    def get(self):
        """Get a specific user's media by their username"""
        current_user_id = get_jwt_identity()
        return StudioService.get_media(current_user_id)
    
@api.route("/delete_image <string:name>")
class StudioDeleteImage(Resource):
    @api.doc(
        "Delete a user image",
        responses={
            200: ("User image successfully deleted", img_resp),
            404: "User not found!",
        },
        security="apikey"
    )
    @jwt_required()
    def post(self,name):
        """Delete a specific user's image by its name"""
        current_user_id = get_jwt_identity()
        return StudioService.delete_image(current_user_id,name)

@api.route("/add_image <string:name> <int:camera> <string:note> <string:tags> <int:workflow>")
class StudioAddImage(Resource):
    @api.doc(
        "Get a user media",
        responses={
            200: ("Image successfully added", img_resp),
            404: "User not found!",
        },
        security="apikey"
    )
    @jwt_required()
    def post(self,name,camera,note,tags,workflow):
        """Add a user's image"""
        current_user_id = get_jwt_identity()
        return StudioService.add_image(current_user_id,name,camera,note,tags,workflow)
    


