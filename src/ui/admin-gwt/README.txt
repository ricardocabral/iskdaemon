Open this project with the latest Eclipse and install Google GWT plugins.
All admin UI code is at the net.imgseek.server.admin.client package.
After changes are made to the Java code, it needs to be compiled into GWT Javascript:
Click on the "GWT Compile Project" on the Google toolbar icon.
GWT will place the output html+css+js is placed at src/ui/admin-gwt/war/iskdaemon_admin
All this content needs to be copied to src/ui/admin-www:
rm -fr ui/admin-www/* && cp -r ui/admin-gwt/war/iskdaemon_admin/* ui/admin-www 
