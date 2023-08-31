import requests
import util
import time
import os
import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

if __name__ == "__main__":
    logging.info("start SD_painter")
    logging.info(f"sd_url: {util.sd_url()}")
    # check sd_url
    requests.get(url=f"{util.sd_url()}/sdapi/v1/options").json()

    logging.info("check sd_url success")
    logging.info(f"get_task_url: {util.get_task_url()}")
    logging.info(f"submit_task_url: {util.submit_task_url()}")

    # check mount file
    if (
        not os.path.exists("args/")
        or not os.path.exists("outputs/")
        or not os.path.exists(".env")
    ):
        raise Exception("miss mount file")

    while True:
        try:
            task_list = requests.get(util.get_task_url()).json()
        except Exception as e:
            logging.warning(f"get task failed: {e}")
            time.sleep(10)
            continue

        if task_list["message"] != "success":
            logging.warning(f"get invalid task")
            time.sleep(5)
            continue

        if "data" not in task_list:
            timestamp = int(time.time())
            if timestamp % 100 == 0:
                logging.warning(f"task data is empty")
            time.sleep(1)
            continue

        for task_args in task_list["data"]:
            try:
                task = util.args_to_task(task_args)
                start_time = time.time()
                encoded_image = task.process()
                if encoded_image == None:
                    encoded_image == ""
                elapsed = time.time() - start_time
                logging.info(f"process success, spend {elapsed} s")

                submit_payload = {
                    "errorMessage": "",
                    "fileName": f"{task._task_id}" + ".png",
                    "id": f"{task._id}",
                    "mediaType": "image/png",
                    "resultImageBase64": encoded_image,
                }
                result = requests.post(util.submit_task_url(), json=submit_payload)
                logging.info(f"submit {task._task_id}: {result.json()}\n")
            except Exception as e:
                id = task_args["id"]
                logging.warning(f"process failed: {e}")
                submit_payload = {
                    "errorMessage": f"{e}",
                    "fileName": "",
                    "id": f"{id}",
                    "mediaType": "",
                    "resultImageBase64": "",
                }
                result = requests.post(util.submit_task_url(), json=submit_payload)
                logging.info(f"submit {id} error: {result.json()}\n")
