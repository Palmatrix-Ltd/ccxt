# -*- coding: utf-8 -*-


import numbers  # noqa E402
from ccxt.base.precise import Precise  # noqa E402


def log_template(exchange, method, entry):
    return ' <<< ' + exchange.id + ' ' + method + ' ::: ' + exchange.json(entry) + ' >>> '


def are_same_types(exchange, entry, key, format):
    # because "typeof" string is not transpilable without === 'name', we list them manually at this moment
    entry_key_val = exchange.safe_value(entry, key)
    format_key_val = exchange.safe_value(format, key)
    same_string = (isinstance(entry_key_val, str)) and (isinstance(format_key_val, str))
    same_numeric = (isinstance(entry_key_val, numbers.Real)) and (isinstance(format_key_val, numbers.Real))
    # todo: the below is correct, but is not being transpiled into python correctly: (x == False) instead of (x is False)
    # const same_boolean = ((entryKeyVal === true) || (entryKeyVal === false)) && ((formatKeyVal === true) || (formatKeyVal === false));
    same_boolean = ((entry_key_val or not entry_key_val) and (format_key_val or not format_key_val))
    same_array = isinstance(entry_key_val, list) and isinstance(format_key_val, list)
    same_object = (isinstance(entry_key_val, dict)) and (isinstance(format_key_val, dict))
    result = (entry_key_val is None) or same_string or same_numeric or same_boolean or same_array or same_object
    return result


def assert_structure_keys(exchange, method, entry, format, empty_not_allowed_for=[]):
    # define common log text
    log_text = log_template(exchange, method, entry)
    # ensure item is not null/undefined/unset
    assert entry, 'item is null/undefined' + log_text
    # get all expected & predefined keys for this specific item and ensure thos ekeys exist in parsed structure
    if isinstance(format, list):
        assert isinstance(entry, list), 'entry is not an array' + log_text
        real_length = len(entry)
        expected_length = len(format)
        assert real_length == expected_length, 'entry length is not equal to expected length of ' + str(expected_length) + log_text
        for i in range(0, len(format)):
            is_in_array = exchange.in_array(i, empty_not_allowed_for)
            if is_in_array:
                assert (entry[i] is not None), str(i) + ' index is undefined, but is is was expected to be set' + log_text
            # because of other langs, this is needed for arrays
            assert are_same_types(exchange, entry, i, format), str(i) + ' index does not have an expected type ' + log_text
    else:
        assert isinstance(entry, dict), 'entry is not an object' + log_text
        keys = list(format.keys())
        for i in range(0, len(keys)):
            key = keys[i]
            key_str = str(key)
            assert (key in entry), key_str + ' key is missing from structure' + log_text
            if exchange.in_array(key, empty_not_allowed_for):
                # if it was in needed keys, then it should have value.
                assert entry[key] is not None, key + ' key has an null value, but is expected to have a value' + log_text
            assert are_same_types(exchange, entry, key, format), key + ' key is neither undefined, neither of expected type' + log_text


def assert_common_timestamp(exchange, method, entry, now_to_check=None, key_name='timestamp'):
    # define common log text
    log_text = log_template(exchange, method, entry)
    is_date_time_object = isinstance(key_name, str)
    # ensure timestamp exists in object
    if is_date_time_object:
        assert (key_name in entry), 'timestamp key ' + key_name + ' is missing from structure' + log_text
    else:
        # if index was provided (mostly from fetchOHLCV) then we check if it exists, as mandatory
        assert not (entry[key_name] is None), 'timestamp index ' + key_name + ' is undefined' + log_text
    ts = entry[key_name]
    if ts is not None:
        # todo: add transpilable is_integer
        assert isinstance(ts, numbers.Real), 'timestamp is not numeric' + log_text
        assert ts > 1230940800000, 'timestamp is impossible to be before 1230940800000 / 03.01.2009' + log_text  # 03 Jan 2009 - first block
        assert ts < 2147483648000, 'timestamp more than 2147483648000 / 19.01.2038' + log_text  # 19 Jan 2038 - int32 overflows # 7258118400000  -> Jan 1 2200
        if now_to_check is not None:
            assert ts < now_to_check + 60000, 'trade timestamp is not below current time. Returned datetime: ' + exchange.iso8601(ts) + ', now: ' + exchange.iso8601(now_to_check) + log_text
    # only in case if the entry is a dictionary, thus it must have 'timestamp' & 'datetime' string keys
    if is_date_time_object:
        # we also test 'datetime' here because it's certain sibling of 'timestamp'
        assert ('datetime' in entry), 'datetime is missing from structure' + log_text
        dt = entry['datetime']
        if dt is not None:
            assert isinstance(dt, str), 'datetime is not a string' + log_text
            assert dt == exchange.iso8601(entry['timestamp']), 'datetime is not iso8601 of timestamp' + log_text


