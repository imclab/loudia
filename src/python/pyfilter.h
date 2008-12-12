/*                                                         
** Copyright (C) 2008 Ricard Marxer <email@ricardmarxer.com.com>
**                                                                  
** This program is free software; you can redistribute it and/or modify
** it under the terms of the GNU General Public License as published by
** the Free Software Foundation; either version 2 of the License, or   
** (at your option) any later version.                                 
**                                                                     
** This program is distributed in the hope that it will be useful,     
** but WITHOUT ANY WARRANTY; without even the implied warranty of      
** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       
** GNU General Public License for more details.                        
**                                                                     
** You should have received a copy of the GNU General Public License   
** along with this program; if not, write to the Free Software         
** Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
*/                                                                          

#ifndef CRICAUDIO_PYTHON_PYFILTER_H
#define CRICAUDIO_PYTHON_PYFILTER_H

#include <Python.h>
#include "filter.h"

class PyFilter {
public:
  PyObject_HEAD
  Filter::Filter* base;

  /* Basic Memory Management */
  static PyObject* make_new(PyTypeObject* type, PyObject* args, PyObject* kwds) {
    return (PyObject*)(type->tp_alloc(type, 0));
  }
  
  static void dealloc(PyObject* self) {
    delete ((PyFilter*)self)->base;
    self->ob_type->tp_free((PyObject*)self);
  }
  
  static int init(PyObject* self, PyObject* args, PyObject* kwds);

  static PyObject* make_new_from_data(PyTypeObject* type, PyObject* args,
                                      PyObject* kwds, Filter::Filter* data) {
    PyFilter* self = (PyFilter*)make_new(type, args, kwds);
    self->base = data;
    return (PyObject*)self;
  }

  static PyObject* process(PyObject* self, PyObject* args);
};

#endif // CRICAUDIO_PYTHON_PYFILTER_H
