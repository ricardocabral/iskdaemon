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
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.TextArea;
import com.google.gwt.user.client.ui.VerticalPanel;

/**
 * Introduction page.
 */
public class StatusSink extends Sink {

	public static SinkInfo init() {
		return new SinkInfo("Status", "Instance status") {
			public Sink createInstance() {
				return new StatusSink();
			}
		};
	}

	private final Grid vGrid = new Grid();
	private final TextArea logText = new TextArea();
    private final ListBox linesList = new ListBox();
    
	public StatusSink() {

		// Grid
		VerticalPanel vp = new VerticalPanel();

		vp.setSpacing(8);
		vp.setWidth("100%");
		vp.add(vGrid);
		HorizontalPanel logControl = new HorizontalPanel();
		logControl.add(new Label("Log lines"));

	    linesList.addItem("10");
	    linesList.addItem("50");
	    linesList.addItem("100");
	    linesList.addItem("500");
	    linesList.addItem("2000");
	    linesList.setItemSelected(0, true);
	    
	    logText.setReadOnly(true);
	    logText.setCharacterWidth(120);	    
	    logText.setVisibleLines(15);
	    logText.setStyleName("fixedFont");
		logControl.add(linesList);
		vp.add(new HTML("<hr/>"));
		vp.add(logControl);
		vp.add(logText);
		initWidget(vp);
		autoRefreshAll();
	}

	public void autoRefreshAll() {
		//	update general stats
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

		//	update log
		XmlRpcRequest<String> request2 = new XmlRpcRequest<String>(client,
				"getIskLog", new Object[] {Integer.parseInt(linesList.getValue(linesList.getSelectedIndex()))},
				new AsyncCallback<String>() {
					public void onFailure(final Throwable response) {
						Iskdaemon_admin.error(response);
					}

					public void onSuccess(final String response) {
						logText.setText(response);
					}
				});
		request2.execute();

	}

	public void manualRefreshAll() {
	}

	public void onShow() {
	}
}
