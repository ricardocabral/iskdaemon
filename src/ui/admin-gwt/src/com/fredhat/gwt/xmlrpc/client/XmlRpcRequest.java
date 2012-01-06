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

import java.util.*;

import com.google.gwt.http.client.*;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.xml.client.*;
import com.google.gwt.xml.client.impl.DOMParseException;

/**
 * This is the class that handles each particular XML-RPC request.  After you
 * have built your {@link XmlRpcClient} object (which contains static information
 * specific to an XML-RPC server such as URL, potential username and password, etc)
 * you will feed this information into the constructor along with the information
 * specific to your method call.
 * @author Fred Drake
 *
 * @param &lt;T&gt; The return value type of the method that you are executing (Integer, 
 * String, Map, etc).  Legal values are as follows:
 * <table border=1>
 * <tr><th>Java Type</th><th>XML Tag Name</th><th>Description</th></tr>
 * <tr><td>{@link Integer}</td><td>i4 or int</td><td>32-bit signed non-null integer value</td></tr>
 * <tr><td>{@link Boolean}</td><td>boolean</td><td>Non-null boolean value (0, or 1)</td></tr>
 * <tr><td>{@link String}</td><td>string</td><td>A non-null string</td></tr>
 * <tr><td>{@link Double}</td><td>double</td><td>A signed, non-null double precision floating point number (64 bit)</td></tr>
 * <tr><td>{@link com.fredhat.gwt.xmlrpc.client.Date}</td><td>dateTime.iso8601</td><td>A pseudo ISO8601 timestamp</td></tr>
 * <tr><td>{@link com.fredhat.gwt.xmlrpc.client.Base64}</td><td>base64</td><td>A base64 encoded string</td></tr>
 * <tr><td>{@link java.util.Map}</td><td>struct</td><td>A key value pair.  The keys are strings, and the values may be any valid data type</td></tr>
 * <tr><td>{@link java.util.List}</td><td>array</td><td>An array of objects, which may be of any valid data type</td></tr>
 * <tr><td><code>null</code></td><td>nil</td><td>A null value (only supported from XMLRPC servers with the nil extension</td></tr>
 * </table>
 * 
 * @since XMLRPC-GWT 1.1
 * @author Fred Drake
 */
public class XmlRpcRequest<T> implements Cloneable {
	private XmlRpcClient client;
	private String methodName;
	private Object[] params;
	private AsyncCallback<T> callback;
	
	/**
	 * The general constructor for an {@link XmlRpcRequest} object
	 * @param client The object containing XML-RPC server specific information
	 * @param methodName The name of the XML-RPC method that you are invoking
	 * @param params The array of input parameters for your XML-RPC method.  
	 * If this is null, it will assume no parameters.  
	 * @param callback The asynchronous callback class instantiation which handles
	 * business logic on both success and failure of the XML-RPC method invocation.
	 */
	public XmlRpcRequest(XmlRpcClient client, String methodName,  
			Object[] params, AsyncCallback<T> callback) {
		this.client = client;
		this.methodName = methodName;
		this.callback = callback;		
		this.params = params;
	}
	
	/**
	 * Invokes the XML-RPC method asynchronously.  All success and failure logic will
	 * be in your {@link AsyncCallback} that you defined in the constructor.
	 */
	public void execute() {
		if (methodName == null || methodName.equals("")) {
			callback.onFailure(new XmlRpcException(
					"The method name parameter cannot be null"));
			return;
		}
		if (params == null)
			params = new Object[]{};
		
		Document request = buildRequest(methodName, params);
		if (client.getDebugMode())
			System.out.println(
					"** Request **\n"+request+"\n*************");
		
		RequestBuilder requestBuilder = new RequestBuilder(
				RequestBuilder.POST, client.getServerURL());
		requestBuilder.setHeader("Content-Type", "text/xml");
		requestBuilder.setTimeoutMillis(client.getTimeoutMillis());
		if (client.getUsername() != null)
			requestBuilder.setUser(client.getUsername());
		if (client.getPassword() != null)
			requestBuilder.setPassword(client.getPassword());
		
		try {
			requestBuilder.sendRequest(request.toString(), new RequestCallback(){
				public void onResponseReceived(Request req, Response res) {
					if (res.getStatusCode() != 200) {
						callback.onFailure(new XmlRpcException("Server returned "+
								"response code "+res.getStatusCode()+" - "+
								res.getStatusText()));
						return;
					}
					try {
						T responseObj = buildResponse(res.getText());
						callback.onSuccess(responseObj);
					} catch (XmlRpcException e) {
						callback.onFailure(e);
					} catch (ClassCastException e) {
						callback.onFailure(e);
					}
				}
				
				public void onError(Request req, Throwable t) {
					callback.onFailure(t);
				}
			});
		} catch (RequestException e) {
			callback.onFailure(new XmlRpcException(
					"Couldn't make server request", e));
		}
	}

