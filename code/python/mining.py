from opcua import Client
from opcua.common.node import Node
from datetime import datetime
import os
import pandas as pd
from pandas import DataFrame
from typing import List, Callable
import db as db
import logging
import requests
import json
import re
import numpy as np
import notification as tg
from time import sleep

logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%s'
)
logger = logging.getLogger(__name__)
client = Client(os.environ['opc_server'])
db_port = os.environ['db_port']
cnc_url = os.environ['cnc_api_url']
milling_url = os.environ['milling_api_url']
tg_chat_id = os.environ['tg_chat']
db_login = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'db',
    'port': db_port,
    'client_encoding': 'utf-8'
}
simulation_nodes_id = ['ns=4;i=1287', 'ns=5;i=31']
boilers_node_id = 'ns=4;i=1240'


def try_catch(func: Callable) -> any:
    try:
        return func()
    except Exception as e:
        return None


def start_simulation() -> None:
    client.connect()
    for simulation_id in simulation_nodes_id:
        simulation_node = client.get_node(simulation_id)
        logger.warning(simulation_node)
        try_catch(lambda: simulation_node.call_method('Reset'))
        try_catch(lambda: simulation_node.call_method('Start'))
    client.disconnect()


def recieve_measurement_data(devices_list: List[str]) -> DataFrame:
    client.connect()
    result = list()
    timestamp = datetime.now()
    for device in devices_list:
        device_node = client.get_node(device)
        value = try_catch(lambda: device_node.get_data_value().Value.Value)
        status= try_catch(lambda: device_node.get_data_value().StatusCode.name)
        result.append({
            'value_id': device,
            'value': value,
            'status': status,
            'timestamp': timestamp
        })
        
    client.disconnect()
    return pd.DataFrame(result)


def recieve_devices_data() -> DataFrame:
    client.connect()
    boilers = client.get_node(boilers_node_id)
    device_data = read_all_nodes(boilers)
    device_df = parse_devices_data(device_data['childs'])
    client.disconnect()
    return device_df.drop_duplicates()


def node_to_dict(node: Node) -> dict:
    return {
        'id': str(node),
        'display_name': node.get_display_name().Text,
        'value': try_catch(lambda: node.get_data_value().Value.Value),
        'status': try_catch(lambda: node.get_data_value().StatusCode.name),
        'timestamp': datetime.now()
    }
    

def read_all_nodes(node: Node) -> dict:
    node_data = node_to_dict(node)
    if node_data['display_name'] != 'Simulation':
        childs = node.get_children()
        childs_data = [read_all_nodes(child) for child in childs]
        return {
            'node': node_data,
            'childs': childs_data
        }
    else:
        return {}


def parse_devices_data(boilers: List[dict]) -> DataFrame:
    data = list()
    for boiler in boilers:
        boiler_name = boiler.get('node',{}).get('display_name')
        boiler_id = boiler.get('node',{}).get('id')
        details = boiler.get('childs', [])
        for detail in details:
            detail_name = detail.get('node',{}).get('display_name')
            detail_id = detail.get('node',{}).get('id')
            components = detail.get('childs', [])
            for component in components:
                component_name = component.get('node',{}).get('display_name')
                component_id = component.get('node',{}).get('id')
                values = component.get('childs', [])
                for value in values:
                    value_name = value.get('node',{}).get('display_name')
                    value_id = value.get('node',{}).get('id')
                    if value_name in ['Output', 'Input']:
                        data.append({
                            'device_name': boiler_name,
                            'device_id': boiler_id,
                            'detail_name': detail_name,
                            'detail_id': detail_id,
                            'component_name': component_name,
                            'component_id': component_id,
                            'value_name': value_name,
                            'value_id': value_id
                        })
    df = DataFrame(data)
    return df.drop_duplicates()


def get_maesurements_data(devices_list: List[str]) -> DataFrame:
    logger.warning('Start getting devices data')
    mesurements_df = recieve_measurement_data(devices_list)
    db.insert_table(mesurements_df, 'measurements', login=db_login)
    logger.warning('Done getting devices data')
    return mesurements_df 


def get_devices_data():
    logger.warning('Start getting devices data')
    devices_df = recieve_devices_data()
    db.overwrite_table(devices_df, 'devices', login=db_login)
    logger.warning('Done getting devices data')

    return 0


def get_notification_data(node: str) -> str:
    df = db.query_to_df(f"""select * from devices where value_id = '{node}' """, login=db_login)
    for _, row in df.iterrows():
        device = row.get('device_name')
        detail = row.get('detail_name')
        component = row.get('component_name')
        node_name = row.get('value_name')
        return f"""<b>{device}</b>
{detail} -> {component} -> {node_name} ❌
        """


def param_val_to_float(val: str) -> float:
    val = str(val)
    result = re.sub('[^\d,-\.]', '', val).replace(',', '.')
    try:
        return float(result)
    except Exception as e:
        return None

def read_cnc_api_data(api_data: dict) -> pd.DataFrame:
    result = list()
    timestamp = datetime.now()
    for item in api_data.get('data', []):
        if len(item) > 1:
            entity = item[0]
            param_list = item[1]
            print(entity)
            for param in param_list:
                if len(param) > 1:
                    param_name = param[0]
                    param_val = param[1]
                    result.append({
                        'entity': entity,
                        'param_name': param_name,
                        'param_val_str': param_val,
                        'param_val_float': param_val_to_float(param_val),
                        'timestamp': timestamp
                    })
    return pd.DataFrame(result)

def get_cnc_data() -> pd.DataFrame:

    r = requests.get(cnc_url)
    json_data = json.loads(r.content)
    df = read_cnc_api_data(json_data)
    db.insert_table(df, 'cnc_machine_data', login=db_login)
    return df

def get_api_data(url: str, table: str) -> pd.DataFrame:
    r = requests.get(url)
    json_data = json.loads(r.content)
    df = read_cnc_api_data(json_data)
    db.insert_table(df, table, login=db_login)
    return df

def mine_cnc_data():
    sent = False
    machine = 'CNC machine'
    while True:
        sleep(10)
        try:
            df = get_api_data(cnc_url, 'cnc_machine_data')
            row = df[df['param_name'] == 'Статус канала'].iloc[0]
            status = row.get('param_val_str')
            if not sent and status != 'Работа':
                entity = row.get('entity')
                param = row.get('param_name')
                sent = True
                tg.send_message(tg_chat_id, f"""<b>{machine}</b>
{entity} -> {param} -> {status} ❌""")
        except Exception as e:
            logger.warning(f'Error: {e}')


def mine_miling_data():
    sent = False
    machine = 'Milling machine'
    while True:
        sleep(10)
        try:
            df = get_api_data(milling_url, 'milling_machine_data')
            row = df[df['param_name'] == 'Статус канала'].iloc[0]
            status = row.get('param_val_str')
            if not sent and status != 'Работа':
                entity = row.get('entity')
                param = row.get('param_name')
                sent = True
                tg.send_message(tg_chat_id, f"""<b>{machine}</b>
{entity} -> {param} -> {status} ❌""")
        except Exception as e:
            logger.warning(f'Error: {e}')


    
