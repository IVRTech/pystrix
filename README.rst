**pystrix** is an attempt at creating a versatile `Asterisk <http://www.asterisk.org/>`_-interface package for AMI and (Fast)AGI needs. It is published as an open-source library under the LGPLv3 by `Ivrnet, inc. <http://www.ivrnet.com/>`_, welcoming contributions from all users.

****

========
Overview
========

pystrix runs on python 2.7/python 3.4+ on any platform. It's targeted at Asterisk 1.10+ and provides a rich, easy-to-extend set of bindings for AGI, FastAGI, and AMI.

================
Release Schedule
================

The current code in the repository correspond to version **1.1.8** of the package.  When a bug is found and fixed a new version of the package will be generated in order to keep it updated and as bug-free as possible.

New releases will follow the format: <release mayor>.<release minor>.<bug fixed> according to the change made to the code.

=======
History
=======

After some research, we found that what was available was either incompatible with the architecture model we needed to work with `Twisted <http://www.twistedmatrix.org/>`_, (while excellent for a great many things, isn't always the right choice), was targeting an outdated version of Asterisk, or had a very rigid, monolithic design. Identifying the `pyst <http://pyst.sourceforge.net/>`_ and `py-asterisk <http://code.google.com/p/py-asterisk/>`_ packages as being similar, but structurally incompatible, to what we wanted, pyst was chosen as the basis for this project, with a full rewrite of its AGI and AMI systems to provide a uniform-looking, highly modular design that incorporates logic and ideas from py-asterisk. The end result is a package that should satisfy anyone who was looking at either of its ancestors and that should be easier to extend as Asterisk continues to evolve.

============
Installation
============

* From pip

.. code:: bash

    $ pip install pystrix

* From github

.. code:: bash

    $ pip install -e git://github.com/marsoguti/pystrix.git#egg=pystrix

=====
Usage
=====

Detailed usage information is provided in the documentation, along with simple examples that should help to get anyone started.

=============
Documentation
=============

Online documentation is available at http://pystrix.readthedocs.io/.

Inline documentation is complete and made readable by `reStructuredText <http://docutils.sourceforge.net/rst.html>`_, so you'll never be completely lost.

****

=======
Credits
=======

`Ivrnet, inc. <http://www.ivrnet.com/>`_
 * Initial development of pystrix was funded by Ivrnet
 * Ivrnet is a software-as-a-service company that develops and operates intelligent software applications, delivered through traditional phone networks and over the Internet. These applications facilitate automated interaction, personalized communication between people, mass communication for disseminating information to thousands of people concurrently, and personalized communication between people and automated systems. Ivrnet's applications are accessible through nearly any form of communication technology, at any time, from anywhere in North America, via voice, phone, fax, email, texting, and the Internet.

`Neil Tallim <http://uguu.ca/>`_
 * Development lead
 * Programming


Other contributions and current package maintenance
---------------------------------------------------

`Marta Solano <marta.solano@ivrtechnology.com>`_
 * Bug solving - Programming
 * Pip package maintenance

`Eric Lee <eric@ivrtechnology.com>`_
 * Python 2 to 3 migration - compatibility
 * Programming

`Karthic Raghupathi <karthicr@ivrtechnology.com>`_
 * Bug solving - Programming
 * Pip package maintenance
