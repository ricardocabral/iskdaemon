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

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.StringTokenizer;

public class ImageDb {
	private Map<Integer, String> idtoname = new HashMap<Integer, String>();
	private String dataFile = "/var/imgid.db"; // CSV file mapping image IDs
												// into their JPG url

	public String getUrlForImg(int id) {
		return "/isk/img/" + idtoname.get(id);
	}

	public ImageDb() {
		File file = new File(dataFile);

		BufferedReader bufRdr = null;
		try {
			bufRdr = new BufferedReader(new FileReader(file));
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		String line = null;

		// read each line of text file
		try {
			while ((line = bufRdr.readLine()) != null) {
				StringTokenizer st = new StringTokenizer(line, ",");
				int id = Integer.parseInt(st.nextToken());
				String name = st.nextToken();
				idtoname.put(id, name);
			}
		} catch (NumberFormatException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		// close the file
		try {
			bufRdr.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

}