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
public class SettingsSink extends Sink {

  public static SinkInfo init() {
    return new SinkInfo("Settings", "Adjust global settings for this isk-daemon instance") {
      public Sink createInstance() {
        return new SettingsSink();
      }
    };
  }

  public SettingsSink() {
    initWidget(new HTML(
      "<div class='infoProse'>This is the Kitchen Sink sample.  "
        + "It demonstrates many of the widgets in the Google Web Toolkit."
        + "<p>This sample also demonstrates something else really useful in GWT: "
        + "history support.  "
        + "When you click on a link at the left, the location bar will be "
        + "updated with the current <i>history token</i>, which keeps the app "
        + "in a bookmarkable state.  The back and forward buttons work properly "
        + "as well.  Finally, notice that you can right-click a link and 'open "
        + "in new window' (or middle-click for a new tab in Firefox).</p></div>",
      true));
  }

  public void onShow() {
  }


public void autoRefreshAll() {
	
}

public void manualRefreshAll() {

}
}