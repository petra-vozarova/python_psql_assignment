import psycopg2
import testing.postgresql
from main import read_data, create_and_execute_query

NUMBER_OF_INTERFACE_TYPES = 5
EXPECTED_ENTRIES = 9
PORT_CHANNEL_ENTRIES = 2
TENGB_ETHERNET_ENTRIES = 4
GB_ETHERNET_ENTRIES = 3

class TestDatabase:
    def setup_class(self):
        self.interfaces = read_data()

    def test_read_data(self):
        """
        Asserts whether the corrent number of interfaces was read and returned from the read_data().
        As per the documentation we expect 5 types of interfaces present.
        """
        keys = self.interfaces.keys()
        assert len(keys) == NUMBER_OF_INTERFACE_TYPES

    def test_table_exists_after_creation(self):
        """
        Asserts whether the table exist in our test DB.
        Table should not exist before running create_and_execute_query() function.
        """
        with testing.postgresql.Postgresql() as postgresql:
            # connect to PostgreSQL
            connection = psycopg2.connect(**postgresql.dsn())
            cursor = connection.cursor()

            query = """
                SELECT EXISTS(
                    SELECT FROM pg_tables WHERE tablename = 'device_configuration'
                );
            """
            cursor.execute(query)
            table_found = cursor.fetchone()[0]
            assert table_found == False

            create_and_execute_query(self.interfaces, connection, cursor)

            cursor.execute(query)
            table_found = cursor.fetchone()[0]
            assert table_found == True

    def test_table_inserts_counts(self):
        """
        Queries the table and asserts whether the correct number of entries exist in it.
        Checks for overall number of rows as well as for the count of each interface type
        """
        with testing.postgresql.Postgresql() as postgresql:
            connection = psycopg2.connect(**postgresql.dsn())
            cursor = connection.cursor()

            create_and_execute_query(self.interfaces, connection, cursor)

            cursor.execute(f"SELECT COUNT(*) FROM device_configuration;")
            overall_count = cursor.fetchone()[0]
            assert overall_count == EXPECTED_ENTRIES

            cursor.execute(f"SELECT COUNT(*) FROM device_configuration WHERE name ~* 'Port-channel';")
            port_channel_count = cursor.fetchone()[0]
            assert port_channel_count == PORT_CHANNEL_ENTRIES

            cursor.execute(f"SELECT COUNT(*) FROM device_configuration WHERE name ~* 'TenGigabitEthernet';")
            tengigabit_ethernet_count = cursor.fetchone()[0]
            assert tengigabit_ethernet_count == TENGB_ETHERNET_ENTRIES

            cursor.execute(f"SELECT COUNT(*) FROM device_configuration WHERE name ~* '^GigabitEthernet';")
            gigabit_ethernet_count = cursor.fetchone()[0]
            assert gigabit_ethernet_count == GB_ETHERNET_ENTRIES

    def test_duplicate_data_not_inserted(self):
        """
        Asserts that after quering the same table with the sama data, no duplicate entries are inserted.
        Overall number of rows stays the same.
        """
        with testing.postgresql.Postgresql() as postgresql:
            connection = psycopg2.connect(**postgresql.dsn())
            cursor = connection.cursor()

            create_and_execute_query(self.interfaces, connection, cursor)
            create_and_execute_query(self.interfaces, connection, cursor)

            cursor.execute(f"SELECT COUNT(*) FROM device_configuration;")
            overall_count = cursor.fetchone()[0]
            assert overall_count == EXPECTED_ENTRIES





