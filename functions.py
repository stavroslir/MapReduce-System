from collections import defaultdict
import ast

def map_function(data):
    word_list = data.split()
    return [(word, 1) for word in word_list]

def shuffle_function(mapped_data):
    result = defaultdict(list)
    for key, value in sorted(mapped_data, key=lambda x: x[0]):
        result[key].append(value)
    return list(result.items())

def reduce_function(shuffled_data):
    result = {}
    for key, *values_str_parts in shuffled_data:
        values_str = ''.join(values_str_parts)
        values = ast.literal_eval(values_str)
        total_count = sum(int(value) for value in values)
        result[key] = total_count
    return result
