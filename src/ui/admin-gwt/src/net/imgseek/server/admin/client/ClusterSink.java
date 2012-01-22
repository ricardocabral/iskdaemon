/*
 * Copyright 2007 Ricardo Niederberger Cabral, all rights reserved.
 * http://server.imgseek.net/
 * 
 */
package net.imgseek.server.admin.client;

import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

/**
 * Introduction page.
 */
public class ClusterSink extends Sink {

	public static SinkInfo init() {
		return new SinkInfo("Cluster",
				"Manage isk-daemon instances on this cluster.") {
			public Sink createInstance() {
				return new ClusterSink();
			}
		};
	}

	private final Grid gridIndiv = new Grid();

	public ClusterSink() {
		initWidget(manageInstances());
	}

	public void autoRefreshAll() {
		updateExisting();
	}

	private Widget manageInstances() {
		VerticalPanel vp = new VerticalPanel();
		vp.setSpacing(8);
		vp.setWidth("100%");

		vp.add(new HTML("<br/><h2>Individual database spaces</h2>"));

		// gridIndiv.setWidth("100%");
		vp.add(gridIndiv);
		gridIndiv.setBorderWidth(1);
		updateExisting();
		vp.add(new HTML("<br/><hr/><h2>All database spaces</h2>"));
		final Grid gridAll = new Grid(2, 2);
		// gridAll.setWidth("100%");
		vp.add(gridAll);
		gridAll.setBorderWidth(1);
		gridAll.setHTML(0, 0, "<b>Command</b>");
		gridAll.setHTML(0, 1, "<b>Description</b>");

		// Save All
		Button saveAllBtn = new Button("Save all");
		gridAll
				.setHTML(
						1,
						1,
						"Save all database spaces to the currently defined data file. It is defined on the <i>settings.py</i> config file.");
		gridAll.setWidget(1, 0, saveAllBtn);
		saveAllBtn.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				final ProgressPopup progressPopup = new ProgressPopup();
				progressPopup.show("Saving");

				// new JsonRpc().request(iskdaemon.JSON_BACKEND, "saveAllDbs",
				// new Object[] {}, new AsyncCallback() {
				// public void onFailure(final Throwable caught) {
				// progressPopup.hide();
				// iskdaemon.error(caught);
				// }
				//
				// public void onSuccess(final Object result) {
				// progressPopup.hide();
				// iskdaemon.showMessage("Database saved.", false);
				// }
				// });
			}
		});
		return vp;
	}

	public void manualRefreshAll() {

	}

	public void onShow() {
	}

	private void updateExisting() {
		// new JsonRpc().request(iskdaemon.JSON_BACKEND, "getDbDetailedList",
		// new Object[] {}, new AsyncCallback() {
		// public void onFailure(final Throwable caught) {
		// iskdaemon.error(caught);
		// }
		//
		// public void onSuccess(final Object result) {
		// Map dbids = (Map) result;
		// if (dbids.size() == 0) { // no dbs yet
		// gridIndiv.resize(1, 1);
		// gridIndiv
		// .setHTML(0, 0,
		// "<b>Please create a database space first.</b>");
		//
		// return;
		// }
		// gridIndiv.resize(dbids.size() + 1, 4);
		//
		// gridIndiv.setHTML(0, 0, "<b>Id</b>");
		// gridIndiv.setHTML(0, 1, "<b>Image count</b>");
		// gridIndiv.setHTML(0, 2, "<b>Query count</b>");
		// gridIndiv.setHTML(0, 3, "<b>Commands</b>");
		//
		// int cnt = 1;
		// for (Iterator iter = dbids.keySet().iterator(); iter
		// .hasNext();) {
		// final String dbid = (String) iter.next();
		// // basic info
		// gridIndiv.setText(cnt, 0, dbid);
		// Object[] dbdata = (Object[]) dbids.get(dbid);
		//
		// // img count
		// gridIndiv.setText(cnt, 1, dbdata[0].toString());
		// if (dbdata[0].toString().equals("0")) {
		// gridIndiv
		// .setText(cnt, 1,
		// "None - Click on the 'Images' section to populate this database.");
		// }
		//
		// gridIndiv.setText(cnt, 2, dbdata[1].toString());
		//
		// // create commands
		//
		// HorizontalPanel commandPanel = new HorizontalPanel();
		// /*
		// * Button saveBtn = new Button("Export");
		// * saveBtn.addClickListener(new ClickListener() {
		// *
		// * public void onClick(Widget sender) {
		// *
		// * new JsonRpc().request( iskdaemon.JSON_BACKEND,
		// * "saveDbAs", new Object[] {dbid, path}, new
		// * AsyncCallback() { public void onFailure(Throwable
		// * caught) { iskdaemon.error(caught); }
		// *
		// * public void onSuccess(Object result) { Integer
		// * ret = (Integer)result;
		// * iskdaemon.showMessage("Database " + ret
		// * +" exported to " + path); }
		// *
		// * }); } }); commandPanel.add(saveBtn);
		// */
		// Button resetBtn = new Button("Reset");
		// resetBtn.addClickListener(new ClickListener() {
		//
		// public void onClick(final Widget sender) {
		// if (!Window
		// .confirm("Reset and remove all images from database space '"
		// + dbid + "' ?")) {
		// return;
		// }
		// // new JsonRpc().request(
		// // iskdaemon.JSON_BACKEND, "resetDb",
		// // new Object[] { dbid },
		// // new AsyncCallback() {
		// // public void onFailure(
		// // final Throwable caught) {
		// // iskdaemon.error(caught);
		// // }
		// //
		// // public void onSuccess(
		// // final Object result) {
		// // iskdaemon
		// // .showMessage("Database "
		// // + dbid
		// // + " reseted.");
		// // }
		// // });
		// }
		// });
		// commandPanel.add(resetBtn);
		//
		// // load
		//
		// /*
		// * Button loadBtn = new Button("Load");
		// * loadBtn.addClickListener(new ClickListener() {
		// *
		// * public void onClick(Widget sender) {
		// *
		// * }
		// *
		// * }); commandPanel.add(loadBtn);
		// */
		//
		// // Export imgid list
		// Button listBtn = new Button("Export image id list");
		// listBtn.addClickListener(new ClickListener() {
		//
		// public void onClick(final Widget sender) {
		// Window
		// .open(
		// iskdaemon.WEB_ENDPOINT
		// + "export?m=imgidlist&dbid="
		// + dbid, "_blank",
		// null);
		// }
		//
		// });
		// commandPanel.add(listBtn);
		//
		// gridIndiv.setWidget(cnt, 3, commandPanel);
		// cnt++;
		// }
		// }
		//
		// });
	}
}
