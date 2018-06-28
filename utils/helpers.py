import os
import urllib3
import urllib.parse
import sys
import csv

urllib3.disable_warnings()
http = urllib3.PoolManager()


project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)


def is_valid_file(file_name):
    if file_name.endswith('.csv'):
        print("Error. Remove file extension and try again")
        return False

    if '/' in file_name or '\\' in file_name:
        print('File name should not contain "/" or "\\"')
        return False

    return True


def display_inserted(result, name=None):
    print('----------------------------------------------------------------\n')
    print('        --------    TRANSACTIONS SUMMARY        --------        \n')
    print('        --------       {0}       --------        \n'.format(name))
    print('----------------------------------------------------------------\n')
    print("There are {0}  successfully inserted records\n".format(len(result)))
    print('================================================================\n')

    if len(result) <= 0:
        print("No record was inserted\n")
    else:
        print('{0} \t{1} \t '.format('Line No.', 'Description'))
        print('------------------------------------------------------------\n')
        for item in result:
            print('{0}\t{1}'.format(item[1], item[0]))


def display_skipped(result):
    print('----------------------------------------------------------------\n')
    print('There are {0}  skipped records \n'.format(len(result)))
    print('===============================================================\n')
    if len(result) <= 0:
        print('No record was skipped \n')
    else:

        print('{0} \t{1} \t {2}'.format('Line No.', 'Description',
                                        'Error Message'))
        print('------------------------------------------------------------\n')
        for key, value in result.items():

            print('{0}\t \t{1} \t{2}'.format(value[1], key, value[0]))


def is_valid_url(url):
    """
    checks if url is valid
    :param url: url
    :return: boolean
    """
    parsed_url = urllib.parse.urlparse(url)

    if parsed_url.scheme and parsed_url.netloc:
        return True

    print('Please enter a valid url.')
    return False


def get_csv_from_url(url, filepath):
    """
    Get csv from URL
    :param url: url that points to csv file
    :param filepath: base path for csv files
    :return: None or file object
    """

    _, filename = os.path.split(url)

    try:
        res = http.urlopen('GET', url, redirect=True)
    except (urllib3.exceptions.HTTPError):
        print('There was an error while processing your request')
        return None

    if 'csv' in res.getheader('content-type'):
        f = open(filepath + filename, 'wb')
        f.write(res.data)
        f.close()
        return filename

    print('The url does not point to a valid a csv file')
    return None


def write_record_skipped(record, file_path):
    """
    Write skipped record to a file
    :param record: record  that was skipped
    :param file_path: path to the output file
    :return: None
    """
    filename = "/skipped.csv"
    fieldnames = ('Make', 'Type', 'Asset Code', 'Category', 'Sub-Category',
                  'Model Number', 'Serial No.')
    with open(file_path + filename, "a+") as csv_file:
        print('\n')
        for row in record:
            dw = csv.DictWriter(csv_file, delimiter=',', fieldnames=fieldnames)
            dw.writerow(row)
