package net.imgseek.server.demo.server;

import gwtupload.server.UploadAction;
import gwtupload.server.exceptions.UploadActionException;
import gwtupload.shared.UConsts;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Hashtable;
import java.util.List;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import net.imgseek.server.demo.shared.DbImageResult;

import org.apache.commons.fileupload.FileItem;
import org.apache.xmlrpc.XmlRpcException;

/**
 * This class sends by email, all the fields and files received by GWTUpload
 * servlet.
 * 
 * @author Manolo Carrasco Moñino
 * 
 */
public class UploadServlet extends UploadAction {
	private IskDaemonClient iskClient = new IskDaemonClient();

	private static final long serialVersionUID = 1L;

	Hashtable<String, String> receivedContentTypes = new Hashtable<String, String>();
	/**
	 * Maintain a list with received files and their content types.
	 */
	Hashtable<String, File> receivedFiles = new Hashtable<String, File>();

	private ImageDb imgIdDb = new ImageDb();

	/**
	 * Override executeAction to save the received files in a custom place and
	 * delete this items from session.
	 */
	@Override
	public String executeAction(HttpServletRequest request,
			List<FileItem> sessionFiles) throws UploadActionException {
		String response = "";
		List<DbImageResult> dbImageList = new ArrayList<DbImageResult>();
		int cont = 0;
		for (FileItem item : sessionFiles) {
			if (false == item.isFormField()) {
				cont++;
				try {
					// / Create a new file based on the remote file name in the
					// client
					// String saveName =
					// item.getName().replaceAll("[\\\\/><\\|\\s\"'{}()\\[\\]]+",
					// "_");
					// File file =new File("/tmp/" + saveName);

					// / Create a temporary file placed in /tmp (only works in
					// unix)
					// File file = File.createTempFile("upload-", ".bin", new
					// File("/tmp"));

					// / Create a temporary file placed in the default system
					// temp folder
					byte[] data = item.get();
					// searching by default on DB Space 1
					Object[] params = new Object[] { 1, data, 12, false };
					try {
						Object[] result = (Object[]) iskClient.client.execute(
								"queryImgBlob", params);
						for (Object res : result) {
							Object[] r = (Object[]) res;
							int rid = (Integer) r[0];
							response += (rid + ";");
							response += (r[1] + ";");
							response += (this.imgIdDb.getUrlForImg(rid) + ";");
						}

						// return "";
					} catch (XmlRpcException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}

				} catch (Exception e) {
					throw new UploadActionException(e.getMessage());
				}
			}
		}

		// / Remove files from session because we have a copy of them
		removeSessionFileItems(request);

		// / Send your customized message to the client.
		return response;
	}

	/**
	 * Get the content of an uploaded file.
	 */
	@Override
	public void getUploadedFile(HttpServletRequest request,
			HttpServletResponse response) throws IOException {
		String fieldName = request.getParameter(UConsts.PARAM_SHOW);
		File f = receivedFiles.get(fieldName);
		if (f != null) {
			response.setContentType(receivedContentTypes.get(fieldName));
			FileInputStream is = new FileInputStream(f);
			copyFromInputStreamToOutputStream(is, response.getOutputStream());
		} else {
			renderXmlResponse(request, response, XML_ERROR_ITEM_NOT_FOUND);
		}
	}
}
