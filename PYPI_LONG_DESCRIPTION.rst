xlseries
========

A python package to scrape `time
series <https://en.wikipedia.org/wiki/Time_series>`__ from *any* excel
file and return them turned into `pandas <http://pandas.pydata.org/pandas-docs/dev/index.html>`__ `data frames <http://pandas.pydata.org/pandas-docs/dev/generated/pandas.DataFrame.html>`__.

Installation
------------

If you want to install in developer mode, `clone the repository <https://github.com/abenassi/xlseries.git>`__ and follow these instructions:

**If you are using Anaconda as your python distribution**

1. ``conda create -n xlseries python=2`` *Create new environment*
2. ``cd project_directory``
3. ``source activate xlseries`` *Activate the environment*
4. ``pip install -e .`` *Install the package in developer mode*
5. ``pip install -r requirements.txt`` *Install dependencies*
6. ``deactivate`` *Deactivate when you are done*

**If you are using a standard python installation**

1. ``cd project_directory``
2. ``virtualenv venv`` *Create new environment*
3. ``source venv/bin/activate`` *Activate the environment*
4. ``pip install -r requirements.txt`` *Install dependencies*
5. ``deactivate`` *Deactivate when you are done*

If you just want to use it:

``pip install xlseries`` in your environment, instead of cloning and pip
installing in developer mode.

Quick start
-----------

.. code:: python

    from xlseries import XlSeries
    xl = XlSeries("path_to_excel_file" or openpyxl.Workbook instance)
    dfs = xl.get_data_frames("path_to_json_parameters" or parameters_dictionary)

With the test case number 1:

.. code:: python

    from xlseries import XlSeries
    from xlseries.utils.path_finders import get_orig_cases_path, get_param_cases_path

    # this will only work if you clone the repo with all the test files
    path_to_excel_file = get_orig_cases_path(1)
    path_to_json_parameters = get_param_cases_path(1)

    xl = XlSeries(path_to_excel_file)
    dfs = series.get_data_frames(path_to_json_parameters)

or passing only the critical parameters as a dictionary:

.. code:: python

    parameters_dictionary = {
        "headers_coord": ["B1","C1"],
        "data_starts": 2,
        "frequency": "M",
        "time_header_coord": "A1"
    }
    dfs = xl.get_data_frames(parameters_dictionary)

you can specify what worksheet you want to scrape (otherwise the first
one will be used):

.. code:: python

    dfs = xl.get_data_frames(parameters_dictionary, ws_name="my_worksheet")

you can ask an XlSeries object for a template dictionary of the critical
parameters you need to fill:

.. code:: python

    >>> params = xl.critical_params_template()
    >>> params
    {'data_starts': 2,
     'frequency': 'M',
     'headers_coord': ['B1', 'C1', 'E1-G1'],
     'time_header_coord': 'A1'}
    >>> params["headers_coord"] = ["B1","C1"]
    >>> dfs = xl.get_data_frames(params, ws_name="my_worksheet")

if this doesn't work and you want to see exactly where the scraping is
failing, you may want to fill out all the parameters and try again to
see where the exception is raised:

.. code:: python

    >>> params = xl.complete_params_template()
    >>> params
    {'alignment': u'vertical',
     'blank_rows': False,
     'continuity': True,
     'data_ends': None,
     'data_starts': 2,
     'frequency': 'M',
     'headers_coord': ['B1', 'C1', 'E1-G1'],
     'missing_value': [None, '-', '...', '.', ''],
     'missings': False,
     'series_names': None,
     'time_alignment': 0,
     'time_composed': False,
     'time_header_coord': 'A1',
     'time_multicolumn': False}
    >>> params["headers_coord"] = ["B1","C1"]
    >>> params["data_ends"] = 256
    >>> params["missings"] = True
    >>> dfs = xl.get_data_frames(params, ws_name="my_worksheet")

-  **Excel file**: Up to this development point the excel file should
   not be more *complicated* than the `7 test cases <https://github.com/abenassi/xlseries#test-cases>`__:

-  **Parameters**: Together with the excel file, some parameters about
   the series must be provided. These could be passed to
   get\_data\_frames() as a path to a *JSON file* or as a *python
   dictionary*. ``xlseries`` use about 14 parameters to characterize the
   time series of a spreadsheet, but only 4 of them are *critical* most
   of the time: the rest can be guessed by the package. The only
   difference between specifying more or less parameters than the 4
   critical is the total time that ``xlseries`` will need to complete
   the task (more parameters, less time). Go to the `parameters <https://github.com/abenassi/xlseries#parameters>`__ section for a more detailed
   explanation about how to use them, and when you need to specify more
   than the basic 4 (``headers_coord``, ``data_starts``, ``frequency``
   and ``time_header_coord``).

Take a look to this `ipython notebook
template <https://github.com/abenassi/xlseries/blob/master/docs/notebooks/Example%20use%20case.ipynb>`__ to get started!.

If you want to dig inside the test cases and get an idea of how far is
going ``xlseries`` at the moment, check out this `ipython notebook with
the 7 test cases <https://github.com/abenassi/xlseries/blob/master/docs/notebooks/Test%20cases.ipynb>`__.

For more details go to the official repository on github:
https://github.com/abenassi/xlseries
