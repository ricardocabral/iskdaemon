/***************************************************************************
    imgSeek ::  This file is the haar 2d transform implemented in C/C++ to speed things up
                             -------------------
    begin                : Fri Jan 17 2003
    email                : nieder|at|mail.ru
    Time-stamp:            <03/05/09 21:29:35 rnc>

    Copyright (C) 2003 Ricardo Niederberger Cabral
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/
#ifndef HAAR_H
#define HAAR_H

/* STL Includes */
#include <queue>

/* Number of pixels on one side of image; required to be a power of 2. */
#define	NUM_PIXELS		128
/* Totals pixels in a square image. */
#define NUM_PIXELS_SQUARED	(NUM_PIXELS * NUM_PIXELS)
/* Number of Haar coeffients we retain as signature for an image. */
#define NUM_COEFS		40

#define UNIT_IS_DOUBLE

#undef ABS
#ifdef UNIT_IS_DOUBLE
#define ABS(x)	fabs(x)
typedef double	Unit;
#else
#define UNIT_IS_INT
#define ABS(x)	abs(x)
typedef int	Unit;
#endif

typedef int Idx;

/* signature structure */
typedef struct valStruct_{
  Unit d;			/* [f]abs(a[i]) */
  int i;			/* index i of a[i] */
  bool operator< (const valStruct_ &right) const // warning: order is inverse so valqueue is ordered smallest->biggest
  {
    return d > right.d;
  }
} valStruct;

typedef std::priority_queue < valStruct > valqueue;

#define max(a, b)  (((a) > (b)) ? (a) : (b))
#define min(a, b)  (((a) > (b)) ? (b) : (a))

void initImgBin();
void transform(Unit* a, Unit* b, Unit* c);
void transformChar(unsigned char* c1, unsigned char* c2, unsigned char* c3, Unit* a, Unit* b, Unit* c);
int calcHaar(Unit* cdata1, Unit* cdata2, Unit* cdata3, Idx* sig1, Idx* sig2, Idx* sig3, double * avgl);

#endif
