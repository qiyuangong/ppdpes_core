from utils.evaluation import average_relative_error


def static_of_attribute(data, att_index):
    static_data = {}
    for record in data:
        curr = record[att_index]
        try:
            static_data[curr] += 1
        except KeyError:
            static_data[curr] = 1
    return static_data


def static_of_microdata(data, att_set):
    static_data = [{} for _ in range(len(att_set))]
    for record in data:
        for index in range(att_set):
            curr = record[index]
            try:
                static_data[index][curr] += 1
            except KeyError:
                static_data[index][curr] = 1
    return static_data


def static_of_anon_data(att_tree, anon_data, att_index):
    static_data = {}
    for record in anon_data:
        curr = record[att_index]
        try:
            static_data[curr] += 1
        except KeyError:
            static_data[curr] = 1
    return static_data