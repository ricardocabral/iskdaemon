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

import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.xml.client.*;
import com.google.gwt.xml.client.impl.DOMParseException;
import com.google.gwt.http.client.*;

import java.util.*;

/**
 * This class collects information that is specific to the XML-RPC server.  It is
 * then used in an {@link XmlRpcRequest} object to invoke your XML-RPC methods.
 *
 * Quick example:
 * <pre class="code">
 * ...
 * XmlRpcClient client = new XmlRpcClient("http://www.foo.com/xmlrpcserver.php");
 * String methodName = "example.addTwoIntegers";
 * Object[] params = new Object[]{3, 4};
 * 
 * XmlRpcRequest&lt;Integer&gt; request = new XmlRpcRequest&lt;Integer&gt;(
 * 			client, methodName, params, new AsyncCallback&lt;Integer&gt;() {
 * 		public void onSuccess(Integer response) {
 * 			// Handle integer response logic here
 * 		}
 * 
 * 		public void onFailure(Throwable response) {
 * 			String failedMsg = response.getMessage();
 * 			// Put other failed response handling logic here
 * 		}
 * });
 * ...
 * </pre>
 * 
 * 
 * 
 * @author Fred Drake
 * @see XmlRpcRequest
 */
public class XmlRpcClient implements Cloneable {	
	/**
	 * The default timeout of a XMLRPC request, in milliseconds.
	 */
	public static final int DEFAULT_TIMEOUT = 10000;

	private String serverURL;
	private boolean debugMessages;
	private int timeout;
	private String username;
	private String password;

	/**
	 * Creates an XMLRPC client with the server URL
	 * @param serverURL the full URL of the XMLRPC server of which you wish to connect
	 */
	public XmlRpcClient(String serverURL) {
		this.serverURL = serverURL;
		this.debugMessages = false;
		this.timeout = DEFAULT_TIMEOUT;
		this.username = null;
		this.password = null;
	}
	
	/**
	 * Gets the XMLRPC client debug mode.  When in debug mode, the raw request and 
	 * response messages will be sent to standard output.  Note that standard output
	 * is only displayed when the application is running under hosted mode.
	 * @return true if the client is in debug mode, false otherwise.
	 */
	public boolean getDebugMode() {
		return debugMessages;
	}

	/**
	 * Sets the XMLRPC client debug mode.  When in debug mode, the raw request and 
	 * response messages will be sent to standard output.  Note that standard output
	 * is only displayed when the application is running under hosted mode.
	 * @param debugMode Set true if you want debug mode, false otherwise.
	 */
	public void setDebugMode(boolean debugMode) {
		this.debugMessages = debugMode;
	}

	/**
	 * Gets the XML-RPC server URL.  Note that this needs to be a full URL (including 
	 * the preceding "http://").
	 * @return The XML-RPC server URL
	 */
	public String getServerURL() {
		return serverURL;
	}
	
	/**
 	 * Sets the XML-RPC server URL.  Note that this needs to be a full URL (including 
	 * the preceding "http://").
	 * @param serverURL The XML-RPC server URL
	 */
	public void setServerURL(String serverURL) {
		this.serverURL = serverURL;
	}
	
	/**
	 * Gets the timeout for a method.  If this amount of time has elapsed without a
	 * return call from an XML-RPC method, the associated {@link AsyncCallback#onFailure(Throwable)}
	 * will be invoked.
	 * @return The timeout value in milliseconds
	 */
	public int getTimeoutMillis() {
		return timeout;
	}

	/**
	 * Gets the username (if one exists) associated with this client.  Only for clients that
	 * require authentication.
	 * @return The associated username, or null if one does not exist.
	 */
	public String getUsername() {
		return username;
	}
	
	/**
	 * Sets the username to be associated with this client.  This is for clients that
	 * require authentication.
	 * @param username The username for server authentication
	 */
	public void setUsername(String username) {
		this.username = username;
	}
	
	/**
	 * Gets the password (if one exists) associated with this client.  Only for clients that
	 * require authentication.
	 * @return The associated password, or null if one does not exist.
	 */
	public String getPassword() {
		return password;
	}
	