	/**
	 * Returns a copy of the {@link XmlRpcRequest} object
	 */
	public Object clone() {
		XmlRpcRequest<T> req = new XmlRpcRequest<T>(this.client, this.methodName,
				this.params, this.callback);
		return req;
	}
	
	// Builds the XML request structure
	private Document buildRequest(String methodName, Object[] params) {
		Document request = XMLParser.createDocument();
		Element methodCall = request.createElement("methodCall");
		{
			Element methodNameElem = request.createElement("methodName");
			methodNameElem.appendChild(request.createTextNode(methodName));
			methodCall.appendChild(methodNameElem);
		}
		{
			Element paramsElem = request.createElement("params");
			for(int i=0; i<params.length; i++) {
				Element paramElem = request.createElement("param");
				paramElem.appendChild(buildValue(params[i]));
				paramsElem.appendChild(paramElem);
				
			}
			methodCall.appendChild(paramsElem);
		}		
		request.appendChild(methodCall);
		
		return request;
	}

	// Builds an individual parameter and sends it back through the StringBuffer
	private Element buildValue(Object param) {
		Document doc = XMLParser.createDocument();
		Element valueElem = doc.createElement("value");
		
		if (param == null) {
			Element nilElem = doc.createElement("nil");
			valueElem.appendChild(nilElem);
		} else if (param instanceof Integer) {
			Element intElem = doc.createElement("int");
			intElem.appendChild(doc.createTextNode(param.toString()));
			valueElem.appendChild(intElem);
		} else if (param instanceof Boolean) {
			Element boolElem = doc.createElement("boolean");			
			boolean b = ((Boolean)param).booleanValue();
			if (b)
				boolElem.appendChild(doc.createTextNode("1"));
			else
				boolElem.appendChild(doc.createTextNode("0"));
			valueElem.appendChild(boolElem);
		} else if (param instanceof String) {
			Element stringElem = doc.createElement("string");
			stringElem.appendChild(doc.createTextNode(param.toString()));
			valueElem.appendChild(stringElem);
		} else if (param instanceof Double) {
			Element doubleElem = doc.createElement("double");
			doubleElem.appendChild(doc.createTextNode(param.toString()));
			valueElem.appendChild(doubleElem);
		} else if (param instanceof com.fredhat.gwt.xmlrpc.client.Date) {
			com.fredhat.gwt.xmlrpc.client.Date date = 
				(com.fredhat.gwt.xmlrpc.client.Date) param;
			Element dateElem = doc.createElement("dateTime.iso8601");
			dateElem.appendChild(doc.createTextNode(dateToISO8601(date)));
			valueElem.appendChild(dateElem);
		} else if (param instanceof Base64) {
			Element base64Elem = doc.createElement("base64");
			base64Elem.appendChild(doc.createTextNode(param.toString()));
			valueElem.appendChild(base64Elem);
		} else if (param instanceof Map) {
			@SuppressWarnings("unchecked")
			Map<String,Object> map = (Map<String,Object>) param;
			Element mapElem = doc.createElement("struct");
			
			for(Iterator<String> iter = map.keySet().iterator(); iter.hasNext();) {
				Object key = iter.next();
				Element memberElem = doc.createElement("member");
				{
					Element nameElem = doc.createElement("name");
					nameElem.appendChild(doc.createTextNode(key.toString()));
					memberElem.appendChild(nameElem);
				}
				{
					Element innerValueElem = buildValue(map.get(key));
					memberElem.appendChild(innerValueElem);
				}
				
				mapElem.appendChild(memberElem);
			}
			
			valueElem.appendChild(mapElem);
		} else if (param instanceof List) {
			@SuppressWarnings("unchecked")
			List<Object> list = (List<Object>) param;
			Element listElem = doc.createElement("array");
			{
				Element dataElem = doc.createElement("data");
				for(Iterator<Object> iter = list.iterator(); iter.hasNext();) {
					Element innerValueElem = buildValue(iter.next());
					dataElem.appendChild(innerValueElem);
				}
				listElem.appendChild(dataElem);
			}
			
			valueElem.appendChild(listElem);
		}
		
		return valueElem;
	}

