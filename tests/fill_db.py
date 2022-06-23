import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, f"{basedir}/../")
import datetime

from flask import Flask

from app.dbmodels.ai import AIModel, Analysis, Dataset, Workflow
from app.dbmodels.camera import Camera  # , CameraManufacturer, Streamer
from app.dbmodels.studio import Image, Video
from app.dbmodels.user import User


def falcoeye():
    if not (user := User.query.filter_by(username="falcoeye").first()):
        user = User(
            email="falcoeye@falcoeye.com", password="falcoeye1234", username="falcoeye"
        )
        db.session.add(user)
        db.session.commit()
    return user


def kaust():
    if not (user := User.query.filter_by(username="kaust").first()):
        user = User(email="kaust@kaust.edu", password="kaust1234", username="kaust")
        db.session.add(user)
        db.session.commit()
    return user


def neom():
    if not (user := User.query.filter_by(username="neom").first()):
        user = User(email="neom@neom.edu", password="neom1234", username="neom")
        db.session.add(user)
        db.session.commit()
    return user


# def ViewIntoTheBlue():
#     if not (
#         manufacturer := CameraManufacturer.query.filter_by(
#             name="ViewIntoTheBlue"
#         ).first()
#     ):
#         manufacturer = CameraManufacturer(name="ViewIntoTheBlue")
#         db.session.add(manufacturer)
#         db.session.commit()
#     return manufacturer


# def HikVision():
#     if not (
#         manufacturer := CameraManufacturer.query.filter_by(name="Hikvision").first()
#     ):
#         manufacturer = CameraManufacturer(name="Hikvision")
#         db.session.add(manufacturer)
#         db.session.commit()
#     return manufacturer


# def youtube():
#     if not (streamer := Streamer.query.filter_by(name="youtube").first()):
#         streamer = Streamer(name="youtube")
#         db.session.add(streamer)
#         db.session.commit()
#     return streamer


# def angelcam():
#     if not (streamer := Streamer.query.filter_by(name="angelcam").first()):
#         streamer = Streamer(name="angelcam")
#         db.session.add(streamer)
#         db.session.commit()
#     return streamer


def harbour_camera(user, streamer, manufacturer):
    if not (
        cam := Camera.query.filter_by(name="Harbour Village Bonaire Coral Reef").first()
    ):
        cam = Camera(
            name="Harbour Village Bonaire Coral Reef",
            status="RUNNING",
            # manufacturer_id=manufacturer.id,
            # streamer_id=streamer.id,
            owner_id=user.id,
            url="https://www.youtube.com/watch?v=tk-qJJbdOh4",
            resolution_x=1920,
            resolution_y=1080,
            latitude=28.011488949141786,
            longitude=34.99277350675658,
        )
        db.session.add(cam)
        db.session.commit()
    return cam


def kaust_camera(user, streamer, manufacturer):
    if not (cam := Camera.query.filter_by(name="KAUST ViewIntoTheBlue Camera").first()):
        cam = Camera(
            name="KAUST ViewIntoTheBlue Camera",
            status="RUNNING",
            # manufacturer_id=manufacturer.id,
            # streamer_id=streamer.id,
            owner_id=user.id,
            url="https://v.angelcam.com/iframe?v=16lb6045r4",
            latitude=22.307636,
            longitude=39.101841,
            resolution_x=1920,
            resolution_y=1080,
        )
        db.session.add(cam)
        db.session.commit()
    return cam


def neom_road_camera(user, streamer, manufacturer):
    if not (cam := Camera.query.filter_by(name="NEOM ROAD CAM").first()):
        cam = Camera(
            name="NEOM ROAD CAM",
            status="RUNNING",
            # manufacturer_id=manufacturer.id,
            # streamer_id=streamer.id,
            owner_id=user.id,
            url="http://x.x.x.x",
            latitude=26.359954095563015,
            longitude=36.256285119283696,
            resolution_x=1920,
            resolution_y=1080,
        )
        db.session.add(cam)
        db.session.commit()
    return cam


def kaust_images(user, camera):
    import glob

    images = glob.glob(f"{basedir}/../../falcoeye_frontend/materials/images/kaust*")
    data = []
    notes = ["redbreasted", "triggerfish", "parrotfish", "longnose"]
    for im, n in zip(images, notes):
        image = Image(
            user=user.id,
            camera_id=camera.id,
            tags="fish, kaust port",
            note=n,
            url=f"../images/{im.split('/')[-1]}",
            thumbnail_url=im,
        )
        db.session.add(image)
        db.session.commit()


def lutjanus_video(user, camera):
    video = Video(
        user=user.id,
        camera_id=camera.id,
        tags="lutjanis, kaust, port",
        note="Group of lutjanis fish",
        duration=7,
        url="../videos/lutjanis.mov",
    )
    db.session.add(video)
    db.session.commit()


