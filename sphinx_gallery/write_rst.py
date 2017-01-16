# -*- coding: utf-8 -*-
r"""
Parser for rst example documents
============================

"""
# Author: Óscar Nájera
# License: 3-clause BSD

from __future__ import absolute_import, division, print_function
import os

from .downloads import CODE_DOWNLOAD
from .notebook import text2string


try:
    # textwrap indent only exists in python 3
    from textwrap import indent
except ImportError:
    def indent(text, prefix, predicate=None):
        """Adds 'prefix' to the beginning of selected lines in 'text'.

        If 'predicate' is provided, 'prefix' will only be added to the lines
        where 'predicate(line)' is True. If 'predicate' is not provided,
        it will default to adding 'prefix' to all non-empty lines that do not
        consist solely of whitespace characters.
        """
        if predicate is None:
            def predicate(line):
                return line.strip()

        def prefixed_lines():
            for line in text.splitlines(True):
                yield (prefix + line if predicate(line) else line)
        return ''.join(prefixed_lines())

SPHX_GLR_SIG = """\n.. rst-class:: sphx-glr-signature

    `Generated by Sphinx-Gallery <http://sphinx-gallery.readthedocs.io>`_\n"""

###############################################################################
# The following strings are used when we have several pictures: we use
# an html div tag that our CSS uses to turn the lists into horizontal
# lists.
HLIST_HEADER = """\n.. rst-class:: sphx-glr-horizontal\n\n"""

HLIST_IMAGE_TEMPLATE = """
    *

      .. image:: /%s
            :scale: 47
"""

SINGLE_IMAGE = """
.. image:: /%s
    :align: center
"""

# This one could contain unicode
CODE_OUTPUT = u""".. rst-class:: sphx-glr-script-out

 Out::

{0}\n"""


def codestr2rst(codestr, lang='python'):
    """Return reStructuredText code block from code string"""
    code_directive = "\n.. code-block:: {0}\n\n".format(lang)
    indented_block = indent(codestr, ' ' * 4)
    return code_directive + indented_block


def rst_notebook_cells(executed_blocks, lang='python'):
    """Writes the rst notebook cells

    Parameters
    ----------
    script_blocks : list of tuples
    """
    # A simple example has two blocks: one for the
    # example introduction/explanation and one for the code
    is_example_notebook_like = len(executed_blocks) > 2
    example_rst = u""  # there can be unicode content
    for block in executed_blocks:
        if block.label == 'code':
            figures_rst = figure_rst(block.figure_list)
            if block.stdout:
                stdout = CODE_OUTPUT.format(indent(block.stdout, u' ' * 4))
            else:
                stdout = ''
            code_output = u"\n{0}\n\n{1}\n\n".format(figures_rst, stdout)

            if is_example_notebook_like:
                example_rst += codestr2rst(block.content, lang) + '\n'
                example_rst += code_output
            else:
                example_rst += code_output
                if 'sphx-glr-script-out' in code_output:
                    # Add some vertical space after output
                    example_rst += "\n\n|\n\n"
                example_rst += codestr2rst(block.content, lang) + '\n'

        else:
            example_rst += text2string(block.content) + '\n'
    return example_rst


def figure_rst(figure_list):
    """Given a list of paths to figures generate the corresponding rst

    Depending on whether we have one or more figures, we use a
    single rst call to 'image' or a horizontal list.

    Parameters
    ----------
    figure_list : list of figures relative paths to Sphinx doc sources
    """

    images_rst = ""
    if len(figure_list) == 1:
        figure_name = figure_list[0]
        images_rst = SINGLE_IMAGE % figure_name.lstrip('/')
    elif len(figure_list) > 1:
        images_rst = HLIST_HEADER
        for figure_name in figure_list:
            images_rst += HLIST_IMAGE_TEMPLATE % figure_name.lstrip('/')

    return images_rst


def rst_notebook(executed_blocks, write_fname, time_elapsed, lang='python'):
    """Saves the notebook to a write_file"""

    ref_fname = write_fname.replace(os.path.sep, '_')

    example_rst = u"""\n\n.. _sphx_glr_{0}:\n\n""".format(ref_fname)
    example_rst += rst_notebook_cells(executed_blocks, lang)

    time_m, time_s = divmod(time_elapsed, 60)
    example_rst += "**Total running time of the script:**" \
        " ({0: .0f} minutes {1: .3f} seconds)\n\n".format(
            time_m, time_s)

    filename = os.path.splitext(write_fname)[0]
    fname = os.path.basename(filename)
    if lang == 'python':
        lang_extension = '.py'
    else:
        lang_extension = '.lua'
    example_rst += CODE_DOWNLOAD.format(fname + lang_extension,
                                        fname + ".ipynb")
    example_rst += SPHX_GLR_SIG

    return example_rst