	// Converts a com.gwt.components.client.xmlrpc.Date to the 
	// pseudo ISO8601 date format
	@SuppressWarnings("deprecation")
	private String dateToISO8601(com.fredhat.gwt.xmlrpc.client.Date date) {
		// The GWT Date object is just a wrapper, 
		// so these deprecated methods are okay.
		int year = date.getYear() + 1900;
		int month = date.getMonth() + 1;
		int day = date.getDate();
		int hour = date.getHours();
		int minute = date.getMinutes();
		int second = date.getSeconds();
		
		StringBuffer sb = new StringBuffer();
		sb.append(dateString(year, 4)).append(dateString(month, 2));
		sb.append(dateString(day, 2)).append("T");
		sb.append(dateString(hour, 2)).append(":");
		sb.append(dateString(minute, 2)).append(":");
		sb.append(dateString(second, 2));
		
		return sb.toString();
	}

	// Converts a pseudo ISO8601 date format to a 
	// com.gwt.components.client.xmlrpc.Date object
	@SuppressWarnings("deprecation")
	private Date iso8601ToDate(String dateString) throws XmlRpcException {
		// We need the format 19980717T14:08:55
		int year;
		int month;
		int day;
		int hour;
		int minute;
		int second;
		com.fredhat.gwt.xmlrpc.client.Date dateObj = new Date();
		
		if (dateString.length() != 17)
			throw new XmlRpcException("Datetime value "+dateString+
					" is not in XMLRPC ISO8601 Format");
		
		try {
			year = Integer.parseInt(dateString.substring(0, 4));
			month = Integer.parseInt(dateString.substring(4, 6));
			day = Integer.parseInt(dateString.substring(6, 8));
			hour = Integer.parseInt(dateString.substring(9, 11));
			minute = Integer.parseInt(dateString.substring(12, 14));
			second = Integer.parseInt(dateString.substring(15));
		} catch (NumberFormatException e) {
			throw new XmlRpcException("Datetime value "+dateString+
					" is not in XMLRPC ISO8601 Format");
		}
		
		// The GWT Date object is just a wrapper, 
		// so these deprecated methods are okay.
		dateObj.setYear(year - 1900);
		dateObj.setMonth(month - 1);
		dateObj.setDate(day);
		dateObj.setHours(hour);
		dateObj.setMinutes(minute);
		dateObj.setSeconds(second);
		
		return dateObj;
	}

