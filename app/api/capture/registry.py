import datetime
import random
import string
from enum import Enum

MAXIMUM_LENGTH = 60

RS = lambda: "".join(
    random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
)


class RegistryStatus(Enum):
    RECORDING = 1
    RECORDED = 2
    CAPTURING = 3
    CAPTURED = 4
    PROCESSING = 5
    DELETING = 6
    READYTOSUBMIT = 7
    SUBMITTED = 8
    FAILEDTOCAPTURE = 9
    FAILEDTORECORD = 10


class Registry:
    Registry = {}

    @staticmethod
    def check_status(key):
        if key in Registry.Registry:
            return Registry.Registry[key].value
        return None

    @staticmethod
    def create_key(user_id, camera_id):
        key = f"{user_id}_{camera_id}_{RS()}"
        return key

    @staticmethod
    def register_recording(key):
        Registry.Registry[key] = RegistryStatus.RECORDING
        return key

    @staticmethod
    def register_capturing(key):
        Registry.Registry[key] = RegistryStatus.CAPTURING
        return key

    @staticmethod
    def register_captured(key):
        if key in Registry.Registry:
            Registry.Registry[key] = RegistryStatus.CAPTURED
        else:
            return None

    @staticmethod
    def register_recorded(key):
        if key in Registry.Registry:
            Registry.Registry[key] = RegistryStatus.RECORDED
        else:
            return None

    @staticmethod
    def set_capture_request_status(key, status):
        for k in RegistryStatus:
            if key == k.name:
                Registry.Registry[key] = k

    @staticmethod
    def register_ready_to_submit(key):
        if key in Registry.Registry:
            Registry.Registry[key] = RegistryStatus.READYTOSUBMIT
        else:
            return None

    @staticmethod
    def register_stop(key):
        if (
            key in Registry.Registry
            and Registry.Registry[key] == RegistryStatus.RECORDING
        ):
            RegistryStatus.RegistryStatus[key] = RegistryStatus.STOPPED
        else:
            return None
