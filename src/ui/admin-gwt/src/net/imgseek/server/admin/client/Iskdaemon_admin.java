package net.imgseek.server.admin.client;

import java.util.Iterator;

import net.imgseek.server.admin.client.Sink.SinkInfo;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.History;
import com.google.gwt.user.client.HistoryListener;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.DockPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasAlignment;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

/**
 * Entry point classes define <code>onModuleLoad()</code>.
 */
public class Iskdaemon_admin implements EntryPoint, HistoryListener {
	/**
	 * The message displayed to the user when the server cannot be reached or
	 * returns an error.
	 */
	private static final String SERVER_ERROR = "An error occurred while "
			+ "attempting to contact the server. Please check your network "
			+ "connection and try again.";
	public static final String VERSION = "0.9.2";
	public static final String RELEASEDATE = "Jan 2012";
	protected static String WEB_ENDPOINT = "/";
	public static final String XMLRPC_BACKEND = WEB_ENDPOINT + "RPC";
	protected static SinkList list = new SinkList();
	private SinkInfo curInfo;
	private Sink curSink;
	private final HTML description = new HTML();
	private final DockPanel panel = new DockPanel();
	private DockPanel sinkContainer;
	private static HorizontalPanel statusPanel = new HorizontalPanel();
	private static Label statusMessageLabel = new Label();

	public static native void close() /*-{
	    $wnd.close();
	  }-*/;

	public static void error(final Throwable caught) {
		if (caught.getMessage().equals("Size: 1 Index: 1")) { //TODO what does it mean?
			return;
		}

		String msg = "Unexpected error:\n";
		msg += caught.getMessage() + "\n";
		msg += caught.getCause() + "\n";
		for (int i = 0; i < caught.getStackTrace().length; i++) {
			msg += caught.getStackTrace()[i] + "\n";
		}

		showMessage(msg, true);
	}

	public static void manualRefreshAllSinks() {
		for (Iterator iter = list.getSinks().iterator(); iter.hasNext();) {
			SinkInfo element = (SinkInfo) iter.next();
			element.getInstance().manualRefreshAll();
		}
	}

	public static void showMessage(final String text) {
		showMessage(text, false);
	}

	public static void showMessage(final String text, final boolean isError) {
		statusMessageLabel.setText(text);
		if (isError) {
			statusPanel.setStyleName("msg-alert-red");
		} else {
			statusPanel.setStyleName("msg-alert");
		}
		statusPanel.setVisible(true);
	}

	/**
	 * Adds all sinks to the list. Note that this does not create actual
	 * instances of all sinks yet (they are created on-demand). This can make a
	 * significant difference in startup time.
	 */
	protected void loadSinks() {
		list.addSink(StatusSink.init());
		// list.addSink(Settings.init());
		list.addSink(DatabasesSink.init());
		list.addSink(ServerInstanceSink.init());
		list.addSink(ImagesSink.init());
		// list.addSink(ClusterSink.init());
		list.addSink(AboutSink.init());
	}

	public void onHistoryChanged(final String token) {
		// Find the SinkInfo associated with the history context. If one is
		// found, show it (It may not be found, for example, when the user mis-
		// types a URL, or on startup, when the first context will be "").
		SinkInfo info = list.find(token);
		if (info == null) {
			showInfo();
			return;
		}
		show(info, false);
	}

