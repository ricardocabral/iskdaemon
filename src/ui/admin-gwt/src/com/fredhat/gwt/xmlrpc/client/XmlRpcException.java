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
 * The standard application-level exception.  This is usually thrown
 * if there is a transmission problem with the XMLRPC request or response 
 * (either by something like a server connect error, malformed XML, or
 * valid XML that doesn't follow the XMLRPC specs).
 * 
 * @author Fred Drake
 *
 */
public class XmlRpcException extends Exception {
	private int code = 0;
	
	/**
	 * Creates an empty XmlRpcException object
	 *
	 */
	public XmlRpcException() {
		super();
	}

	/**
	 * Creates an {@link XmlRpcException} object with a specified message
	 * @param message the descriptive exception message
	 */
	public XmlRpcException(String message) {
		super(message);
	}

	/**
	 * Creates an {@link XmlRpcException} object with a specified message
	 * and custom XML-RPC fail code number.
	 * @param code
	 * @param message
	 */
	public XmlRpcException(int code, String message) {
		super(message);
		this.code = code;
	}

	/**
	 * Creates an {@link XmlRpcException} object with a specified throwable
	 * @param t the preceding throwable
	 */
	public XmlRpcException(Throwable t) {
		super(t);
	}

	/**
	 * Creates an {@link XmlRpcException} object with a specified message
	 * and preceding throwable
	 * @param message the descriptive exception message
	 * @param t the preceding throwable
	 */
	public XmlRpcException(String message, Throwable t) {
		super(message, t);
	}

	/**
	 * Creates an {@link XmlRpcException} object with a specified XMLRPC fault
	 * code, message, and throwable.
	 * @param code the XMLRPC fault code
	 * @param message the descriptive exception message
	 * @param t the preceding throwable
	 */
	public XmlRpcException(int code, String message, Throwable t) {
		super(message, t);
		this.code = code;
	}

	/**
	 * Fetches the XMLRPC fault code, or zero if none exists.
	 * @return the numeric fault code
	 */
	public int getCode() {
		return code;
	}
}
