/**
 * 
 */
package net.imgseek.server.admin.client;

import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.RootPanel;

/**
 * @author rnc
 *
 */
/**
 * A very simple popup that closes automatically when you click off of it.
 */
public class ProgressPopup extends PopupPanel {
	HTML contents ;
	public ProgressPopup() {
		super(true);

		contents = new HTML(getHTMLTemplate(""));
		setWidget(contents);

		setStyleName("ks-popups-Popup");
	}
	
	private String getHTMLTemplate(String msg) {
		return 
		"<table><tr><td><img src='wait22trans.gif'/></td><td><p><font color='#777777'>Please wait ...</font><br/>"+msg+"</p></td></tr></table>";				
	}
	
	public void show(String msg) {
		
		setPopupPosition(RootPanel.get().getOffsetWidth()/2,RootPanel.get().getOffsetHeight()/2);
		contents.setHTML(getHTMLTemplate(msg));
		super.show();
	}
}