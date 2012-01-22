/*
 * Copyright 2007 Ricardo Niederberger Cabral, all rights reserved.
 * http://server.imgseek.net/
 * 
 */
package net.imgseek.server.admin.client;

import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.TabPanel;
import com.google.gwt.user.client.ui.Widget;

/**
 * Introduction page.
 */
public class HelpSink extends Sink {

	public static SinkInfo init() {
		return new SinkInfo("Help", "Help & About") {
			public Sink createInstance() {
				return new HelpSink();
			}
		};
	}
	private final TabPanel tabs = new TabPanel();

	private Widget help() {
		return new HTML("" +
				"See the <a href='http://www.imgseek.net/isk-daemon/documents-1'>online documentation</a>."
				);
	}	
	private Widget about() {
		return new HTML(
				"<div class='infoProse'>Version: "
						+ Iskdaemon_admin.VERSION
						+ "<p>Release date: "
						+ Iskdaemon_admin.RELEASEDATE
						+ "<p>See <a href='http://server.imgseek.net/'>web site</a> for more details."
						+ "<p>Copyright &copy; <a target='_blank' href='http://server.imgseek.net/'>imgSeek</a>. All rights reserved. Licensed under the <a href='http://www.gnu.org/licenses/gpl-2.0-standalone.html'>GPLv2</a>"
				);
	}
	public HelpSink() {
		tabs.setWidth("100%");

		tabs.add(help(), "Help");
		tabs.add(about(), "About");
		tabs.selectTab(0);
		initWidget(tabs);
		
	}

	public void autoRefreshAll() {

	}

	public void manualRefreshAll() {

	}

	public void onShow() {
	}
}