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
package net.imgseek.server.demo.server;

import java.net.MalformedURLException;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import net.imgseek.server.demo.client.IskDemoService;
import net.imgseek.server.demo.shared.DbImageResult;

import org.apache.xmlrpc.XmlRpcException;
import org.apache.xmlrpc.client.XmlRpcClient;
import org.apache.xmlrpc.client.XmlRpcClientConfigImpl;

import com.google.gwt.user.server.rpc.RemoteServiceServlet;

/**
 * The server side implementation of the RPC service.
 */
@SuppressWarnings("serial")
public class IskDemoServiceImpl extends RemoteServiceServlet implements
		IskDemoService {

	private static final int DB_NUM_IMGS = 30607; // total number of images on
													// DB. Used for quickly
													// selecting random ids
	private XmlRpcClient client;
	private ImageDb imgIdDb = new ImageDb();
	private Random generator;

	public IskDemoServiceImpl() throws MalformedURLException {
		super();

		XmlRpcClientConfigImpl config = new XmlRpcClientConfigImpl();
		config.setServerURL(new URL("http://127.0.0.1:31128/RPC")); // isk-daemon
																	// XML-RPC
																	// endpoint
																	// URL
		config.setEnabledForExtensions(true);
		client = new XmlRpcClient();
		client.setConfig(config);
		generator = new Random(1958027);

	}

	public DbImageResult whitelist(DbImageResult l) {
		return null;
	}

	@Override
	public List<DbImageResult> queryImgID(long id, int numres, boolean fast) {
		List<DbImageResult> dbImageList = new ArrayList<DbImageResult>();

		if (id == 0) { // random images
			for (int i = 0; i < numres; i++) {
				int rid = generator.nextInt(DB_NUM_IMGS) + 1; // +1 so id 0 is
																// not selected
				dbImageList.add(new DbImageResult(rid, 0.0, this.imgIdDb
						.getUrlForImg(rid)));
			}
		} else { // similarity search
			// searching by default on DB Space 1
			Object[] params = new Object[] { 1, (int) id, numres, fast };
			try {
				Object[] result = (Object[]) client.execute("queryImgID",
						params);
				for (Object res : result) {
					Object[] r = (Object[]) res;
					int rid = (Integer) r[0];
					dbImageList.add(new DbImageResult(rid, (Double) r[1],
							this.imgIdDb.getUrlForImg(rid)));
				}
				return dbImageList;
			} catch (XmlRpcException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		return dbImageList;
	}
}
