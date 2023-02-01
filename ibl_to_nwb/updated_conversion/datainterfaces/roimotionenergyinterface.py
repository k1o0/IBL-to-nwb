"""Data Interface for the special data type of ROI Motion Energy."""
from one.api import ONE
from pydantic import DirectoryPath
from pynwb import TimeSeries, H5DataIO
from neuroconv.basedatainterface import BaseDataInterface

class RoiMotionEnergyInterface(BaseDataInterface):
    def __init__(self, session: str, cache_folder: DirectoryPath, camera_name: str):
        self.session = session
        self.cache_folder = cache_folder
        self.camera_name = camera_name

    def run_conversion(self, nwbfile, metadata: dict):
        one = ONE(
            base_url='https://openalyx.internationalbrainlab.org',
            password='international',
            silent=True,
            cache_folder=self.cache_folder,
        )

        left_right_or_body = self.camera_name[:5].rstrip("C")

        camera_data = one.load_object(id=self.session, obj=self.camera_name, collection="alf")
        motion_energy_video_region = one.load_object(
            id=self.session, obj=f"{left_right_or_body}ROIMotionEnergy", collection="alf"
        )

        width, height, x, y = motion_energy_video_region["position"]

        description = f"""
        Motion energy calculated for a region of the {left_right_or_body} camera video that is {width} pixels wide, {height} pixels tall, and the top-left corner of the region is the pixel ({x}, {y}).

        CAUTION: As each software will load the video in a different orientation, the ROI might need to be adapted.
        For example, when loading the video with cv2 in Python, x and y axes are flipped from the convention used above.
        The region then becomes [{y}:{y+height}, {x}:{x+width}].
        """

        motion_energy_series = TimeSeries(
            name=f"{left_right_or_body.capitalize()}CameraMotionEnergy",
            description=description,
            data=H5DataIO(camera_data["ROIMotionEnergy"]),
            timestamps=H5DataIO(camera_data["times"]),
            unit="a.u.",
        )
        behavior_module = nwbfile.create_processing_module(name="behavior", description="processed behavioral data")
        behavior_module.add(motion_energy_series)
