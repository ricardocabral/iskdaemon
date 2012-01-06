/*
 * Copyright 2007 Ricardo Niederberger Cabral, all rights reserved.
 * http://server.imgseek.net/
 * 
 */
package net.imgseek.server.admin.client;

import java.util.Iterator;
import java.util.Map;

import com.fredhat.gwt.xmlrpc.client.XmlRpcRequest;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.VerticalPanel;

/**
 * Introduction page.
 */
public class StatusSink extends Sink {

	public static SinkInfo init() {
		return new SinkInfo("Status", "isk-daemon status") {
			public Sink createInstance() {
				return new StatusSink();
			}
		};
	}

	private final Grid vGrid = new Grid();

	public StatusSink() {

		autoRefreshAll();

		// Grid
		VerticalPanel vp = new VerticalPanel();

		vp.setSpacing(8);
		vp.setWidth("100%");
		vp.add(vGrid);
		initWidget(vp);
	}

	public void autoRefreshAll() {

		XmlRpcRequest<Map> request = new XmlRpcRequest<Map>(client,
				"getGlobalServerStats", new Object[] {},
				new AsyncCallback<Map>() {
					public void onFailure(final Throwable response) {
						Iskdaemon_admin.error(response);
					}

					public void onSuccess(final Map response) {
						vGrid.resize(response.size(), 2);
						vGrid.setBorderWidth(1);
						int i = 0;
						for (Iterator it = response.keySet().iterator(); it
								.hasNext();) {
							String stat = (String) it.next();
							vGrid.setHTML(i, 0, "<b>" + stat + "</b>");
							vGrid.setText(i, 1, response.get(stat).toString());
							i++;
						}

					}
				});
		request.execute();

	}

	public void manualRefreshAll() {
	}

	public void onShow() {
	}
}
