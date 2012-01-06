/*
XMLRPC client for GWT
Copyright (C) 2006

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

*/

package com.fredhat.gwt.xmlrpc.client;

/**
 * This class is an extension of {@link java.util.Date} that does not use
 * milliseconds.  This conforms to the ISO8601 date standard.
 * 
 * @author Fred Drake
 *
 */
public class Date extends java.util.Date {

    /**
     * Allocates a <code>Date</code> object and initializes it so that 
     * it represents the time at which it was allocated, measured to the 
     * nearest second.
     */
	public Date() {
		super();
		makeEvenSecond();
	}

	/**
     * Allocates a <code>Date</code> object and initializes it to 
     * represent the specified number of seconds since the 
     * standard base time known as "the epoch", namely January 1, 
     * 1970, 00:00:00 GMT. 
     *
     * @param   date   the milliseconds since January 1, 1970, 00:00:00 GMT.
	 */
	public Date(long date) {
		super(date);
		makeEvenSecond();
	}
	
	/**
     * Allocates a <code>Date</code> object and initializes it so that 
     * it represents the date and time indicated by the string 
     * <code>s</code>, which is interpreted as if by the 
     * {@link Date#parse} method. 
     *
     * @param   s   a string representation of the date.
     * @see     java.text.DateFormat
     * @see     java.util.Date#parse(java.lang.String)
	 */
	@SuppressWarnings("deprecation")
	public Date(String s) {
		super(s);
		makeEvenSecond();
	}

    /**
     * Sets this <code>Date</code> object to represent a point in time that is 
     * <code>time</code> milliseconds after January 1, 1970 00:00:00 GMT.  In this
     * extension, the last three milliseconds are wiped, replaced with a perfectly
     * even second. 
     *
     * @param   time   the number of milliseconds.
     */
	@Override
	public void setTime(long time) {
		super.setTime(time);
		makeEvenSecond();
	}

	// Force a perfectly even second any time the millisecond portion of 
	// the date is being messed with.
	private void makeEvenSecond() {
		super.setTime((super.getTime()/1000)*1000);
	}
}
