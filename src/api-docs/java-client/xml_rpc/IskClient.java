/*
 * Copyright 2007 Ricardo Niederberger Cabral, all rights reserved.
 * http://server.imgseek.net/
 * 
 */
package net.imgseek.iskdaemon.xmlrpcclient;

import java.net.MalformedURLException;
import java.net.URL;

import org.apache.xmlrpc.XmlRpcException;
import org.apache.xmlrpc.client.XmlRpcClient;
import org.apache.xmlrpc.client.XmlRpcClientConfigImpl;


/** Requires java XML-RPC client from http://ws.apache.org/xmlrpc/download.html
 * 
 * 
 * @author rnc
 *
 */
public class IskClient {

	/**
	 * @param args
	 * @throws MalformedURLException 
	 * @throws XmlRpcException 
	 */
	public static void main(String[] args) throws MalformedURLException, XmlRpcException {

	    XmlRpcClientConfigImpl config = new XmlRpcClientConfigImpl();
	    config.setServerURL(new URL("http://localhost:31128/RPC"));
	    XmlRpcClient client = new XmlRpcClient();
	    client.setConfig(config);
	    
	    // Get all database spaces
	    Object[] dbList = (Object[]) client.execute("getDbList", new Object[]{});
	    for (int i = 0; i < dbList.length; i++) {
	    	System.out.println((Integer)dbList[i]);			
		}
	    
	    // Create db space 1
	    client.execute("createDb", new Object[]{new Integer(1)});
	    
	    // Add images to database space 1
	    client.execute("addImg", new Object[]{
	    		new Integer(1),
	    		new Integer(1),
	    		"c:\\data\\DSC00006.JPG"	    		
	    		});	    

	    // Get image count on db space 1
	    Integer imgCount = (Integer) client.execute("getDbImgCount", new Object[]{new Integer(1)});
	    System.out.println(imgCount);
	}
}
