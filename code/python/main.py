from flask import Flask, request, Response
import logging
import os
import db as db
import notification as tg
import mining as mining
from time import sleep
from multiprocessing import Process

processes = {}

db_port = os.environ['db_port']
db_password = os.environ['db_password']

db_login = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': db_password,
    'host': 'db',
    'port': db_port,
    'client_encoding': 'utf-8'
}

app = Flask(__name__)
host = os.environ['flask_host']
port = os.environ['flask_port']
tg_chat_id = os.environ['tg_chat']
flask_token = os.environ['token']
cnc_url = os.environ['cnc_api_url']
milling_url = os.environ['milling_api_url']
collect_samples = int(os.environ['opc_ua_samples'])

logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%s'
)

logger = logging.getLogger(__name__)



@app.route('/health', methods=['GET'])
def api_func():
    token = request.args.get('token', '')
    logger.warning(token, flask_token, flask_token==token)
    if token == flask_token:
        return 'ok'
    else:
        return Response('Wrong token', 401)


@app.route('/send', methods=['GET'])
def api_send():
    token = request.args.get('token', '')
    if token == flask_token:
        tg.send_message(tg_chat_id, 'Hello')
        return 'ok'
    else:
        return Response('Wrong token', 401)


@app.route('/start-simulation', methods=['GET'])
def api_start_simulation():
    token = request.args.get('token', '')
    if token == flask_token:
        mining.start_simulation()
        return 'Simulation started'
    else:
        return Response('Wrong token', 401)

@app.route('/start-collecting-devices', methods=['GET'])
def api_start_collecting_devices():
    token = request.args.get('token', '')
    if token == flask_token:
        mining.get_devices_data()
        return 'Devices collected'
    else:
       return Response('Wrong token', 401)

@app.route('/start-collecting-measurements', methods=['GET'])
def api_start_collecting_measurements():
    token = request.args.get('token', '')
    if token == flask_token:
        query = 'SELECT DISTINCT value_id FROM devices'
        found_nodes_with_error = []
        devices_list = db.query_to_df(query, login=db_login)['value_id'].unique()
        for _ in range(collect_samples):
            df = mining.get_maesurements_data(devices_list)
            nodes_with_error = df[df['status'] != 'Good']['value_id'].unique()
            for node in nodes_with_error:
                if node not in found_nodes_with_error:
                    found_nodes_with_error.append(node)
                    notification_text = mining.get_notification_data(node)
                    logger.warning(notification_text)
                    tg.send_message(tg_chat_id, notification_text)
            sleep(1)
        return 'Measurements collected'
    else:
        return Response('Wrong token', 401)

@app.route('/start-collect-cnc', methods=['GET'])
def api_start_cnc_collect():
    token = request.args.get('token', '')
    proc_name = 'cnc'
    if token == flask_token and proc_name not in processes:
        miner = lambda: mining.mine_machine_data('CNC machine', cnc_url, 'cnc_machine_data')
        process = Process(target=miner, daemon=True, name=proc_name)
        process.start()
        processes[proc_name] = process
        return 'CNC collecting started'
    else:
        return Response('Wrong token', 401)

@app.route('/stop-collect-cnc', methods=['GET'])
def api_stop_cnc_collect():
    token = request.args.get('token', '')
    proc_name = 'cnc'
    if token == flask_token and proc_name in processes:
        processes.get(proc_name, Process()).kill()
        processes.pop(proc_name)
        return 'CNC collecting stoped'
    else:
        return Response('Wrong token', 401)


@app.route('/start-collect-milling', methods=['GET'])
def api_start_milling_collect():
    token = request.args.get('token', '')
    proc_name = 'milling'
    if token == flask_token and proc_name not in processes:
        miner = lambda: mining.mine_machine_data('Milling machine', milling_url, 'milling_machine_data')
        process = Process(target=miner, daemon=True, name=proc_name)
        process.start()
        processes[proc_name] = process
        return 'milling collecting started'
    else:
        return Response('Wrong token', 401)

@app.route('/stop-collect-milling', methods=['GET'])
def api_stop_milling_collect():
    token = request.args.get('token', '')
    proc_name = 'milling'
    if token == flask_token and proc_name in processes:
        processes.get(proc_name, Process()).kill()
        processes.pop(proc_name)
        return 'milling collecting stoped'
    else:
        return Response('Wrong token', 401)

def main():
    app.run(host=host, port=port)


if __name__ == '__main__':
    main()