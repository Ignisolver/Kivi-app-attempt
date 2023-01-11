from kivy_garden.zbarcam import ZBarCam

import PIL

from kivy.properties import ListProperty
from pyzbar import pyzbar
from kivy_garden.zbarcam.utils import fix_android_image
# from kivy.uix.button import Button
# from kivy.metrics import dp

class MyZBarCam(ZBarCam):
    """
        Widget that use the Camera and zbar to detect qrcode.
        When found, the `codes` will be updated.
    """

    resolution = ListProperty([480, 640])

    symbols = ""

    def __init__(self, **kwargs):
        self.register_event_type('on_bar_found')
        super(MyZBarCam, self).__init__(**kwargs)

    def _setup(self):
        """
        Postpones some setup tasks that require self.ids dictionary.
        """
        self._remove_shoot_button()

        # `self.xcamera._camera` instance may not be available if e.g.
        # the `CAMERA` permission is not granted
        self.xcamera.bind(on_camera_ready=self._on_camera_ready)
        # camera may still be ready before we bind the event
        if self.xcamera._camera is not None:
            self._on_camera_ready(self.xcamera)


    def _on_texture(self, instance):

        if self.children[0].state == "down":
            self.symbols=self._detect_qrcode_frame(
                texture=instance.texture, code_types=self.code_types)
            if self.symbols:
                self.dispatch('on_bar_found')

    def _detect_qrcode_frame(self, texture, code_types):
        image_data = texture.pixels
        size = texture.size
        # Fix for mode mismatch between texture.colorfmt and data returned by
        # texture.pixels. texture.pixels always returns RGBA, so that should
        # be passed to PIL no matter what texture.colorfmt returns. refs:
        # https://github.com/AndreMiras/garden.zbarcam/issues/41
        pil_image = PIL.Image.frombytes(mode='RGBA', size=size,
                                        data=image_data)
        pil_image = fix_android_image(pil_image)
        symbolss = ""
        codes = pyzbar.decode(pil_image, symbols=code_types)

        for code in codes:
            symbolss = ZBarCam.Symbol(type=code.type, data=code.data)

            if symbolss.type == "EAN13":
                symbolss = symbolss.data.decode("utf-8")
                # symbolss = EAN13_to_name(symbolss)
            else:
                symbolss = symbolss.data.decode("utf-8")

        return symbolss

    def on_bar_found(self):
        pass