	/**
	 * Sets the password to be associated with this client.  This is for clients that
	 * require authentication.
	 * @param password The password for server authentication
	 */
	public void setPassword(String password) {
		this.password = password;
	}
	
	/**
	 * Sets the timeout of the XMLRPC request, overiding the 
	 * {@link XmlRpcClient#DEFAULT_TIMEOUT} value.  
	 * @param timeout The timeout of the request, in milliseconds.
	 */
	public void setTimeoutMillis(int timeout) {
		this.timeout = timeout;
	}
	
	/**
	 * Executes an asynchronous XMLRPC call to the server with a specified username
	 * and password.  If the execution was successful, the callback's {@link AsyncCallback#onSuccess(Object)} 
	 * method will be invoked with the return value as the argument.  If the 
	 * execution failed for any reason, the callback's {@link AsyncCallback#onFailure(Throwable)} method will 
	 * be invoked with an instance of {@link XmlRpcException} instance as it's argument.
	 * @param username the username for authentication
	 * @param password the password for authentication
	 * @param methodName the name of the XMLRPC method
	 * @param params the parameters for the XMLRPC method
	 * @param callback the logic implementation for handling the XMLRPC responses.
	 * @deprecated As of XMLRPC-GWT v1.1,
	 * build an {@link XmlRpcRequest} then call {@link XmlRpcRequest#execute()}
	 */
	@SuppressWarnings("unchecked")
	@Deprecated
	public void execute(String username, String password, String methodName, 
			Object[] params, final AsyncCallback callback) {
		if (methodName == null || methodName.equals("")) {
			callback.onFailure(new XmlRpcException(
					"The method name parameter cannot be null"));
			return;
		}
		if (params == null)
			params = new Object[0];
		
		Document request = buildRequest(methodName, params);
		if (debugMessages)
			System.out.println(
					"** Request **\n"+request+"\n*************");
		
		RequestBuilder requestBuilder = new RequestBuilder(
				RequestBuilder.POST, serverURL);
		requestBuilder.setHeader("Content-Type", "text/xml");
		requestBuilder.setTimeoutMillis(timeout);
		if (username != null)
			requestBuilder.setUser(username);
		if (password != null)
			requestBuilder.setPassword(password);
		
		try {
			requestBuilder.sendRequest(request.toString(), new RequestCallback(){
				public void onResponseReceived(Request req, Response res) {
					if (res.getStatusCode() != 200) {
						callback.onFailure(new XmlRpcException("Server returned "+
								"response code "+res.getStatusCode()+" - "+
								res.getStatusText()));
						return;
					}
					Object responseObj = buildResponse(res.getText());
					if (responseObj instanceof XmlRpcException)
						callback.onFailure((XmlRpcException)responseObj);
					else
						callback.onSuccess(responseObj);
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
	 * Executes an asynchronous XMLRPC call to the server.  If the execution was
	 * successful, the callback's {@link AsyncCallback#onSuccess(Object)} method will be invoked with the return
	 * value as the argument.  If the execution failed for any reason, the callback's
	 * {@link AsyncCallback#onFailure(Throwable)} method will be invoked with an instance of {@link XmlRpcException}
	 * as it's argument.
	 * @param methodName the name of the XMLRPC method
	 * @param params the parameters for the XMLRPC method
	 * @param callback the logic implementation for handling the XMLRPC responses.
	 * @deprecated As of XMLRPC-GWT v1.1,
	 * build an {@link XmlRpcRequest} then call {@link XmlRpcRequest#execute()}
	 */
	@SuppressWarnings("unchecked")
	@Deprecated
	public void execute(String methodName, Object[] params, 
			AsyncCallback callback) {
		this.execute(null, null, methodName, params, callback);
	}

	/**
	 * Returns a copy of the {@link XmlRpcClient} object
	 */
	public Object clone() {
		XmlRpcClient clientClone = new XmlRpcClient(this.serverURL);
		clientClone.debugMessages = this.debugMessages;
		clientClone.timeout = this.timeout;
		
		return clientClone;
	}
	
	// Builds the XML request structure
	// This is legacy logic used in the deprecated execute methods.
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
	// This is legacy logic used in the deprecated execute methods.
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
	// This is legacy logic used in the deprecated execute methods.
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
	// This is legacy logic used in the deprecated execute methods.
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
	// This is legacy logic used in the deprecated execute methods.
	private Object buildResponse(String responseText) {
		if (debugMessages)
			System.out.println(
					"** Response **\n"+responseText+"\n**************");
		Document doc = null;
		try {
			doc = XMLParser.parse(responseText);
		} catch (DOMParseException e) {
			return new XmlRpcException("Unparsable response", e);
		}
		
		Element methodResponse = doc.getDocumentElement();
		if (!methodResponse.getNodeName().equals("methodResponse"))
			return new XmlRpcException(
					"The document element must be named \"methodResponse\" "+
					"(this is "+methodResponse.getNodeName()+")");
		if (getElementNodeCount(methodResponse.getChildNodes()) != 1)
			return new XmlRpcException(
					"There may be only one element under <methodResponse> "+
					"(this has "+getElementNodeCount(
							methodResponse.getChildNodes())+")");
			
		Element forkNode = getFirstElementChild(methodResponse);
		if (forkNode.getNodeName().equals("fault")) {
			if (getElementNodeCount(forkNode.getChildNodes()) != 1)
				return new XmlRpcException("The <fault> element must have "+
						"exactly one child");
			Element valueNode = getFirstElementChild(forkNode);
			Object faultDetailsObj = getValueNode(valueNode);
			if (!(faultDetailsObj instanceof Map))
				return new XmlRpcException("The <fault> element must be a <struct>");
			@SuppressWarnings("unchecked")
			Map<String,Object> faultDetails = (Map<String,Object>) faultDetailsObj;
			if (faultDetails.get("faultCode") == null || 
					faultDetails.get("faultString") == null || 
					!(faultDetails.get("faultCode") instanceof Integer))
				return new XmlRpcException("The <fault> element must contain "+
						"exactly one <struct> with an integer \"faultCode\" and "+
						"a string \"faultString\" value");
			int faultCode = ((Integer) faultDetails.get("faultCode")).intValue();
			return new XmlRpcException(faultCode, 
					faultDetails.get("faultString").toString(), null);
		} else if (!forkNode.getNodeName().equals("params"))
			return new XmlRpcException("The <methodResponse> must contain either "+
					"a <params> or <fault> element.");

		// No return object is allowed
		Element paramNode = getFirstElementChild(forkNode);
		if (paramNode == null)
			return null;
		if (!paramNode.getNodeName().equals("param") || 
				getElementNodeCount(paramNode.getChildNodes()) < 1)
			return new XmlRpcException("The <params> element must contain "+
					"one <param> element");
		Node valueNode = getFirstElementChild(paramNode);
		
		return getValueNode(valueNode);
	}
	
	// Fetches the proper java object from an XML node
	// This is legacy logic used in the deprecated execute methods.
	private Object getValueNode(Node node) {
		if (!node.getNodeName().equals("value"))
			return new XmlRpcException("Value node must be named <value>, not "+
					"<"+node.getNodeName()+">");
		if (getElementNodeCount(node.getChildNodes()) == 0) {
			// If no type is indicated, the type is string.
			String strValue = getNodeTextValue(node);
			return strValue == null ? "" : strValue;
		}
		if (getElementNodeCount(node.getChildNodes()) != 1)
			return new XmlRpcException("A <value> node must have exactly one child");
		Node valueType = getFirstElementChild(node);
		if (valueType.getNodeName().equals("i4") || 
				valueType.getNodeName().equals("int")) {
			String intValueString = getNodeTextValue(valueType);
			if (intValueString == null)
				return new XmlRpcException("Integer child is not a text node");
			try {
				return new Integer(intValueString);
			} catch (NumberFormatException e) {
				return new XmlRpcException("Value \""+intValueString+"\" is not"+
						" an integer");
			}
		} else if (valueType.getNodeName().equals("boolean")) {
			String boolValue = getNodeTextValue(valueType);
			if (boolValue == null)
				return new XmlRpcException("Child of <boolean> is not a text node");
			if (boolValue.equals("0"))
				return new Boolean(false);
			else if (boolValue.equals("1"))
				return new Boolean(true);
			else
				return new XmlRpcException("Value \""+boolValue+"\" must be 0 or 1");
		} else if (valueType.getNodeName().equals("string")) {
			String strValue = getNodeTextValue(valueType);
			if (strValue == null)
				strValue = ""; // Make sure <string/> responses will exist as empty
			return strValue;
		} else if (valueType.getNodeName().equals("double")) {
			String doubleValueString = getNodeTextValue(valueType);
			if (doubleValueString == null)
				return new XmlRpcException("Child of <double> is not a text node");
			try {
				return new Double(doubleValueString);
			} catch (NumberFormatException e) {
				return new XmlRpcException("Value \""+doubleValueString+
						"\" is not a double");
			}
		} else if (valueType.getNodeName().equals("dateTime.iso8601")) {
			String dateValue = getNodeTextValue(valueType);
			if (dateValue == null)
				return new XmlRpcException("Child of <dateTime> is not a text node");
			try {
				return iso8601ToDate(dateValue);
			} catch (XmlRpcException e) {
				return new XmlRpcException(e.getMessage());
			}
		} else if (valueType.getNodeName().equals("base64")) {
			String baseValue = getNodeTextValue(valueType);
			if (baseValue == null)
				return new XmlRpcException("Improper XML-RPC response format");
			return new Base64(baseValue);
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
					return new XmlRpcException("Children of <struct> may only be "+
							"named <member>");
				// NodeList.getElementsByTagName(String) does a deep search, so we
				// can legally get more than one back.  Therefore, if the response
				// has more than one <name/> and <value/> at it's highest level,
				// we will only process the first one it comes across.
				if (memberNode.getElementsByTagName("name").getLength() < 1)
					return new XmlRpcException("A <struct> element must contain "+
							"at least one <name> child");
				if (memberNode.getElementsByTagName("value").getLength() < 1)
					return new XmlRpcException("A <struct> element must contain "+
							"at least one <value> child");
				
				name = getNodeTextValue(memberNode.getElementsByTagName(
						"name").item(0));
				value = getValueNode(memberNode.getElementsByTagName(
						"value").item(0));
				if (name == null)
					return new XmlRpcException("The <name> element must "+
							"contain a string value");
				map.put(name, value);
			}
			
			return map;
		} else if (valueType.getNodeName().equals("array")) {
			if (getElementNodeCount(valueType.getChildNodes()) != 1)
				return new XmlRpcException("An <array> element must contain "+
						"a single <data> element");
			Node dataNode = getFirstElementChild(valueType);
			if (!dataNode.getNodeName().equals("data"))
				return new XmlRpcException("An <array> element must contain "+
						"a single <data> element");
			List<Object> list = new ArrayList<Object>();
			for(int i=0; i<dataNode.getChildNodes().getLength(); i++) {
				Node valueNode = dataNode.getChildNodes().item(i);
				if (valueNode.getNodeType() != Node.ELEMENT_NODE)
					continue;
				if (!valueNode.getNodeName().equals("value"))
					return new XmlRpcException("Children of <data> may only be "+
							"<value> elements");
				list.add(getValueNode(valueNode));
			}
			
			return list;
		} else if (valueType.getNodeName().equals("nil")) {
			return null;
		}
		
		// Not sure what it was supposed to be
		return new XmlRpcException("Improper XML-RPC response format:"+
				" Unknown node name \""+valueType.getNodeName()+"\"");
	}

	// Quick utility method to help properly format the pseudo ISO8601 date. 
	// This is legacy logic used in the deprecated execute methods.
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
	// This is legacy logic used in the deprecated execute methods.
	private String getNodeTextValue(Node node) {
		if (node.getChildNodes().getLength() != 1)
			return null;
		Node textNode = (Node) node.getFirstChild();
		if (textNode.getNodeType() != Node.TEXT_NODE)
			return null;
		
		return textNode.getNodeValue();
	}

	// Fetches the number of element nodes in a node list.
	// This is legacy logic used in the deprecated execute methods.
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
	// This is legacy logic used in the deprecated execute methods.
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
