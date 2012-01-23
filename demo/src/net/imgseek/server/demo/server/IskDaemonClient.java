package net.imgseek.server.demo.server;

import java.net.MalformedURLException;
import java.net.URL;

import org.apache.xmlrpc.client.XmlRpcClient;
import org.apache.xmlrpc.client.XmlRpcClientConfigImpl;

public class IskDaemonClient {
	public XmlRpcClient client;

	public IskDaemonClient() {

		XmlRpcClientConfigImpl config = new XmlRpcClientConfigImpl();
		try {
			config.setServerURL(new URL("http://127.0.0.1:31128/RPC"));
		} catch (MalformedURLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} // isk-daemon
			// XML-RPC
			// endpoint
			// URL
		config.setEnabledForExtensions(true);
		this.client = new XmlRpcClient();
		this.client.setConfig(config);

	}
}