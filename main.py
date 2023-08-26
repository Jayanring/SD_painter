import requests
import util
import time
import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

if __name__ == '__main__':
    logging.info('start SD_painter')
    logging.info(f'sd_url: {util.sd_url()}')
    logging.info(f'get_task_url: {util.get_task_url()}')
    logging.info(f'submit_task_url: {util.submit_task_url()}')
    while True:
        try:
            task_list = requests.get(util.get_task_url()).json()
        except Exception as e:
            logging.warn(f'get task failed: {e}')
            time.sleep(10)
            continue

        if task_list['message'] != 'success':
            logging.warn(f'get invalid task')
            time.sleep(5)
            continue

        if 'data' not in task_list:
            logging.warn(f'task no data')
            time.sleep(1)
            continue

        for task_args in task_list['data']:
            try:
                task = util.args_to_task(task_args)
                start_time = time.time()
                encoded_image = task.process()
                elapsed = time.time() - start_time
                logging.info(f"process success, spend {elapsed} s")

                submit_payload = {'errorMessage': '', 'fileName': f'{task._task_id}',
                                  'id': f'{task._id}', 'mediaType': 'png', 'resultImageBase64': encoded_image}
                result = requests.post(
                    util.submit_task_url(), json=submit_payload)
                logging.info(f'submit {task._task_id}: {result.json()}\n')
            except Exception as e:
                logging.warn(f'process failed: {e}')
                submit_payload = {'errorMessage': f'{e}', 'fileName': '',
                                  'id': f'{task._id}', 'mediaType': 'png', 'resultImageBase64': ''}
                result = requests.post(
                    util.submit_task_url(), json=submit_payload)
                logging.info(
                    f'submit {task._task_id} error: {result.json()}\n')

        break
