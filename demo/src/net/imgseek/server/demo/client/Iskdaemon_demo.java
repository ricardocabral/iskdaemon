/*
 * Created: Sat Jan 21 15:44:22 BRST 2012
 *
 * Copyright (C) 2012 Ricardo Niederberger Cabral
 * <ricardo.cabral at imgseek.net>
 * 
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */
package net.imgseek.server.demo.client;

import java.util.List;

import net.imgseek.server.demo.shared.DbImageResult;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.core.client.GWT;
import com.google.gwt.event.logical.shared.ValueChangeEvent;
import com.google.gwt.event.logical.shared.ValueChangeHandler;
import com.google.gwt.i18n.client.NumberFormat;
import com.google.gwt.user.client.History;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Hyperlink;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.VerticalPanel;

/**
 * Entry point classes define <code>onModuleLoad()</code>.
 */
public class Iskdaemon_demo implements EntryPoint, ValueChangeHandler<String> {
	private static final int GRID_COLS = 4;
	private static final int NUMRES = 12;

	/**
	 * Create a remote service proxy to talk to the server-side Isk service.
	 */
	private final IskDemoServiceAsync iskDemoService = GWT
			.create(IskDemoService.class);

	private final Grid resultsGrid = new Grid(3, GRID_COLS);

	/**
	 * This is the entry point method.
	 */
	public void onModuleLoad() {
		VerticalPanel mvp = new VerticalPanel();
		RootPanel.get("main").add(mvp);
		HorizontalPanel hhp = new HorizontalPanel();
		mvp.add(hhp);
		hhp.add(new HTML("<h1>isk-daemon example</h1>"));
		hhp.add(new HTML(
				"<p><a href=http://server.imgseek.net/>isk-daemon</a> is an open source database server capable of adding content-based (visual) image searching to any image related website or software. Click on the '+ similar' link below each image to search by visual similarity. See <a href='http://www.imgseek.net/isk-daemon/demo'>more details</a> about this demo, including source code.</p>"));
		hhp.add(new Hyperlink("Random images", "similar-0"));

		mvp.add(resultsGrid);
		mvp.add(new HTML(
				"<br/>Copyright 2012 <a href=http://www.imgseek.net/>imgSeek project</a>. Sample images are copyrighted by <a href=http://www.vision.caltech.edu/Image_Datasets/Caltech256/>Caltech 256</a>. Includes 30,607 images, covering a large number of categories."));

		// If the application starts with no history token, redirect to a new
		String initToken = History.getToken();
		if (initToken.length() == 0) {
			History.newItem("similar-0");
		}
		// Add history listener
		History.addValueChangeHandler(this);
		// Now that we've setup our listener, fire the initial history state.
		History.fireCurrentHistoryState();
	}

	@Override
	public void onValueChange(ValueChangeEvent<String> event) {
		int tid = 0;
		try {
			tid = Integer.parseInt(event.getValue().substring(8));
		} catch (NumberFormatException e) {
			e.printStackTrace();
		}

		final NumberFormat df = NumberFormat.getFormat("#.##");

		iskDemoService.queryImgID(tid, NUMRES, false,
				new AsyncCallback<List<DbImageResult>>() {
					public void onFailure(Throwable caught) {
						// TODO Show the RPC error message to the user
					}

					public void onSuccess(List<DbImageResult> result) {
						resultsGrid.clear();
						int i = 0;

						for (DbImageResult res : result) {
							VerticalPanel rvp = new VerticalPanel();
							rvp.setStyleName("dotted");
							rvp.add(new Image(res.getUrl()));
							HorizontalPanel hc = new HorizontalPanel();
							String scoreLabel = "(random) ";
							if (res.getScore() > 0)
								scoreLabel = df.format(res.getScore()) + "%";
							hc.add(new Label(scoreLabel));
							hc.add(new Hyperlink("   + similar", "similar-"
									+ res.getId()));
							rvp.add(hc);

							resultsGrid.setWidget(i / GRID_COLS, i % GRID_COLS,
									rvp);
							i++;
						}
					}
				});
	}
}