def vehicles_video(user, camera):
    video = Video(
        user=user.id,
        camera_id=camera.id,
        tags="road, 4 wheels, truck",
        note="Heavy traffic in highway",
        duration=29,
        url="../videos/vehicles.mp4",
    )
    db.session.add(video)
    db.session.commit()


def arabian_angelfish_video(user, camera):
    video = Video(
        user=user.id,
        camera_id=camera.id,
        tags="arabian anglefish, kaust, port",
        note="Beautiful arabian anglefish visits kaust",
        duration=46,
        url="../videos/arabian_angelfish.mov",
        thumbnail_url="../videos/arabian_angelfish_thumbnail.jpg",
    )
    db.session.add(video)
    db.session.commit()


def fourtythree_dataset(user):
    if not (dataset := Dataset.query.filter_by(name="Fourty Three Fish").first()):
        dataset = Dataset(
            name="Fourty Three Fish",
            creator=user.id,
            annotation_type="Bounding box",
            image_width=1920,
            image_height=1080,
            size_type="unified",
        )
        db.session.add(dataset)
        db.session.commit()
    return dataset


def vehicleseye_model(user):
    if not (model := AIModel.query.filter_by(name="VehicleEye").first()):
        model = AIModel(
            name="VehicleEye",
            creator=user.id,
            publish_date=datetime.datetime.now(),
            archeticture="yolov5",
            backbone=None,
            dataset_id=None,
            technology="torch",
            speed=5,
        )
        db.session.add(model)
        db.session.commit()
    return model


def fourtythree_model(user, dataset):
    if not (model := AIModel.query.filter_by(name="FourtyThreeFish").first()):
        model = AIModel(
            name="FourtyThreeFish",
            creator=user.id,
            publish_date=datetime.datetime.now(),
            archeticture="frcnn",
            backbone="resnet50",
            dataset_id=dataset.id,
            technology="tensorflow",
            speed=1,
        )
        db.session.add(model)
        db.session.commit()
    return model


def fishfinder_model(user, dataset):
    if not (model := AIModel.query.filter_by(name="FishFinder").first()):
        model = AIModel(
            name="FishFinder",
            creator=user.id,
            publish_date=datetime.datetime.now(),
            archeticture="frcnn",
            backbone="resnet50",
            dataset_id=dataset.id,
            technology="tensorflow",
            speed=1,
        )
        db.session.add(model)
        db.session.commit()
    return model


def vehicle_count_workflow(user, ai_model):
    if not (workflow := Workflow.query.filter_by(name="VehicleEye").first()):
        workflow = Workflow(
            name="VehicleEye",
            creator=user.id,
            publish_date=datetime.datetime.now(),
            aimodel_id=ai_model.id,
            usedfor="""
            Monitoring vehicle crowd in certain road over several time intervals to compare
            the crowd over daytime, days, weeks, months and seasons. When crossed with other
            data (weather, events,..etc) the outcome can be used to detect driver behavior over different conditions
            """,
            consideration=""" -   Works for 4 types of vehicles [car|bus|truck|2-wheels]
                -   Works during the day
                -	A single vehicle can be counted more than once
                -	Depending on the interval, vehicles might not be observed and counted
                -	Vehicle must be within close proximity
                -	Visibility might affect the results
            """,
            assumption="""
            For the stream, depending on the interval, the sampling rate is going
            to be a frame per second or slower.
            """,
            accepted_media="Video|Camera",
            results_description="""
            Line chart shows number of occurrences for each category in the sight of view per predicted frame
            User can aggregate results by second, minutes, hour and day
            Aggregation includes sum and average

            Each frame will have relative (video) or actual (stream) timestamp.

            For the video, the result will be published after the full prediction is completed
            For the stream, the results will be published actively
            """,
            results_type="csv",
            thumbnail_url="../workflows/vehicle_count_workflow.jpg",
        )
        db.session.add(workflow)
        db.session.commit()
    return workflow


def fish_catcher_workflow(user, ai_model):
    if not (workflow := Workflow.query.filter_by(name="FishCatcher").first()):
        workflow = Workflow(
            name="FishCatcher",
            creator=user.id,
            publish_date=datetime.datetime.now(),
            aimodel_id=ai_model.id,
            usedfor="""
            This model can be used to monitor and catch 43 types of common coral fish
            when the appear across the sight view of the camera. These fish have unique
            behaviors which are still under research by marine biologist.
            """,
            consideration=""" - The model detects one type of fish in each run
                - In the stream option, the fish must stay at sight of the camera for enough time
                to trigger the recording
                - Fish must be within close proximity
                - Underwater visibility might affect the results
            """,
            assumption="""
            For the stream, depending on the interval, the sampling rate is going
            to be a frame per second or slower.
            """,
            accepted_media="Video|Camera",
            results_description="""
            split & end of video: multiple files for each segment
            split & first occurrence: single segment cut
            merge: single files combining all appearances
            Each segment must have the relative (video) or actual (stream) timestamp.
            """,
            results_type="videos",
            thumbnail_url="../workflows/fish_catcher_workflow.jpg",
        )
        db.session.add(workflow)
        db.session.commit()
    return workflow