	// Parses the servers XML response and constructs the proper return object. 
	private T buildResponse(String responseText) throws XmlRpcException {
		if (client.getDebugMode())
			System.out.println(
					"** Response **\n"+responseText+"\n**************");
		Document doc = null;
		try {
			doc = XMLParser.parse(responseText);
		} catch (DOMParseException e) {
			throw new XmlRpcException("Unparsable response", e);
		}
		
		Element methodResponse = doc.getDocumentElement();
		if (!methodResponse.getNodeName().equals("methodResponse"))
			throw new XmlRpcException(
					"The document element must be named \"methodResponse\" "+
					"(this is "+methodResponse.getNodeName()+")");
		if (getElementNodeCount(methodResponse.getChildNodes()) != 1)
			throw new XmlRpcException(
					"There may be only one element under <methodResponse> "+
					"(this has "+getElementNodeCount(
					methodResponse.getChildNodes())+")");
			
		Element forkNode = getFirstElementChild(methodResponse);
		if (forkNode.getNodeName().equals("fault")) {
			if (getElementNodeCount(forkNode.getChildNodes()) != 1)
				throw new XmlRpcException("The <fault> element must have "+
						"exactly one child");
			Element valueNode = getFirstElementChild(forkNode);
			Object faultDetailsObj = getValueNode(valueNode);
			if (!(faultDetailsObj instanceof Map))
				throw new XmlRpcException("The <fault> element must be a <struct>");
			@SuppressWarnings("unchecked")
			Map<String,Object> faultDetails = (Map<String,Object>) faultDetailsObj;
			if (faultDetails.get("faultCode") == null || 
					faultDetails.get("faultString") == null || 
					!(faultDetails.get("faultCode") instanceof Integer))
				throw new XmlRpcException("The <fault> element must contain "+
						"exactly one <struct> with an integer \"faultCode\" and "+
						"a string \"faultString\" value");
			int faultCode = ((Integer) faultDetails.get("faultCode")).intValue();
			throw new XmlRpcException(faultCode, 
					faultDetails.get("faultString").toString(), null);
		} else if (!forkNode.getNodeName().equals("params"))
			throw new XmlRpcException("The <methodResponse> must contain either "+
					"a <params> or <fault> element.");

		// No return object is allowed
		Element paramNode = getFirstElementChild(forkNode);
		if (paramNode == null)
			return null;
		if (!paramNode.getNodeName().equals("param") || 
				getElementNodeCount(paramNode.getChildNodes()) < 1)
			throw new XmlRpcException("The <params> element must contain "+
					"one <param> element");
		Node valueNode = getFirstElementChild(paramNode);
		
		return getValueNode(valueNode);
	}
	
	// Fetches the proper java object from an XML node
	@SuppressWarnings("unchecked")
	private T getValueNode(Node node) throws XmlRpcException {
		if (!node.getNodeName().equals("value"))
			throw new XmlRpcException("Value node must be named <value>, not "+
					"<"+node.getNodeName()+">");
		if (getElementNodeCount(node.getChildNodes()) == 0) {
			// If no type is indicated, the type is string.
			String strValue = getNodeTextValue(node);
			return (T)(strValue == null ? "" : strValue);
		}
		if (getElementNodeCount(node.getChildNodes()) != 1)
			throw new XmlRpcException("A <value> node must have exactly one child");
		Node valueType = getFirstElementChild(node);
		if (valueType.getNodeName().equals("i4") || 
				valueType.getNodeName().equals("int")) {
			String intValueString = getNodeTextValue(valueType);
			if (intValueString == null)
				throw new XmlRpcException("Integer child is not a text node");
			try {
				return (T)(new Integer(intValueString));
			} catch (NumberFormatException e) {
				throw new XmlRpcException("Value \""+intValueString+"\" is not"+
						" an integer");
			}
		} else if (valueType.getNodeName().equals("boolean")) {
			String boolValue = getNodeTextValue(valueType);
			if (boolValue == null)
				throw new XmlRpcException("Child of <boolean> is not a text node");
			if (boolValue.equals("0"))
				return (T)(new Boolean(false));
			else if (boolValue.equals("1"))
				return (T)(new Boolean(true));
			else
				throw new XmlRpcException("Value \""+boolValue+"\" must be 0 or 1");
		} else if (valueType.getNodeName().equals("string")) {
			String strValue = getNodeTextValue(valueType);
			if (strValue == null)
				strValue = ""; // Make sure <string/> responses will exist as empty
			return (T)strValue;
		} else if (valueType.getNodeName().equals("double")) {
			String doubleValueString = getNodeTextValue(valueType);
			if (doubleValueString == null)
				throw new XmlRpcException("Child of <double> is not a text node");
			try {
				return (T)(new Double(doubleValueString));
			} catch (NumberFormatException e) {
				throw new XmlRpcException("Value \""+doubleValueString+
						"\" is not a double");
			}
		} else if (valueType.getNodeName().equals("dateTime.iso8601")) {
			String dateValue = getNodeTextValue(valueType);
			if (dateValue == null)
				throw new XmlRpcException("Child of <dateTime> is not a text node");
			try {
				return (T)iso8601ToDate(dateValue);
			} catch (XmlRpcException e) {
				throw new XmlRpcException(e.getMessage());
			}
		} else if (valueType.getNodeName().equals("base64")) {
			String baseValue = getNodeTextValue(valueType);
			if (baseValue == null)
				throw new XmlRpcException("Improper XML-RPC response format");
			return (T)new Base64(baseValue);
		} else if (valueType.getNodeName().equals("struct")) {
			@SuppressWarnings("unchecked")
			Map<String,Object> map = new HashMap<String,Object>(
					getElementNodeCount(valueType.getChildNodes()));
			for(int i=0; i<valueType.getChildNodes().getLength(); i++) {
				if (valueType.getChildNodes().item(i).getNodeType() !=
						Node.ELEMENT_NODE)
					continue;
				Element memberNode = (Element) valueType.getChildNodes().item(i);
				String name = null;
				Object value = null;
				if (!memberNode.getNodeName().equals("member"))
					throw new XmlRpcException("Children of <struct> may only be "+
							"named <member>");
				// NodeList.getElementsByTagName(String) does a deep search, so we
				// can legally get more than one back.  Therefore, if the response
				// has more than one <name/> and <value/> at it's highest level,
				// we will only process the first one it comes across.
				if (memberNode.getElementsByTagName("name").getLength() < 1)
					throw new XmlRpcException("A <struct> element must contain "+
							"at least one <name> child");
				if (memberNode.getElementsByTagName("value").getLength() < 1)
					throw new XmlRpcException("A <struct> element must contain "+
							"at least one <value> child");
				
				name = getNodeTextValue(memberNode.getElementsByTagName(
						"name").item(0));
				value = getValueNode(memberNode.getElementsByTagName(
						"value").item(0));
				if (name == null)
					throw new XmlRpcException("The <name> element must "+
							"contain a string value");
				map.put(name, value);
			}
			
			return (T)map;
		} else if (valueType.getNodeName().equals("array")) {
			if (getElementNodeCount(valueType.getChildNodes()) != 1)
				throw new XmlRpcException("An <array> element must contain "+
						"a single <data> element");
			Node dataNode = getFirstElementChild(valueType);
			if (!dataNode.getNodeName().equals("data"))
				throw new XmlRpcException("An <array> element must contain "+
						"a single <data> element");
			List<Object> list = new ArrayList<Object>();
			for(int i=0; i<dataNode.getChildNodes().getLength(); i++) {
				Node valueNode = dataNode.getChildNodes().item(i);
				if (valueNode.getNodeType() != Node.ELEMENT_NODE)
					continue;
				if (!valueNode.getNodeName().equals("value"))
					throw new XmlRpcException("Children of <data> may only be "+
							"<value> elements");
				list.add(getValueNode(valueNode));
			}
			
			return (T)list;
		} else if (valueType.getNodeName().equals("nil")) {
			return null;
		}
		
		// Not sure what it was supposed to be
		throw new XmlRpcException("Improper XML-RPC response format:"+
				" Unknown node name \""+valueType.getNodeName()+"\"");
	}

