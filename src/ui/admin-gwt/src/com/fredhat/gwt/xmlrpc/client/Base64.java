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
 * This class holds an XMLRPC Base64 encoded value.
 * @author Fred Drake
 */
public class Base64 {
	private String value;

	/**
	 * Creates a Base64 object
	 * @param value The encoded string value
	 */
	public Base64(String value) {
		this.value = value;
	}

	/**
	 * Returns the encoded base64 string
	 * @return the encoded base64 string
	 */
	public String getValue() {
		return value;
	}

	/**
	 * Returns the encoded base64 string
	 */
	@Override
	public String toString() {
		return value;
	}

	/**
	 * Returns a hash code for this object
	 */
	@Override
	public int hashCode() {
		final int PRIME = 31;
		int result = 1;
		result = PRIME * result + ((value == null) ? 0 : value.hashCode());
		return result;
	}

	/**
	 * Compares this object to the specified object
	 */
	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (!(obj instanceof Base64))
			return false;
		final Base64 other = (Base64) obj;
		if (value == null) {
			if (other.value != null)
				return false;
		} else if (!value.equals(other.value))
			return false;
		return true;
	}
	
}
