/*                                                         
** Copyright (C) 2008 Ricard Marxer <email@ricardmarxer.com>
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

#include "Typedefs.h"
#include "Debug.h"

#include <vector>

#include "LowPass.h"
#include "Utils.h"

using namespace std;
using namespace Eigen;

LowPass::LowPass( int order, Real freq, Real rippleDB, int channels, FilterType filterType) : 
  _order(order),
  _freq(freq),
  _rippleDB(rippleDB),
  _channels(channels),
  _filter(channels),
  _filterType(filterType)
                                                                                           
{
  DEBUG("LOWPASS: Constructor order: " << order << 
        ", freq: " << freq << 
        ", rippleDB: " << rippleDB );

  if ( order < 1 ) {
    // Throw an exception
  }
  
  setup();
  
  DEBUG("LOWPASS: Constructed");
}

void LowPass::setup(){
  DEBUG("LOWPASS: Setting up...");

  DEBUG("LOWPASS: Getting zpk");  
  // Get the lowpass z, p, k
  MatrixXC zeros, poles;
  Real gain;

  switch( _filterType ){
  case CHEBYSHEVI:
    chebyshev1(_order, _rippleDB, _channels, &zeros, &poles, &gain);
    break;

  case CHEBYSHEVII:
    chebyshev2(_order, _rippleDB, _channels, &zeros, &poles, &gain);
    break;
  }
  
  DEBUG("LOWPASS: zeros:" << zeros );
  DEBUG("LOWPASS: poles:" << poles );
  DEBUG("LOWPASS: gain:" << gain );
  
  // Convert zpk to ab coeffs
  MatrixXC a;
  MatrixXC b;
  zpkToCoeffs(zeros, poles, gain, &b, &a);

  DEBUG("LOWPASS: Calculated the coeffs");

  // Since we cannot create matrices of Nx0
  // we have created at least one Zero in 0
  if ( zeros == MatrixXC::Zero(zeros.rows(), zeros.cols()) ){
    // Now we must remove the last coefficient from b
    MatrixXC temp = b.block(0, 0, b.rows(), b.cols()-1);
    b = temp;
  }

  // Get the warped critical frequency
  Real fs = 2.0;
  Real warped = 2.0 * fs * tan( M_PI * _freq / fs );
  
  // Warpped coeffs
  MatrixXC wa;
  MatrixXC wb;
  lowPassToLowPass(b, a, warped, &wb, &wa);

  DEBUG("LOWPASS: Calculated the low pass to low pass");
  
  // Digital coeffs
  MatrixXR da;
  MatrixXR db;
  bilinear(wb, wa, fs, &db, &da);
  
  DEBUG("LOWPASS: setup the coeffs");

  // Set the coefficients to the filter
  _filter.setA( da.transpose() );
  _filter.setB( db.transpose() );
  
  _filter.setup();
  
  DEBUG("LOWPASS: Finished set up...");
}

void LowPass::a(MatrixXR* a) {
  _filter.a(a);
}

void LowPass::b(MatrixXR* b) {
  _filter.b(b);
}

void LowPass::process(MatrixXR samples, MatrixXR* filtered) {
  _filter.process(samples, filtered);
}

void LowPass::reset(){
  // Initial values
  _filter.reset();
}