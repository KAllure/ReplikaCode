import os
import subprocess

import numpy as np
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session

from cakechat.utils.logger import get_logger

_logger = get_logger(__name__)


def _use_gpu_env():
    try:
        use_gpu = os.environ['USE_GPU']
        return int(use_gpu)
    except (KeyError, ValueError):
        return None


def is_dev_env():
    try:
        is_dev = os.environ['IS_DEV']
        return bool(int(is_dev))
    except (KeyError, ValueError):
        return False


def init_cuda_env():
    os.environ['PATH'] += ':/usr/local/cuda/bin'
    os.environ['LD_LIBRARY_PATH'] = '/usr/local/cuda/lib64:/usr/local/nvidia/lib64/:/usr/local/cuda/extras/CUPTI/lib64'
    os.environ['LIBRARY_PATH'] = '/usr/local/share/cudnn'
    os.environ['CUDA_HOME'] = '/usr/local/cuda'
    os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'


def init_keras_horovod(hvd):
    """
    Set config for Horovod. Config params copied from official example:
    https://github.com/uber/horovod/blob/master/examples/keras_mnist_advanced.py#L15

    :param hvd: instance of horovod.keras
    """

    init_cuda_env()

    hvd.init()
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True  # pylint: disable=maybe-no-member
    config.gpu_options.visible_device_list = str(hvd.local_rank())  # pylint: disable=maybe-no-member
    set_session(tf.Session(config=config))


def set_keras_tf_session(gpu_memory_fraction):
    config = tf.ConfigProto()
    config.gpu_options.per_process_gpu_memory_fraction = float(gpu_memory_fraction)  # pylint: disable=maybe-no-member
    set_session(tf.Session(config=config))


def get_gpu_id_by_gunicorn_worker_idx():
    def _get_gpu_ids():
        if 'CUDA_VISIBLE_DEVICES' not in os.environ:
            _logger.warn('CUDA_VISIBLE_DEVICES is not defined, using gpu 0')
            return ['0']

        return os.environ['CUDA_VISIBLE_DEVICES'].split(',')

    def _select_gpu_id_by_worker_idx(gpu_ids, worker_idx):
        return gpu_ids[worker_idx % len(gpu_ids)]

    if 'GUNICORN_WORKER_IDX' in os.environ:
        _logger.info('GUNICORN_WORKER_IDX = {}'.format(os.environ['GUNICORN_WORKER_IDX']))
        worker_idx = int(os.environ['GUNICORN_WORKER_IDX'])
    else:
        _logger.warn('GUNICORN_WORKER_IDX is not defined')
        worker_idx = 0

    gpu_ids = _get_gpu_ids()
    return _select_gpu_id_by_worker_idx(gpu_ids, worker_idx)


def run_horovod_train(train_cmd, gpu_ids):
    os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
    os.environ['CUDA_VISIBLE_DEVICES'] = ','.join(gpu_ids)

    cmd = 'mpirun -np {workers_nums} -H localhost:{workers_nums} {train_cmd}'.format(
        workers_nums=len(gpu_ids), train_cmd=train_cmd)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while process.poll() is None:
        output = process.stdout.readline()
        if output:
            print(output.strip())


def is_main_horovod_worker(horovod):
    return horovod is None or horovod.rank() == 0


def set_horovod_worker_random_seed(horovod):
    seed = horovod.rank() if horovod else 0
    np.random.seed(seed)

