
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


class DependencyChecker():
    def __init__(self, columns):
        self.columns = columns

    @classmethod
    def check_dependency(cls, column, columns):
        instance = cls(columns)
        return instance.get_dependency(column)

    @classmethod
    def has_dep(cls, column, columns):
        instance = cls(columns)
        return instance.has_dep(column)

    # def has_dep(self, column):
    #     if self.columns[0] == column:
    #         return False
    #     return True

    def get_dependency(self, column):
        if column in self.columns:
            colunm_index = self.columns.index(column)
            if colunm_index > 0:
                return self.columns[colunm_index - 1]
        return None
