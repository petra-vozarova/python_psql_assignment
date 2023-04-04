import json
import psycopg2
import os
from dotenv import load_dotenv

def read_data():
    """Reads data from a data file and extracts interfaces configuration data."""
    with open('./data/configClear_v2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    interfaces = data['frinx-uniconfig-topology:configuration']['Cisco-IOS-XE-native:native']['interface']
    return interfaces

def connect_database():
    """Establishes a connection with DB using .env configuration."""
    load_dotenv()
    try:
        connection = psycopg2.connect(
            database = os.environ.get('PG_DATABASE'),
            user = os.environ.get('PG_USER'),
            password = os.environ.get('PG_PASSWORD'),
            host = os.environ.get('PG_HOST'),
            port = os.environ.get('PG_PORT'),
        )

        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute('SELECT %s as connected;', ('Connection to DB successful!',))
        result = cursor.fetchone()
        print(result)
        return (connection, cursor)
    except Exception as err:
        print(f'Connection to DB failed!:\n{err}')


def create_and_execute_query(interfaces, connection, cursor):
    """
    Creates a table schema, loops through interfaces configuration data,
    extracts relevant information and inserts that data into the table.
    """

    createTableQuery = """
        CREATE TABLE IF NOT EXISTS device_configuration(
            id SERIAL PRIMARY KEY,
            connection INTEGER NULL,
            name VARCHAR(255) NOT NULL,
            description VARCHAR(255),
            config json,
            type VARCHAR(50) NULL,
            infra_type VARCHAR(50) NULL,
            port_channel_id INTEGER NULL,
            max_frame_size INTEGER NULL
        );
    """
    cursor.execute(createTableQuery)

    tracked_interfaces = ['Port-channel', 'TenGigabitEthernet', 'GigabitEthernet']
    for interface_name in interfaces.keys():
        if interface_name in tracked_interfaces:
            for device in interfaces[interface_name]:
                name = interface_name + str(device['name'])
                description = device.get('description')
                max_frame_size = device.get('mtu')
                config = json.dumps(device)
                port_channel = device.get('Cisco-IOS-XE-ethernet:channel-group')
                if port_channel:
                    if 'number' in port_channel.keys():
                        port_channel_id = port_channel['number']
                else:
                    port_channel_id = None

                # code to check for entry with the same name already being present to prevent duplicate entries
                cursor.execute(f"SELECT COUNT(*) FROM device_configuration WHERE name = '{name}';")
                entry_exists = cursor.fetchone()[0] > 0

                if not entry_exists:
                    print(f"Inserting a new interface: Name: {name}")
                    try:
                        cursor.execute("""
                            INSERT INTO device_configuration
                            (name, description, config, port_channel_id, max_frame_size, connection, type, infra_type)
                            VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (name, description, config, port_channel_id, max_frame_size, None, None, None)
                        )
                    except Exception as err:
                        print(err)

if __name__ == "__main__":
    interfaces = read_data()
    connection, cursor = connect_database()
    create_and_execute_query(interfaces, connection, cursor)
    connection.close()