def map_function(data):

    import json
    word_list = data.split()
    return json.dumps([(word, 1) for word in word_list])

def shuffle_function(input_paths):

    import json
    from collections import defaultdict
    result = defaultdict(list)
    for input_path in input_paths:
        with open(input_path, 'r') as file:
            mapped_data = json.load(file)
        for pair in mapped_data:
            if len(pair) != 2:  # Skip elements that don't have exactly two items
                continue
            key, value = pair
            result[key].append(value)
    return dict(result)  

def reduce_function(input):

    import ast
    dict_obj = ast.literal_eval(input)
    result_dict = dict_obj[0]
    for key,value in result_dict.items():
        word = key
        count_list = value
        result_dict[word] = sum(count_list)
    return result_dict
