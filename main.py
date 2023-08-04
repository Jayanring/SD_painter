import queue
import threading
import util
import logging
from flask import Flask, request, jsonify


class ThreadSafeCounter:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            self.count += 1
            return self.count

    def set_count(self, count):
        with self.lock:
            self.count = count

    def get_count(self):
        with self.lock:
            return self.count


class TaskQueue:
    def __init__(self):
        self.queue = queue.Queue()
        self.task_seq = ThreadSafeCounter()
        seq = util.get_history_seq()

        app.logger.info(f'start from seq: {seq}')

        self.task_seq.set_count(seq)
        self.done = seq

    def insert_task(self, task):
        seq = self.task_seq.increment()
        task._task_id = str(seq) + '_' + task._task_id

        app.logger.info(
            f'insert task: {task._task_id}, mode: {task._mode}, done seq: {self.done}')

        self.queue.put(task)
        return task._task_id

    def get_task_result(self, task_id):
        seq = int(task_id.split('_')[0])
        processing = self.done + 1
        if seq == processing:
            app.logger.info(f'get task: {task_id}, processing')
            return f'processing'
        elif seq > processing:
            app.logger.info(
                f'get task: {task_id}, {seq - processing} tasks to process')
            return f'in queue {seq - processing}'
        else:
            app.logger.info(f'get task: {task_id}, success')
            path = f'history_outputs/{task_id}.png'
            encoded_image = util.encode_image(path)
            return encoded_image

    def worker(self):
        while True:
            task = self.queue.get()
            app.logger.info(
                f'process task: {task._task_id}, mode: {task._mode}')
            task.process()
            self.done = int(task._task_id.split('_')[0])
            self.queue.task_done()


app = Flask(__name__)


@app.route('/insert_task', methods=['POST'])
def insert_task():
    task_args = request.get_json()
    task = util.args_to_task(task_args)
    task_queue.insert_task(task)

    return jsonify({"task_id": task._task_id})


@app.route('/get_task_result', methods=['POST'])
def get_task_result():
    task_id = request.get_json()['task_id']
    encoded_image = task_queue.get_task_result(task_id)
    return jsonify({"result": encoded_image})


def setup_flask_logger():
    from flask.logging import default_handler
    app.logger.removeHandler(default_handler)

    logger = app.logger
    logger.setLevel(logging.DEBUG)

    custom_handler = logging.FileHandler('logfile.log', 'w')
    custom_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    custom_handler.setFormatter(formatter)

    logger.addHandler(custom_handler)


if __name__ == '__main__':
    setup_flask_logger()

    app.logger.info('starting...')

    task_queue = TaskQueue()

    consumer_thread = threading.Thread(target=task_queue.worker)
    consumer_thread.start()

    from gevent import pywsgi
    server = pywsgi.WSGIServer(('0.0.0.0', 8000), app)
    server.serve_forever()
