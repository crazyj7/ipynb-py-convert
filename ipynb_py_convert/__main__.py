import json
import sys
from os import path
import io

header_comment = '# %%\n'


def nb2py(notebook):
    result = []
    cells = notebook['cells']

    for cell in cells:
        cell_type = cell['cell_type']

        if cell_type == 'markdown':
            result.append("%s'''\n%s\n'''" %
                          (header_comment, ''.join(cell['source'])))

        if cell_type == 'code':
            result.append("%s%s" % (header_comment, ''.join(cell['source'])))

    return '\n\n'.join(result)


def py2nb(py_str):
    # remove leading header comment
    if py_str.startswith(header_comment):
        py_str = py_str[len(header_comment):]

    cells = []
    chunks = py_str.split('\n\n%s' % header_comment)

    for chunk in chunks:
        cell_type = 'code'
        if chunk.startswith("'''"):
            chunk = chunk.strip("'\n")
            cell_type = 'markdown'

        cell = {
            'cell_type': cell_type,
            'metadata': {},
            'source': chunk.splitlines(True),
        }

        if cell_type == 'code':
            cell.update({'outputs': [], 'execution_count': None})

        cells.append(cell)

    notebook = {
        'cells': cells,
        'metadata': {
            'anaconda-cloud': {},
            'kernelspec': {
                'display_name': 'Python 3',
                'language': 'python',
                'name': 'python3'},
            'language_info': {
                'codemirror_mode': {'name': 'ipython', 'version': 3},
                'file_extension': '.py',
                'mimetype': 'text/x-python',
                'name': 'python',
                'nbconvert_exporter': 'python',
                'pygments_lexer': 'ipython3',
                'version': '3.6.1'}},
        'nbformat': 4,
        'nbformat_minor': 1
    }

    return notebook


def get_encoding(path):
    encodings = ['utf-8', 'utf-16', 'utf-32', 'utf-7', 'utf-16-be', 'utf-16-le',
                 'ascii', 'euc-kr', 'euc-jp', 'euc-jis-2004', 'euc-jisx0213', 'gb2312', 'gbk', 'hz', 'latin-1',
                 'koi8-r', 'koi8-u', 'mac-cyrillic', 'mac-greek', 'mac-iceland', 'mac-latin2', 'mac-roman',
                 'mac-turkish', 'ptcp154', 'shift-jis', 'shift-jis-2004', 'shift-jisx0213',
                 'cp437', 'cp949', 'cp932',
                 'windows-1250', 'windows-1252', ]
    for enc in encodings:
        try:
            f = io.open(path, 'r', encoding=enc)
            f.readlines()
            f.seek(0)
        except FileNotFoundError as ex:
            return 'utf-8'
        except Exception as ex:
            pass
        else:
            return enc
    return 'unknown'


def open_autoenc(path, mode, encoding=''):
    if len(encoding)==0:
        enc = get_encoding(path)
    else:
        enc = encoding
#     print(enc)
    return open(path, mode, encoding=enc)


def convert(in_file, out_file):
    _, in_ext = path.splitext(in_file)
    _, out_ext = path.splitext(out_file)

    if in_ext == '.ipynb' and out_ext == '.py':
        with open_autoenc(in_file, 'r') as f:
            notebook = json.load(f)
        py_str = nb2py(notebook)
        with open_autoenc(out_file, 'w') as f:
            f.write(py_str)

    elif in_ext == '.py' and out_ext == '.ipynb':
        with open_autoenc(in_file, 'r') as f:
            py_str = f.read()
        notebook = py2nb(py_str)
        with open_autoenc(out_file, 'w') as f:
            json.dump(notebook, f, indent=2)

    else:
        raise(Exception('Extensions must be .ipynb and .py or vice versa'))


def main():
    argv = sys.argv
    out_file = ''
    if len(argv) < 2:
        print('Usage: ipynb-py-convert in.ipynb [out.py]')
        print('or:    ipynb-py-convert in.py [out.ipynb]')
        sys.exit(1)

    if len(argv) == 2:
        out_file = argv[1]
        exts = out_file.split('.')
        filename = '.'.join(exts[:-1])
        if exts[-1] == 'ipynb':
            out_file = filename+'.py'
        if exts[-1] == 'py':
            out_file = filename+'.ipynb'

    else:
        out_file = argv[2]

    convert(in_file=argv[1], out_file=out_file)


if __name__ == '__main__':
    main()