def fish_counter_workflow(user, ai_model):
    if not (workflow := Workflow.query.filter_by(name="FishCounter").first()):
        workflow = Workflow(
            name="FishCounter",
            creator=user.id,
            publish_date=datetime.datetime.now(),
            aimodel_id=ai_model.id,
            usedfor="""
            Monitoring fish crowd in certain location over several time intervals to
            compare the crowd over daytime, days, weeks, months and seasons. When crossed with
            maritime data (weather, water condition and quality) the outcome can be used to detect
            fish behavior over different conditions
            """,
            consideration=""" -	A single fish can be counted more than once
                -	Depending on the interval, fish might not be observed and counted
                -	Fish must be within close proximity
                -	Underwater visibility might affect the results
            """,
            assumption="""
            For the stream, depending on the interval, the sampling rate is going
            to be a frame per second or slower.""",
            accepted_media="Video|Camera",
            results_description="""
            Line chart shows number of fish in the sight of view per predicted frame
            User can aggregate results by second, minutes, hour and day
            Aggregation includes sum and average

            Each frame will have relative (video) or actual (stream) timestamp.

            For the video, the result will be published after the full prediction is completed

            For the stream, the results will be published actively
            """,
            results_type="csv",
            thumbnail_url="../workflows/fish_counter_workflow.jpg",
        )
        db.session.add(workflow)
        db.session.commit()
    return workflow


def count_fish_harbour_camera(user, workflow):
    if not (
        analysis := Analysis.query.filter_by(name="count fish harbour camera").first()
    ):
        analysis = Analysis(
            name="count fish harbour camera",
            creator=user.id,
            workflow_id=workflow.id,
            status="completed",
            results_path="../analysis/count_fish_harbour_camera/",
            thumbnail_url="../workflows/fish_counter_workflow.jpg",
        )
        db.session.add(analysis)
        db.session.commit()
    return analysis


def count_fish_lutjanis_video(user, workflow):
    if not (
        analysis := Analysis.query.filter_by(name="count fish lutjanis video").first()
    ):
        analysis = Analysis(
            name="count fish lutjanis video",
            creator=user.id,
            workflow_id=workflow.id,
            status="completed",
            results_path="../analysis/count_fish_lutjanus_video/",
            thumbnail_url="../workflows/fish_counter_workflow.jpg",
        )
        db.session.add(analysis)
        db.session.commit()
    return analysis


def count_vehicles(user, workflow):
    if not (analysis := Analysis.query.filter_by(name="count vehicles").first()):
        analysis = Analysis(
            name="count vehicles",
            creator=user.id,
            workflow_id=workflow.id,
            status="completed",
            results_path="../analysis/count_vehicles/",
            thumbnail_url="../workflows/vehicle_count_workflow.jpg",
        )
        db.session.add(analysis)
        db.session.commit()
    return analysis


def find_arabian_angelfish(user, workflow):
    if not (
        analysis := Analysis.query.filter_by(name="find arabian angelfish").first()
    ):
        analysis = Analysis(
            name="find arabian angelfish",
            creator=user.id,
            workflow_id=workflow.id,
            status="completed",
            results_path="../analysis/find_arabian_angelfish/",
            thumbnail_url="../workflows/fish_catcher_workflow.jpg",
        )
        db.session.add(analysis)
        db.session.commit()
    return analysis


# def run():

#     fe = falcoeye()
#     kuser = kaust()
#     nuser = neom()
#     print("users added")

#     #yo = youtube()
#     #angl = angelcam()

#     #vie = ViewIntoTheBlue()
#     #hk = HikVision()

#     harbour = harbour_camera(nuser, yo, vie)
#     kcamera = kaust_camera(kuser, angl, vie)
#     ncamera = neom_road_camera(nuser, angl, hk)

#     kaust_images(kuser, kcamera)
#     # lutjanus_video(kuser,kcamera)
#     # arabian_angelfish_video(kuser,kcamera)
#     # vehicles_video(nuser,hk)

#     ds = fourtythree_dataset(fe)

#     vm = fourtythree_model(fe, ds)
#     fsh = fishfinder_model(fe, ds)
#     ve = vehicleseye_model(fe)

#     wf1 = vehicle_count_workflow(fe, ve)
#     wf2 = fish_catcher_workflow(fe, vm)
#     wf3 = fish_counter_workflow(fe, fsh)

#     count_fish_harbour_camera(kuser, wf3)
#     count_fish_lutjanis_video(kuser, wf3)
#     count_vehicles(nuser, wf1)
#     find_arabian_angelfish(kuser, wf2)


if __name__ == "__main__":
    from flask_sqlalchemy import SQLAlchemy

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        basedir, "../data-dev.sqlite"
    )
    db = SQLAlchemy(app)
    with app.app_context():
        db.create_all()
        # run()
