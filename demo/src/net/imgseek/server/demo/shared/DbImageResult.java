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
package net.imgseek.server.demo.shared;

import com.google.gwt.user.client.rpc.IsSerializable;

public class DbImageResult implements IsSerializable {
	public DbImageResult() {
		super();
	}

	private Double score;

	public DbImageResult(Integer id, Double r, String url) {
		super();
		this.id = id;
		this.setScore(r);
		this.url = url;
	}

	private int id;

	public int getId() {
		return id;
	}

	public void setId(int id) {
		this.id = id;
	}

	public String getUrl() {
		return url;
	}

	public void setUrl(String url) {
		this.url = url;
	}

	public Double getScore() {
		return score;
	}

	public void setScore(Double r) {
		this.score = r;
	}

	private String url;
}
