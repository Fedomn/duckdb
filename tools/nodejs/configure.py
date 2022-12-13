import os
import sys
import pickle

# list of extensions to bundle
extensions = ['parquet', 'icu', 'json']

# path to target
basedir = os.getcwd()
target_dir = os.path.join(basedir, 'src', 'duckdb')
gyp_in = os.path.join(basedir, 'binding.gyp.in')
gyp_out = os.path.join(basedir, 'binding.gyp')
cache_file = os.path.join(basedir, 'filelist.cache')

# path to package_build.py
os.chdir(os.path.join('..', '..'))
scripts_dir = 'scripts'

sys.path.append(scripts_dir)
import package_build

def sanitize_path(x):
    return x.replace('\\', '/')

defines = []
for ext in extensions:
    defines.extend(['BUILD_{}_EXTENSION'.format(ext.upper())])

if 'DUCKDB_NODE_BUILD_CACHE' in os.environ and os.path.isfile(cache_file):
    with open(cache_file, 'rb') as f:
        cache = pickle.load(f)
    source_list = cache['source_list']
    include_list = cache['include_list']
    library_text = cache['library_text']
    windows_options = cache['windows_options']
    cflags = cache['cflags']
elif 'DUCKDB_NODE_BINDIR' in os.environ:
    def find_library_path(libdir, libname):
        flist = os.listdir(libdir)
        for fname in flist:
            fpath = os.path.join(libdir, fname)
            if os.path.isfile(fpath) and package_build.file_is_lib(fname, libname):
                return fpath
        raise Exception(f"Failed to find library {libname} in {libdir}")
    # existing build
    existing_duckdb_dir = os.environ['DUCKDB_NODE_BINDIR']
    cflags = os.environ['DUCKDB_NODE_CFLAGS']
    libraries = os.environ['DUCKDB_NODE_LIBS'].split(' ')

    include_directories = [os.path.join('..', '..', include) for include in package_build.third_party_includes()]
    include_list = package_build.includes(extensions)

    result_libraries = package_build.get_libraries(existing_duckdb_dir, libraries, extensions)
    libraries = []
    for (libdir, libname) in result_libraries:
        if libdir is None:
            continue
        libraries.append(find_library_path(libdir, libname))

    libs = ',\n                 '.join(['"' + sanitize_path(x) + '"' for x in libraries])
    source_list = []
    library_text = f'''"libraries": [
                 {libs}
            ]
    '''
    cflags = ''
    windows_options = ''
    print(os.environ['DUCKDB_NODE_CFLAGS'])
    if os.name == 'nt':
        all_options = [x for x in os.environ['DUCKDB_NODE_CFLAGS'].split(' ') if len(x) > 0 and x[0] == '/']
        windows_options = ',\n                        '.join(['"' + x + '"' for x in all_options])
    else:
        cflag_list = []
        if '-g' in os.environ['DUCKDB_NODE_CFLAGS']:
            cflag_list += ['-g']
        if '-O0' in os.environ['DUCKDB_NODE_CFLAGS']:
            cflag_list += ['-O0']
        cflags = ',\n                '.join(['"' + x + '"' for x in cflag_list])

    if 'DUCKDB_NODE_BUILD_CACHE' in os.environ:
        cache = {
            'source_list': source_list,
            'include_list': include_list,
            'library_text': library_text,
            'cflags': cflags,
            'windows_options': windows_options
        }
        with open(cache_file, 'wb+') as f:
            pickle.dump(cache, f)
else:
    # fresh build - copy over all of the files
    (source_list, include_list, original_sources) = package_build.build_package(target_dir, extensions, False)

    # # the list of all source files (.cpp files) that have been copied into the `duckdb_source_copy` directory
    # print(source_list)
    # # the list of all include files
    # print(include_list)
    source_list = [os.path.relpath(x, basedir) if os.path.isabs(x) else os.path.join('src', x) for x in source_list]
    include_list = [os.path.join('src', 'duckdb', x) for x in include_list]
    library_text = ''
    windows_options = ''
    cflags = ''

define_text = ',\n                '.join(['"' + x + '"' for x in defines])

with open(gyp_in, 'r') as f:
    text = f.read()

text = text.replace('${SOURCE_FILES}', ',\n                '.join(['"' + sanitize_path(x) + '"' for x in source_list]))
text = text.replace('${INCLUDE_FILES}', ',\n                '.join(['"' + sanitize_path(x) + '"' for x in include_list]))
text = text.replace('${LIBRARY_FILES}', library_text)
text = text.replace('${WINDOWS_OPTIONS}', windows_options)
text = text.replace('${CFLAGS}', cflags)
text = text.replace('${DEFINES}', define_text)

with open(gyp_out, 'w+') as f:
    f.write(text)
