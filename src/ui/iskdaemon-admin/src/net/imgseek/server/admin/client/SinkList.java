/*
 * Copyright 2007 Ricardo Niederberger Cabral, all rights reserved.
 * http://server.imgseek.net/
 * 
 */
package net.imgseek.server.admin.client;

import java.util.ArrayList;

import net.imgseek.server.admin.client.Sink.SinkInfo;

import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Hyperlink;
import com.google.gwt.user.client.ui.VerticalPanel;

/**
 * The left panel that contains all of the sinks, along with a short description
 * of each.
 */
public class SinkList extends Composite {

  private VerticalPanel list = new VerticalPanel();
  private ArrayList sinks = new ArrayList();
  private int selectedSink = -1;

  public SinkList() {
    initWidget(list);
    setStyleName("ks-List");
  }

  public void addSink(final SinkInfo info) {
    String name = info.getName();
    Hyperlink link = new Hyperlink(name, name);
    link.setStyleName("ks-SinkItem");

    list.add(link);
    sinks.add(info);
  }

  public SinkInfo find(String sinkName) {
    for (int i = 0; i < sinks.size(); ++i) {
      SinkInfo info = (SinkInfo) sinks.get(i);
      if (info.getName().equals(sinkName)) {
        return info;
      }
    }

    return null;
  }

  public void setSinkSelection(String name) {
    if (selectedSink != -1) {
      list.getWidget(selectedSink).removeStyleName("ks-SinkItem-selected");
    }
    
    for (int i = 0; i < sinks.size(); ++i) {
      SinkInfo info = (SinkInfo) sinks.get(i);
      if (info.getName().equals(name)) {
        selectedSink = i;
        list.getWidget(selectedSink).addStyleName("ks-SinkItem-selected");
        return;
      }
    }
  }

public ArrayList getSinks() {
	return sinks;
}
}
