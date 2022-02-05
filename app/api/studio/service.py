from app.dbmodels.studio import DBVideo as Video
from app.dbmodels.studio import DBImage as Image
from app.dbmodels.schemas import ImageSchema
from app import db
from app.utils import err_resp
from app.utils import internal_err_resp
from app.utils import message
from flask import current_app
from datetime import datetime

image_schema = ImageSchema()

class StudioService:
	@staticmethod
	def get_user_media(userid):
		"""Get user data by username"""
		videos = Video.query.filter_by(user=userid)
		images = Image.query.filter_by(user=userid)

		from .utils import load_video_short_data, load_image_short_data

		try:
			video_data = [load_video_short_data(v) for v in videos]
			image_data = [load_image_short_data(i) for i in images]
			media_data = videos + image_data
			
			resp = message(True, "User data sent")
			resp["media"] = media_data
			return resp, 200

		except Exception as error:
			current_app.logger.error(error)
			return internal_err_resp()

	@staticmethod
	def add_image(userid,name,camera,note,tags,workflow):
		# Check if the email is taken
		if Image.query.filter_by(user=userid,name=name).first() is not None:
			return err_resp("Name is already being used.", "name_taken", 403)
		try:
			new_image = Image(
					user=userid,
					name=name,
					camera=camera,
					tags=tags,
					note=note,
					workflow=workflow,
					creation_datetime=datetime.utcnow())
			db.session.add(new_image)
			db.session.flush()
			db.session.commit()

			img_info = image_schema.dump(new_image)
			resp = message(True, "Image has been added.")
			resp["image"] = img_info
			return resp, 201
		except Exception as error:
			current_app.logger.error(error)
			return internal_err_resp()

	@staticmethod
	def delete_image(userid,name):
		# Check if the email is taken
		
		if (img := Image.query.filter_by(user=userid,name=name).first()) is None:
			return err_resp("Image doesn't exist", "image_not_exist", 403)
		print(img)
		try:
			img_info = image_schema.dump(img)
			resp = message(True, "Image has been deleted.")
			resp["image"] = img_info

			db.session.delete(img)
			
			db.session.flush()
			db.session.commit()
			print(resp)
			return resp, 201
		except Exception as error:
			raise
			current_app.logger.error(error)
			return internal_err_resp()

		

