/*
 * Copyright 2007 Ricardo Niederberger Cabral, all rights reserved.
 * http://server.imgseek.net/
 * 
 */
package net.imgseek.server.admin.client;

import com.google.gwt.user.client.ui.HTML;

/**
 * Introduction page.
 */
public class AboutSink extends Sink {

	public static SinkInfo init() {
		return new SinkInfo("About", "About isk-daemon") {
			public Sink createInstance() {
				return new AboutSink();
			}
		};
	}

	public AboutSink() {
		initWidget(new HTML(
				"<div class='infoProse'>Version: "
						+ Iskdaemon_admin.VERSION
						+ "<p>Release date: "
						+ Iskdaemon_admin.RELEASEDATE
						+ "<p><a href='http://server.imgseek.net/'>Web site</a> for more details, submit bugs, provide feedback etc.",
				true));
	}

	public void autoRefreshAll() {

	}

	public void manualRefreshAll() {

	}

	public void onShow() {
	}
}