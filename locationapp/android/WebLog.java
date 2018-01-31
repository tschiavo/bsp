/*
   Copyright 2013 The Moore Collective, LLC
*/
package org.yerr.beeaware.beacon;

import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.HttpResponse;

public class WebLog {
 
	public static void Log(String string) {
		try {
            /*
			HttpClient httpclient = new DefaultHttpClient();
			HttpResponse response = httpclient.execute(new HttpGet(
				"http://beeaware.spriggle.net/?" + string
			));
            */
		} catch (Exception e) {
		}
	}
}
