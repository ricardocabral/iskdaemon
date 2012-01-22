/*
 * Copyright 2007 Ricardo Niederberger Cabral, all rights reserved.
 * http://server.imgseek.net/
 * 
 */
package net.imgseek.server.admin.client;

import java.util.Iterator;
import java.util.List;
import java.util.Map;

import com.fredhat.gwt.xmlrpc.client.XmlRpcRequest;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.KeyboardListener;
import com.google.gwt.user.client.ui.TabPanel;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

/**
 * Introduction page.
 */
public class DatabasesSink extends Sink {

	public static SinkInfo init() {
		return new SinkInfo("Databases",
				"Manage database spaces inside this isk-daemon instance") {
			public Sink createInstance() {
				return new DatabasesSink();
			}
		};
	}

	private final TabPanel tabs = new TabPanel();

	private final Grid gridIndiv = new Grid();

	public DatabasesSink() {
		tabs.setWidth("100%");

		tabs.add(manageDb(), "Existing");
		tabs.add(addDb(), "Create new");
		tabs.selectTab(0);
		initWidget(tabs);
	}

	private Widget addDb() {
		Grid grid = new Grid(2, 2);
		grid.setText(0, 0, "Database space id:");
		final TextBox dbidtb = new TextBox();
		dbidtb.setTitle("Enter a positive integer as the database id");
		dbidtb.setName("dbidtb");

		grid.setWidget(0, 1, dbidtb);

		// id validation
		dbidtb.addKeyboardListener(new KeyboardListener() {
			public void onKeyDown(final Widget sender, final char keyCode,
					final int modifiers) {

			}

			public void onKeyPress(final Widget sender, final char keyCode,
					final int modifiers) {

			}

			public void onKeyUp(final Widget sender, final char keyCode,
					final int modifiers) {

			}

		});

		// submit button
		Button submit = new Button("Add", new ClickListener() {
			public void onClick(final Widget sender) {

				XmlRpcRequest<Integer> request = new XmlRpcRequest<Integer>(
						client, "createDb", new Object[] { dbidtb.getText() },
						new AsyncCallback<Integer>() {
							public void onFailure(final Throwable response) {
								Iskdaemon_admin.error(response);
							}

							public void onSuccess(final Integer ret) {
								Iskdaemon_admin.showMessage("Database " + ret
										+ " created.");
								// update and switch to existing dbs
								Iskdaemon_admin.manualRefreshAllSinks();
								tabs.selectTab(0);

							}
						});
				request.execute();
			}
		});
		grid.setWidget(1, 1, submit);

		return grid;
	}

	public void autoRefreshAll() {
		updateExisting();
	}

	private Widget manageDb() {
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

				XmlRpcRequest<Integer> request = new XmlRpcRequest<Integer>(
						client, "saveAllDbs", new Object[] {},
						new AsyncCallback<Integer>() {
							public void onFailure(final Throwable response) {
								progressPopup.hide();
								Iskdaemon_admin.error(response);
							}

							public void onSuccess(final Integer ret) {
								progressPopup.hide();
								Iskdaemon_admin.showMessage(ret.toString()
										+ " database(s) saved.", false);
							}
						});
				request.execute();
			}
		});
		return vp;
	}

	public void manualRefreshAll() {

	}

	public void onShow() {
	}

	private void updateExisting() {

		XmlRpcRequest<Map> request = new XmlRpcRequest<Map>(client,
				"getDbDetailedList", new Object[] {}, new AsyncCallback<Map>() {
					public void onFailure(final Throwable response) {
						Iskdaemon_admin.error(response);
					}

					public void onSuccess(final Map dbids) {
						if (dbids.size() == 0) { // no dbs yet
							gridIndiv.resize(1, 1);
							gridIndiv
									.setHTML(0, 0,
											"<b>Please create a database space first.</b>");
							tabs.selectTab(1);
							return;
						}
						gridIndiv.resize(dbids.size() + 1, 4);

						gridIndiv.setHTML(0, 0, "<b>Id</b>");
						gridIndiv.setHTML(0, 1, "<b>Image count</b>");
						gridIndiv.setHTML(0, 2, "<b>Query count</b>");
						gridIndiv.setHTML(0, 3, "<b>Commands</b>");

						int cnt = 1;
						for (Iterator iter = dbids.keySet().iterator(); iter
								.hasNext();) {
							final String dbid = (String) iter.next();
							// basic info
							gridIndiv.setText(cnt, 0, dbid);
							List dbdata = (List) dbids.get(dbid);

							// img count
							gridIndiv.setText(cnt, 1, dbdata.get(0).toString());
							if (dbdata.get(0).equals("0")) {
								gridIndiv
										.setText(cnt, 1,
												"None - Click on the 'Images' section to populate this database.");
							}

							gridIndiv.setText(cnt, 2, dbdata.get(1).toString());

							// create commands

							HorizontalPanel commandPanel = new HorizontalPanel();

							Button resetBtn = new Button("Reset");
							resetBtn.addStyleName("alert-button");
							resetBtn.addClickListener(new ClickListener() {

								public void onClick(final Widget sender) {
									if (!Window
											.confirm("Reset and remove all images from database space '"
													+ dbid + "' ?")) {
										return;
									}

									XmlRpcRequest<Integer> request = new XmlRpcRequest<Integer>(
											client, "resetDb",
											new Object[] { dbid },
											new AsyncCallback<Integer>() {
												public void onFailure(
														final Throwable response) {
													Iskdaemon_admin.error(response);
												}

												public void onSuccess(
														final Integer ret) {
													if (ret == 1) {
														Iskdaemon_admin
																.showMessage("Database "
																		+ dbid
																		+ " reseted.");
													} else {
														Iskdaemon_admin
																.showMessage("Unable to reset database "
																		+ dbid
																		+ ". Check server log.");
													}
												}
											});
									request.execute();

								}
							});
							commandPanel.add(resetBtn);

							// Export imgid list
							Button listBtn = new Button("Export image id list");
							listBtn.addClickListener(new ClickListener() {

								public void onClick(final Widget sender) {
									Window
											.open(
													Iskdaemon_admin.WEB_ENDPOINT
															+ "export?m=imgidlist&dbid="
															+ dbid, "_blank",
													null);
								}

							});
							commandPanel.add(listBtn);

							gridIndiv.setWidget(cnt, 3, commandPanel);
							cnt++;
						}

					}
				});
		request.execute();
	}
}
