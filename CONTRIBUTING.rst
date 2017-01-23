.. -*- mode: rst; fill-column: 80 -*-

============
Contributing
============

Thank you for considering contributing to **ndeflib**. There are many
ways to help and any help is welcome.


Reporting issues
================

- Under which versions of Python does this happen? This is especially
  important if your issue is encoding related.

- Under which version of **ndeflib** does this happen? Check if this
  issue is fixed in the repository.


Submitting patches
==================

- Include tests if your patch is supposed to solve a bug, and explain
  clearly under which circumstances the bug happens. Make sure the
  test fails without your patch.

- Include or update tests and documentation if your patch is supposed
  to add a new feature. Note that documentation is in two places, the
  code itself for rendering help pages and in the docs folder for the
  online documentation.

- Follow `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_ and
  `PEP 257 <https://www.python.org/dev/peps/pep-0257/>`_.


Development tips
================

- `Fork <http://guides.github.com/activities/forking/>`_ the
  repository and clone it locally::

    git clone git@github.com:your-username/ndeflib.git
    cd ndeflib

- Create virtual environments for Python 2 an Python 3, setup the
  ndeftool package in develop mode, and install required development
  packages::

    virtualenv python-2
    python3 -m venv python-3
    source python-2/bin/activate
    python setup.py develop
    pip install -r requirements-dev.txt
    source python-3/bin/activate
    python setup.py develop
    pip install -r requirements-dev.txt

- Verify that all tests pass and the documentation is build::

    tox

- Preferably develop in the Python 3 virtual environment. Running
  ``tox`` ensures tests are run with both the Python 2 and Python 3
  interpreter but it takes some time to complete. Alternatively switch
  back and forth between versions and just run the tests::

    source python-2/bin/activate
    py.test
    source python-3/bin/activate
    py.test

- Test coverage should be close to 100 percent. A great help is the
  HTML output produced by coverage.py::

    py.test --cov ndef --cov-report html
    firefox htmlcov/index.html

- The documentation can be created and viewed loacally::

    (cd docs && make html)
    firefox docs/_build/html/index.html

