# PATHS
import os
class Paths:
    base = os.path.dirname(__file__)
    # data = os.path.join(base, "data/")
    icons = os.path.join(base, "resources/icons")  
    # images = os.path.join(base, "resources/images")  
    settings = os.path.join(base, "config")
    # style = os.path.join(base, "resources/styles.qss")
    threads = os.path.join(base, "models/threads")
    # tests = os.path.join(base, "TEST")
    
    # File loaders
    # @classmethod
    # def datafile(cls, filename):
    #     return os.path.join(cls.data, filename)
    @classmethod
    def icon(cls, filename):
        return os.path.join(cls.icons, filename)
    # @classmethod
    # def image(cls, filename):
    #     return os.path.join(cls.images, filename)
    # @classmethod
    # def model(cls, filename):
    #     return os.path.join(cls.models, filename)
    # @classmethod
    # def setting(cls, filename):
    #     return os.path.join(cls.settings, filename)
    # @classmethod
    # def thread(cls, filename):
    #     return os.path.join(cls.settings, filename)
    # @classmethod
    # def view(cls, filename):
    #     return os.path.join(cls.views, filename)
    # @classmethod
    # def test(cls, filename):
    #     return os.path.join(cls.tests, filename)

CHANNELS_NAMES = [
    "Dev1/ai0",
    "Dev1/ai1",
    "Dev1/ai2",
    "Dev1/ai3",
    "Dev1/ai4",
    "Dev1/ai5",
    "Dev1/ai6",
    "Dev1/ai7",
]

STYLES = {
    "btn": "height: 30px;"
}