	// Quick utility method to help properly format the pseudo ISO8601 date. 
	private String dateString(int number, int places) {
		String numStr = new Integer(number).toString();
		StringBuffer sb = new StringBuffer();
		places -= numStr.length();
		for(int i=0; i<places; i++) {
			sb.append("0");
		}
		sb.append(numStr);
		
		return sb.toString();
	}	

	// Quick utility method to achieve the text value of a node without having to
	// traverse one more level deep each time.  Similar in feel to JDOM's 
	// convenience method.
	private String getNodeTextValue(Node node) {
		if (node.getChildNodes().getLength() != 1)
			return null;
		Node textNode = (Node) node.getFirstChild();
		if (textNode.getNodeType() != Node.TEXT_NODE)
			return null;
		
		return textNode.getNodeValue();
	}

	// Fetches the number of element nodes in a node list.
	private int getElementNodeCount(NodeList nodeList) {
		int elements = 0;
		for(int i=0; i<nodeList.getLength(); i++) {
			Node node = nodeList.item(i);
			if (node.getNodeType() == Node.ELEMENT_NODE)
				elements++;
		}
		
		return elements;
	}

	// Acts just like Node.getFirstChild() except this returns the first
	// child that is an element node.
	private Element getFirstElementChild(Node parentNode) {
		NodeList children = parentNode.getChildNodes();
		for(int i=0; i<children.getLength(); i++) {
			Node node = children.item(i);
			if (node.getNodeType() == Node.ELEMENT_NODE)
				return (Element)node;
		}
		
		return null;
	}
}
