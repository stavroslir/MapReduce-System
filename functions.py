
def map_function(data):
    import json
    word_list = data.split()
    return json.dumps([(word, 1) for word in word_list])

def shuffle_function(mapped_data):
    import json
    from collections import defaultdict
    result = defaultdict(list)
    mapped_data = json.loads(mapped_data)
    for key, value in sorted(mapped_data, key=lambda x: x[0]):
        result[key].append(value)
    return json.dumps(list(result.items()))

def reduce_function(shuffled_data):
    import json
    result = {}
    shuffled_data = json.loads(shuffled_data)
    for key, values in shuffled_data:
        total_count = sum(values)
        result[key] = total_count
    return json.dumps(result)
