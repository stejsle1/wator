WaTor
=====

WaTor is simulation of sea world with fishs and sharks.


Install
-------

To install module run:

.. code:: Python

   # to install requirements
   python -m pip install -r requirements.txt
   # to install module
   python setup.py develop
  
GUI
---

WaTor allow to run application with graphical user interface (GUI). 

To run GUI type:

.. code:: Python

    python -m wator


GUI allow to save and open simulation or create new one - all by clicking on 'File' menu ale picking one of listed buttons.
Button 'Next chronon' run function `tick()`, button 'Simulation' run function `tick()` 10 times (like real-life simulation).
Button 'About' in menu 'Help' print out a window with information about application.
Button 'Quit' exits the application.

License
-------

This project is licensed under the CCO License - see LICENSE file for more information.
