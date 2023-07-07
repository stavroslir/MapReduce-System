def map_function(data):
    import json
    word_list = data.split()
    return json.dumps([(word, 1) for word in word_list])

def shuffle_function(mapped_data):
    import json
    from collections import defaultdict
    result = defaultdict(list)

    # Iterate over the list of key-value pairs
    for pair in mapped_data:
        if len(pair) != 2:  # Skip elements that don't have exactly two items
            continue
        key, value = pair
        result[key].append(value)

    return json.dumps(list(result.items()))




def reduce_function(input_paths):
    import json
    result = {}
    for input_path in input_paths:
        with open(input_path, 'r') as file:
            shuffled_data = json.load(file)
        for key, values in shuffled_data:
            total_count = sum(values)
            if key in result:
                result[key] += total_count
            else:
                result[key] = total_count
    return json.dumps(result)
