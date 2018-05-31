# #!/usr/bin/python
# # fetch.py - Fetch and display the rows from a MySQL database query
#
# # import the MySQLdb and sys modules
import psycopg2
import os


#
# # open a database connection
# # be sure to change the host IP address, username,
# #  password and database name to match your own
#
#


def post_assets():
    connection = psycopg2.connect(os.environ.get('DATABASE_URL'))
#
#     # prepare a cursor object using cursor() method
    cursor = connection.cursor()

    with open('assets.csv', 'r',) as f:
        next(f)
        try:
            cursor.copy_from(f, '"core_asset"',
                             sep="|", columns=('asset_code',
                                               'model_number_id',
                                               'serial_number',
                                               'created_at',
                                               'last_modified',
                                               'current_status',
                                               'asset_condition'))
        except psycopg2.IntegrityError:
            connection.rollback()

    connection.commit()
    connection.close()


if __name__ == '__main__':
    post_assets()
