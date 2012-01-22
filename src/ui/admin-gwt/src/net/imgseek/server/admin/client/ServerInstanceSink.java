/*
 * Copyright 2007 Ricardo Niederberger Cabral, all rights reserved.
 * http://server.imgseek.net/
 * 
 */
package net.imgseek.server.admin.client;

import com.fredhat.gwt.xmlrpc.client.XmlRpcRequest;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

/**
 * Introduction page.
 */
public class ServerInstanceSink extends Sink {

	public static SinkInfo init() {
		return new SinkInfo("Server",
				"Manage this isk-daemon server instance.") {
			public Sink createInstance() {
				return new ServerInstanceSink();
			}
		};
	}

	public ServerInstanceSink() {
		VerticalPanel vp = new VerticalPanel();
		vp.setSpacing(8);
		vp.add(new HTML("<h2>Instance commands</h2>"));

		// Commands
		Button shutBtn = new Button("Shutdown");
		shutBtn.addStyleName("alert-button");
		vp.add(shutBtn);
		shutBtn.addClickListener(new ClickListener() {

			public void onClick(final Widget sender) {
				if (Window
						.confirm("Are you sure you want to shutdown this isk-daemon instance ?")) {

					XmlRpcRequest<Integer> request = new XmlRpcRequest<Integer>(
							client, "shutdownServer", new Object[] {},
							new AsyncCallback<Integer>() {
								public void onFailure(final Throwable response) {
									Iskdaemon_admin.error(response);
								}

								public void onSuccess(final Integer ret) {
									Iskdaemon_admin
											.showMessage("'Shutdown requested, window will now close.");
									Iskdaemon_admin.close();
								}
							});
					request.execute();

				}
			}
		});

		initWidget(vp);
	}
	
	public void autoRefreshAll() {

	}

	public void manualRefreshAll() {

	}

	public void onShow() {
	}
}
