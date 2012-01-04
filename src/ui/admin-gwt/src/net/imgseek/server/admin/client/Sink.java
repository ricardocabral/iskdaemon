/*
 * Copyright 2007 Ricardo Niederberger Cabral, all rights reserved.
 * http://server.imgseek.net/
 * 
 */
package net.imgseek.server.admin.client;

import com.fredhat.gwt.xmlrpc.client.XmlRpcClient;
import com.google.gwt.user.client.ui.Composite;

/**
 * A 'sink' is a single panel of the kitchen sink. They are meant to be lazily
 * instantiated so that the application doesn't pay for all of them on startup.
 */
public abstract class Sink extends Composite {

	/**
	 * Encapsulated information about a sink. Each sink is expected to have a
	 * static <code>init()</code> method that will be called by the kitchen sink
	 * on startup.
	 */
	public abstract static class SinkInfo {
		private Sink instance;
		private final String name, description;

		public SinkInfo(final String name, final String desc) {
			this.name = name;
			description = desc;
		}

		public abstract Sink createInstance();

		public String getDescription() {
			return description;
		}

		public final Sink getInstance() {
			if (instance != null) {
				return instance;
			}
			return instance = createInstance();
		}

		public String getName() {
			return name;
		}
	}

	static XmlRpcClient client = new XmlRpcClient(Iskdaemon_admin.XMLRPC_BACKEND);

	public abstract void autoRefreshAll();

	public abstract void manualRefreshAll();

	/**
	 * Called just before this sink is hidden.
	 */
	public void onHide() {
	}

	/**
	 * Called just after this sink is shown.
	 */
	public void onShow() {
	}
}
