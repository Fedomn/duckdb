import os
import re
import json

scalar_functions = ['bit', 'blob', 'date', 'enum']

header = '''//===----------------------------------------------------------------------===//
//                         DuckDB
//
// {HEADER}_functions.hpp
//
//
//===----------------------------------------------------------------------===//
// This file is generated by scripts/generate_functions.py

#pragma once

#include "duckdb/function/function_set.hpp"

namespace duckdb {

'''

footer = '''}
'''

def normalize_path_separators(x):
    return os.path.sep.join(x.split('/'))

function_type_set = {}
all_function_list = []
for scalar in scalar_functions:
    path = f'scalar/{scalar}'
    header_path = normalize_path_separators(f'extension/core_functions/include/{path}_functions.hpp')
    json_path = normalize_path_separators(f'extension/core_functions/{path}/functions.json')
    with open(json_path, 'r') as f:
        parsed_json = json.load(f)
    new_text = header.replace('{HEADER}', path)
    for entry in parsed_json:
        function_text = ''
        struct_type = entry['struct']
        if 'alias' in entry:
            aliased_type = function_type_set[entry['alias']]
            if aliased_type == 'scalar_function':
                all_function_list.append([entry['name'], f"DUCKDB_SCALAR_FUNCTION_ALIAS({struct_type})"])
            elif aliased_type == 'scalar_function_set':
                all_function_list.append([entry['name'], f"DUCKDB_SCALAR_FUNCTION_SET_ALIAS({struct_type})"])
            else:
                print("Unknown entry type " + aliased_type + ' for entry ' + entry['struct'])
                exit(1)
            function_type_set[entry['struct']] = aliased_type
            new_text += '''struct {STRUCT} {
	using ALIAS = {ALIAS};

	static constexpr const char *Name = "{NAME}";
};

'''.replace('{STRUCT}', entry['struct']).replace('{NAME}', entry['name']).replace('{ALIAS}', entry['alias'])
            continue
        function_type_set[entry['struct']] = entry['type']
        if entry['type'] == 'scalar_function':
            function_text = 'static ScalarFunction GetFunction();'
            all_function_list.append([entry['name'], f"DUCKDB_SCALAR_FUNCTION({struct_type})"])
        elif entry['type'] == 'scalar_function_set':
            function_text = 'static ScalarFunctionSet GetFunctions();'
            all_function_list.append([entry['name'], f"DUCKDB_SCALAR_FUNCTION_SET({struct_type})"])
        else:
            print("Unknown entry type " + entry['type'] + ' for entry ' + entry['struct'])
            exit(1)
        new_text += '''struct {STRUCT} {
	static constexpr const char *Name = "{NAME}";
	static constexpr const char *Parameters = "{PARAMETERS}";
	static constexpr const char *Description = "{DESCRIPTION}";
	static constexpr const char *Example = "{EXAMPLE}";

	{FUNCTION}
};

'''.replace('{STRUCT}', entry['struct']).replace('{NAME}', entry['name']).replace('{PARAMETERS}', entry['parameters'] if 'parameters' in entry else '').replace('{DESCRIPTION}', entry['description']).replace('{EXAMPLE}', entry['example']).replace('{FUNCTION}', function_text)
    new_text += footer
    with open(header_path, 'w+') as f:
        f.write(new_text)

function_list_file = normalize_path_separators('extension/core_functions/function_list.cpp')
with open(function_list_file, 'r') as f:
    text = f.read()

static_function = 'static StaticFunctionDefinition internal_functions[] = {'
pos = text.find(static_function)
header = text[:pos]
footer_lines = text[pos:].split('\n')
footer = ''
for i in range(len(footer_lines)):
    if len(footer_lines[i]) == 0:
        footer = '\n'.join(footer_lines[i:])
        break

new_text = header
new_text += static_function + '\n'
all_function_list = sorted(all_function_list, key=lambda x: x[0])
for entry in all_function_list:
    new_text += '\t' + entry[1] + ',\n'
new_text += '\tFINAL_FUNCTION\n};\n'
new_text += footer

with open(function_list_file, 'w+') as f:
    f.write(new_text)
