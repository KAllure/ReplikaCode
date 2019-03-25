import os
import sys

from cakechat.utils.env import get_gpu_id_by_gunicorn_worker_idx, set_keras_tf_session

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


os.environ['CUDA_VISIBLE_DEVICES'] = get_gpu_id_by_gunicorn_worker_idx()
set_keras_tf_session(gpu_memory_fraction=os.environ['GPU_MEMORY_FRACTION'])

from cakechat.api.v1.server import app

if __name__ == '__main__':
    # runs development server
    app.run(host='0.0.0.0', port=8080)