	public void onModuleLoad() {

		WEB_ENDPOINT = GWT.getModuleBaseURL();

		// Load all the sinks.
		loadSinks();

		// Status panel
		statusPanel.setVisible(false);
		statusPanel.setStyleName("msg-alert");
		statusPanel.add(statusMessageLabel);
		statusPanel.setSpacing(8);
		statusPanel.setWidth("100%");
		HTML closeLink = new HTML("<font size=small>[close]</font>");
		closeLink.setStyleName("msg-alert-link");
		closeLink.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				statusPanel.setVisible(false);
			}
		});
		statusPanel.add(closeLink);

		// Put the sink list on the left, and add the outer dock panel to the
		// root.
		sinkContainer = new DockPanel();
		sinkContainer.setStyleName("ks-Sink");

		VerticalPanel vp = new VerticalPanel();
		vp.setWidth("100%");
		vp.add(statusPanel);
		vp.add(description);
		vp.add(sinkContainer);

		description.setStyleName("ks-Info");

		// Common Header
		HorizontalPanel hpHeader = new HorizontalPanel();
		hpHeader.setWidth("100%");
		hpHeader.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);

		HTML iskTitle = new HTML("isk-daemon (" + VERSION + ")");// " at <i>" +
		// WEB_ENDPOINT
		// +
		// "</i>");
		// TODO show remote server name when cluster funcionality is implemented
		iskTitle.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);

		hpHeader.add(iskTitle);

		// Compose dock panel
		panel.add(hpHeader, DockPanel.NORTH);
		panel.add(list, DockPanel.WEST);
		panel.add(vp, DockPanel.CENTER);

		panel.setCellVerticalAlignment(list, HasAlignment.ALIGN_TOP);
		panel.setCellWidth(vp, "100%");
		RootPanel.get().add(panel);

		// Common Footer
		HorizontalPanel hpFooter = new HorizontalPanel();
		hpFooter.setWidth("100%");
		hpFooter.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);

		HTML copyRightFooter = new HTML(
				"<div align='right'>Copyright &copy; <a target='_blank' href='http://server.imgseek.net/'>imgSeek</a>. All rights reserved. Licensed under the <a href='http://www.gnu.org/licenses/gpl-2.0-standalone.html'>GPLv2</a></div>");
		copyRightFooter
				.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);

		// hpFooter.add(footerShare);
		hpFooter.add(copyRightFooter);
		RootPanel.get().add(hpFooter);

		History.addHistoryListener(this);

		// Show the initial screen.
		String initToken = History.getToken();
		if (initToken.length() > 0) {
			onHistoryChanged(initToken);
		} else {
			showInfo();
		}

		// Start timer
		Timer t = new Timer() {
			public void run() {
				for (Iterator iter = list.getSinks().iterator(); iter.hasNext();) {
					SinkInfo element = (SinkInfo) iter.next();
					element.getInstance().autoRefreshAll();
				}
			}
		};
		// Schedule the timer to run once in 5 seconds.
		t.scheduleRepeating(5000);

		// TODO: check if iskdaemon instance is passwd protect then prompt for
		// login: http://code.google.com/p/gwt-stuff/
	}

	public void show(final SinkInfo info, final boolean affectHistory) {
		// Don't bother re-displaying the existing sink. This can be an issue
		// in practice, because when the history context is set, our
		// onHistoryChanged() handler will attempt to show the currently-visible
		// sink.
		if (info == curInfo) {
			return;
		}
		curInfo = info;

		// Remove the old sink from the display area.
		if (curSink != null) {
			curSink.onHide();
			sinkContainer.remove(curSink);
		}

		// Get the new sink instance, and display its description in the
		// sink list.
		curSink = info.getInstance();
		list.setSinkSelection(info.getName());
		description.setHTML(info.getDescription());

		// If affectHistory is set, create a new item on the history stack. This
		// will ultimately result in onHistoryChanged() being called. It will
		// call
		// show() again, but nothing will happen because it will request the
		// exact
		// same sink we're already showing.
		if (affectHistory) {
			History.newItem(info.getName());
		}

		// Display the new sink.
		sinkContainer.add(curSink, DockPanel.CENTER);
		sinkContainer.setCellWidth(curSink, "100%");
		sinkContainer.setCellHeight(curSink, "100%");
		sinkContainer.setCellVerticalAlignment(curSink, DockPanel.ALIGN_TOP);
		curSink.onShow();
	}

	private void showInfo() {
		show(list.find("Status"), false);
	}
}
