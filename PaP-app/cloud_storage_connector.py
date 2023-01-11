from pcloud import PyCloud
import logging
import sys

logger = logging.getLogger("PaP Store")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class CloudStorageConnector:
    cloud = PyCloud

    def __init__(self, email, password, **kwargs):
        self.pc = self.cloud(email, password, **kwargs)

    def read_file_from_cloud(self, path):
        fda = self.pc.file_open(flags=0x0000, path=path)
        data = self.pc.file_read(fd=fda["fd"], count=self.pc.file_size(fd=fda["fd"])["size"])
        self.pc.file_close(fd=fda)
        logger.info(f"Opened {path} from cloud")
        return data

    @staticmethod
    def write_data_to_file(path, data):
        with open(path, "w") as tmp:
            res = tmp.write(data.decode("UNICODE").replace("\r", ""))
        logger.info(f"Wrote data to {path}")
        return res

    def upload_files(self, files, path):
        logger.info(f"Uploaded {files} to {path}")

        return self.pc.uploadfile(files=files, path=path)
