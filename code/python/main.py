from flask import Flask
import logging
import os
import db as db
import notification as tg
import mining as mining
from time import sleep

db_port = os.environ['db_port']

db_login = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'db',
    'port': db_port,
    'client_encoding': 'utf-8'
}

app = Flask(__name__)
host = os.environ['flask_host']
port = os.environ['flask_port']
tg_chat_id = os.environ['tg_chat']
collect_samples = 300

logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%s'
)

logger = logging.getLogger(__name__)


@app.route('/health', methods=['GET'])
def api_func():
    return 'ok'


@app.route('/send', methods=['GET'])
def api_send():
    tg.send_message(tg_chat_id, 'Hello')
    return 'ok'


@app.route('/start-simulation', methods=['GET'])
def api_start_simulation():
    mining.start_simulation()
    return 'Simulation started'


@app.route('/start-collecting-devices', methods=['GET'])
def api_start_collecting_devices():
    mining.get_devices_data()
    return 'Devices collected'


@app.route('/start-collecting-mesurements', methods=['GET'])
def api_start_collecting_mesurements():
    found_nodes_with_error = []
    for _ in range(collect_samples):
        df = mining.get_mesurements_data()
        nodes_with_error = df[df['status'] != 'Good']['value_id'].unique()
        for node in nodes_with_error:
            if node not in found_nodes_with_error:
                found_nodes_with_error.append(node)
                notification_text = mining.get_notification_data(node)
                logger.warning(notification_text)
                tg.send_message(tg_chat_id, notification_text)
        sleep(1)
    return 'Mesurements collected'


def main():
    app.run(host=host, port=port)


if __name__ == '__main__':
    main()