def assert_currency_code(exchange, method, entry, actual_code, expected_code=None):
    log_text = log_template(exchange, method, entry)
    if actual_code is not None:
        assert isinstance(actual_code, str), 'currency code should be either undefined or a string' + log_text
        assert (actual_code in exchange.currencies), 'currency code should be present in exchange.currencies' + log_text
        if expected_code is not None:
            assert actual_code == expected_code, 'currency code in response (' + actual_code + ') should be equal to expected code (' + expected_code + ')' + log_text


def assert_symbol(exchange, method, entry, key, expected_symbol=None):
    log_text = log_template(exchange, method, entry)
    actual_symbol = exchange.safe_string(entry, key)
    if actual_symbol is not None:
        assert isinstance(actual_symbol, str), 'symbol should be either undefined or a string' + log_text
        assert (actual_symbol in exchange.markets), 'symbol should be present in exchange.symbols' + log_text
    if expected_symbol is not None:
        assert actual_symbol == expected_symbol, 'symbol in response (' + actual_symbol + ') should be equal to expected symbol (' + expected_symbol + ')' + log_text


def assert_greater(exchange, method, entry, key, compare_to):
    log_text = log_template(exchange, method, entry)
    value = exchange.safe_string(entry, key)
    if value is not None:
        assert Precise.string_gt(value, compare_to), key + ' is expected to be > ' + compare_to + log_text


def assert_greater_or_equal(exchange, method, entry, key, compare_to):
    log_text = log_template(exchange, method, entry)
    value = exchange.safe_string(entry, key)
    if value is not None:
        assert Precise.string_ge(value, compare_to), key + ' is expected to be >= ' + compare_to + log_text


def assert_less(exchange, method, entry, key, compare_to):
    log_text = log_template(exchange, method, entry)
    value = exchange.safe_string(entry, key)
    if value is not None:
        assert Precise.string_lt(value, compare_to), key + ' is expected to be < ' + compare_to + log_text


def assert_less_or_equal(exchange, method, entry, key, compare_to):
    log_text = log_template(exchange, method, entry)
    value = exchange.safe_string(entry, key)
    if value is not None:
        assert Precise.string_le(value, compare_to), key + ' is expected to be <= ' + compare_to + log_text


def assert_against_array(exchange, method, entry, key, expected_array):
    log_text = log_template(exchange, method, entry)
    value = exchange.safe_value(entry, key)
    if value is not None:
        assert exchange.in_array(value, expected_array), '\"' + key + '\" key is expected to be one from: [' + ','.join(expected_array) + ']' + log_text


def revise_fee_object(exchange, method, entry):
    log_text = log_template(exchange, method, entry)
    if entry is not None:
        assert ('cost' in entry), '\"fee\" should contain a \"cost\" key' + log_text
        assert_greater_or_equal(exchange, method, entry, 'cost', '0')
        assert ('currency' in entry), '\"fee\" should contain a \"currency\" key' + log_text
        assert_currency_code(exchange, method, entry, entry['currency'])


def revise_fees_object(exchange, method, entry):
    log_text = log_template(exchange, method, entry)
    if entry is not None:
        assert isinstance(entry, list), '\"fees\" is not an array' + log_text
        for i in range(0, len(entry)):
            revise_fee_object(exchange, method, entry[i])


def revise_sorted_timestamps(exchange, method, code_or_symbol, items, ascending=False):
    for i in range(0, len(items)):
        if i > 0:
            ascending_or_descending = 'ascending' if ascending else 'descending'
            first_index = i - 1 if ascending else i
            second_index = i if ascending else i - 1
            assert items[first_index]['timestamp'] >= items[second_index]['timestamp'], exchange.id + ' ' + method + ' ' + code_or_symbol + ' must return a ' + ascending_or_descending + ' sorted array of items by timestamp. ' + exchange.json(items)
