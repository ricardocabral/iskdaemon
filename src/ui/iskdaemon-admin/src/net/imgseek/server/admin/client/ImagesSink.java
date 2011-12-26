/*
 * Copyright 2007 Ricardo Niederberger Cabral, all rights reserved.
 * http://server.imgseek.net/
 * 
 */
package net.imgseek.server.admin.client;

import java.util.List;

import com.fredhat.gwt.xmlrpc.client.XmlRpcRequest;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ChangeListener;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.TabPanel;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class ImagesSink extends Sink {

	public static SinkInfo init() {
		return new SinkInfo("Images", "Manage images") {
			public Sink createInstance() {
				return new ImagesSink();
			}
		};
	}

	private final TabPanel tabs = new TabPanel();

	private final ListBox dbcombo = new ListBox();

	public ImagesSink() {

		tabs.setWidth("100%");

		dbcombo.setVisibleItemCount(1);

		updateDbCombo();

		FlowPanel hp = new FlowPanel();
		hp.setWidth("100%");
		hp.setStyleName("ks-Info-normal-font");
		HorizontalPanel hpDb = new HorizontalPanel();
		hpDb.add(new HTML("Operating on database space:"));
		hpDb.add(dbcombo);
		hp.add(hpDb);
		VerticalPanel vp = new VerticalPanel();
		vp.setWidth("100%");
		vp.add(hp);
		vp.add(tabs);
		tabs.setWidth("100%");
		tabs.add(manageImagesPage(), "Perfom operation on existing images");
		tabs.add(importImagesPage(), "Import images");
		tabs.selectTab(0);

		initWidget(vp);

	}

	public void autoRefreshAll() {

	}

	private Widget importImagesPage() {
		// Path
		HorizontalPanel hp = new HorizontalPanel();
		hp.setWidth("100%");
		hp.setSpacing(5);
		hp.add(new HTML("Import filesystem path on server machine "));
		final TextBox pathEdit = new TextBox();
		hp.add(pathEdit);

		// Path type
		hp.add(new HTML(" which is a "));
		final ListBox pathTypeCombo = new ListBox();
		pathTypeCombo.setVisibleItemCount(1);
		pathTypeCombo.addItem("Single image");
		pathTypeCombo.addItem("Directory");
		hp.add(pathTypeCombo);

		// single image id
		final Label imgIdLabel = new Label(" and set its ID to ");
		hp.add(imgIdLabel);
		imgIdLabel.setVisible(false);

		final TextBox imgIdEdit = new TextBox();
		hp.add(imgIdEdit);
		imgIdEdit.setVisible(false);

		// Add dir optns
		final CheckBox cbRec = new CheckBox("to be imported recursively");
		cbRec.setVisible(true);
		pathTypeCombo.addChangeListener(new ChangeListener() {
			public void onChange(final Widget sender) {
				if (sender == pathTypeCombo) {
					if (((ListBox) sender).getSelectedIndex() == 0) { // file
						// selected
						cbRec.setVisible(false);
						imgIdLabel.setVisible(true);
						imgIdEdit.setVisible(true);
					} else { // dir selected
						cbRec.setVisible(true); // toggle recursive chekcbox
						imgIdLabel.setVisible(false);
						imgIdEdit.setVisible(false);
					}
				}
			}
		});
		pathTypeCombo.setItemSelected(1, true);
		hp.add(cbRec);
		// Add !
		Button addBtn = new Button("Import");
		hp.add(addBtn);
		addBtn.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				if (pathTypeCombo.getSelectedIndex() == 0) { // single image
					XmlRpcRequest<Integer> request = new XmlRpcRequest<Integer>(
							client, "addImg", new Object[] {
									dbcombo.getItemText(dbcombo
											.getSelectedIndex()),
									imgIdEdit.getText(), pathEdit.getText() },
							new AsyncCallback<Integer>() {
								public void onFailure(final Throwable response) {
									Iskdaemon_admin.error(response);
								}

								public void onSuccess(final Integer result) {
									if (result.equals(new Integer(1))) {
										Iskdaemon_admin
												.showMessage("Image imported.");
									} else {
										Iskdaemon_admin
												.showMessage(
														"Unable to import image.",
														true);
									}
								}
							});
					request.execute();
				} else { // dir
					final ProgressPopup progressPopup = new ProgressPopup();
					progressPopup.show("Importing");

					XmlRpcRequest<Integer> request = new XmlRpcRequest<Integer>(
							client, "addDir", new Object[] {
									dbcombo.getItemText(dbcombo
											.getSelectedIndex()),
									pathEdit.getText(),
									new Boolean(cbRec.isChecked()) },
							new AsyncCallback<Integer>() {
								public void onFailure(final Throwable response) {
									progressPopup.hide();
									Iskdaemon_admin.error(response);
								}

								public void onSuccess(final Integer ret) {
									progressPopup.hide();
									Iskdaemon_admin
											.showMessage("Directory imported. Total new images: "
													+ ret);
								}
							});
					request.execute();

				}
			}
		});

		return hp;
	}

	private Widget manageImagesPage() {
		/*
		 * queryImgID, isImageOnDB, removeImg, getImageHeight, getImageWidth,
		 * calcAvglDiff, calcDiff, getImageAvgl,
		 */
		VerticalPanel vp = new VerticalPanel();
		vp.setSpacing(5);
		vp.setWidth("100%");
		// Operation
		HorizontalPanel hp = new HorizontalPanel();
		hp.setWidth("100%");
		vp.add(hp);
		hp.add(new HTML("Perform operation"));
		final ListBox operationCombo = new ListBox();
		operationCombo.setVisibleItemCount(1);
		operationCombo.addItem("Get similar images");
		operationCombo.addItem("Check if image ID is on database space");
		operationCombo.addItem("Remove image from database space");
		operationCombo.addItem("Get image dimensions in pixels");
		operationCombo
				.addItem("Get luminance similarity between two images (fast)");
		operationCombo.addItem("Get visual similarity between two images");
		operationCombo.addItem("Get image average luminance");
		hp.add(operationCombo);

		// Parameters (image ids)
		final TextBox id1Edit = new TextBox();
		hp.add(new HTML(" on image with ID "));
		hp.add(id1Edit);

		final TextBox id2Edit = new TextBox();
		final HTML id2Label = new HTML(" and second image with ID ");
		hp.add(id2Label);
		hp.add(id2Edit);
		id2Edit.setVisible(false);
		id2Label.setVisible(false);

		operationCombo.addChangeListener(new ChangeListener() {

			public void onChange(final Widget sender) {
				int selId = operationCombo.getSelectedIndex();
				if (selId == 4 || selId == 5) { // two ids needed
					id2Label.setVisible(true);
					id2Edit.setVisible(true);
				} else { // single id needed
					id2Label.setVisible(false);
					id2Edit.setVisible(false);
				}
			}
		});

		// Perform button
		Button performBtn = new Button("Perform");
		hp.add(performBtn);

		final VerticalPanel resultsVp = new VerticalPanel();
		resultsVp.setWidth("100%");
		final HTML resultLabel = new HTML();
		resultsVp.add(new HTML("<br/><h2>Last operation results</h2>"));
		resultsVp.add(resultLabel);
		resultsVp.setVisible(false);
		vp.add(resultsVp);

		performBtn.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				int selId = operationCombo.getSelectedIndex();
				if (selId == 0) { // get similar images

					XmlRpcRequest<List> request = new XmlRpcRequest<List>(
							client, "queryImgID", new Object[] {
									dbcombo.getItemText(dbcombo
											.getSelectedIndex()),
									id1Edit.getText(), new Integer(25) },
							new AsyncCallback<List>() {
								public void onFailure(final Throwable response) {
									Iskdaemon_admin.error(response);
								}

								public void onSuccess(final List pairList) {
									resultsVp.setVisible(true);

									if (pairList.size() == 0) {
										resultLabel
												.setHTML("<i>Query returned nothing.</i> Possible causes: <ul><li>Supplied database is empty<li>Invalid image id was supplied<li>Database has less than 25 images<ul>");
										return;
									}
									String txt = "25 most similar images:<br/><ul>";
									for (int i = 0; i < pairList.size(); i++) {
										List pair = (List) pairList.get(i);
										String imgId = pair.get(0).toString();
										String imgRatio = pair.get(1)
												.toString();
										if (imgRatio.length() > 5) {
											txt += "<li><b>" + imgId + "</b> ("
													+ imgRatio.substring(0, 5)
													+ "%)";
										} else {
											txt += "<li><b>" + imgId + "</b> ("
													+ imgRatio + "%)";
										}
									}
									txt += "</ul>";
									resultLabel.setHTML(txt);
								}
							});
					request.execute();
				}
				if (selId == 1) { // is on db
					XmlRpcRequest<Boolean> request = new XmlRpcRequest<Boolean>(
							client, "isImgOnDb", new Object[] {
									dbcombo.getItemText(dbcombo
											.getSelectedIndex()),
									id1Edit.getText() },
							new AsyncCallback<Boolean>() {
								public void onFailure(final Throwable response) {
									Iskdaemon_admin.error(response);
								}

								public void onSuccess(final Boolean res) {
									Iskdaemon_admin
											.showMessage(
													"ID "
															+ id1Edit.getText()
															+ (res == true ? " found on database."
																	: " NOT found on database."),
													false);
								}
							});
					request.execute();

				}
				if (selId == 2) { // remove from db

					XmlRpcRequest<Integer> request = new XmlRpcRequest<Integer>(
							client, "removeImg", new Object[] {
									dbcombo.getItemText(dbcombo
											.getSelectedIndex()),
									id1Edit.getText() },
							new AsyncCallback<Integer>() {
								public void onFailure(final Throwable response) {
									Iskdaemon_admin.error(response);
								}

								public void onSuccess(final Integer ret) {
									if (ret.equals(1)) {
										Iskdaemon_admin.showMessage("Image removed.",
												false);
									} else {
										Iskdaemon_admin
												.showMessage("Unable to remove image, check server log.");
									}

								}
							});
					request.execute();

				}
				if (selId == 3) { // image dimensions

					XmlRpcRequest<List> request = new XmlRpcRequest<List>(
							client, "getImgDimensions", new Object[] {
									dbcombo.getItemText(dbcombo
											.getSelectedIndex()),
									id1Edit.getText() },
							new AsyncCallback<List>() {
								public void onFailure(final Throwable response) {
									Iskdaemon_admin.error(response);
								}

								public void onSuccess(final List dim) {
									Iskdaemon_admin.showMessage(
											"Image dimensions in pixels (WxH): "
													+ dim.get(0).toString()
													+ "x"
													+ dim.get(1).toString(),
											false);
								}
							});
					request.execute();

				}
				if (selId == 4) { // calcAvglDiff
					XmlRpcRequest<Double> request = new XmlRpcRequest<Double>(
							client, "calcImgAvglDiff", new Object[] {
									dbcombo.getItemText(dbcombo
											.getSelectedIndex()),
									id1Edit.getText(), id2Edit.getText() },
							new AsyncCallback<Double>() {
								public void onFailure(final Throwable response) {
									Iskdaemon_admin.error(response);
								}

								public void onSuccess(final Double ret) {
									Iskdaemon_admin.showMessage("Difference ratio: "
											+ ret, false);
								}
							});
					request.execute();

				}
				if (selId == 5) { // calcDiff
					XmlRpcRequest<Double> request = new XmlRpcRequest<Double>(
							client, "calcImgDiff", new Object[] {
									dbcombo.getItemText(dbcombo
											.getSelectedIndex()),
									id1Edit.getText(), id2Edit.getText() },
							new AsyncCallback<Double>() {
								public void onFailure(final Throwable response) {
									Iskdaemon_admin.error(response);
								}

								public void onSuccess(final Double ret) {
									Iskdaemon_admin.showMessage("Difference ratio: "
											+ ret, false);
								}
							});
					request.execute();

				}
				if (selId == 6) { // get avgl
					XmlRpcRequest<List> request = new XmlRpcRequest<List>(
							client, "getImgAvgl", new Object[] {
									dbcombo.getItemText(dbcombo
											.getSelectedIndex()),
									id1Edit.getText() },
							new AsyncCallback<List>() {
								public void onFailure(final Throwable response) {
									Iskdaemon_admin.error(response);
								}

								public void onSuccess(final List dim) {

									Iskdaemon_admin.showMessage(
											"Image average luminance is  ("
													+ dim.get(0) + ","
													+ dim.get(1) + ","
													+ dim.get(2) + ")", false);
								}
							});
					request.execute();
				}
			}

		});

		return vp;
	}

	public void manualRefreshAll() {
		updateDbCombo();
	}

	public void onShow() {
	}

	private void updateDbCombo() {
		XmlRpcRequest<List> request = new XmlRpcRequest<List>(client,
				"getDbList", new Object[] {}, new AsyncCallback<List>() {
					public void onFailure(final Throwable response) {
						Iskdaemon_admin.error(response);
					}

					public void onSuccess(final List dblist) {
						dbcombo.clear();

						if (dblist.size() == 0) { // empty db
							Iskdaemon_admin
									.showMessage(
											"No database spaces found. Create one using the 'Databases' tab on the left.",
											true);
						}
						for (int i = 0; i < dblist.size(); ++i) {
							dbcombo.addItem(dblist.get(i).toString());
						}
						dbcombo.setSelectedIndex(0);
					}
				});
		request.execute();

	}
}
