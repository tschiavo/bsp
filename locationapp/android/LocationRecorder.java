/*
   Copyright 2013 The Moore Collective, LLC
*/
package org.yerr.beeaware.beacon;

import org.apache.cordova.CordovaWebView;
import org.apache.cordova.CordovaPlugin;
import org.apache.cordova.PluginResult;
import org.apache.cordova.CallbackContext;
import org.apache.cordova.CordovaInterface;

import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.HttpResponse;

import android.app.Activity;
import android.app.ActivityManager;
import android.app.ActivityManager.RunningServiceInfo;

import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;

import android.database.sqlite.SQLiteDatabase;
import android.database.Cursor;

import android.location.Location;

import android.os.IBinder;
import android.os.RemoteException;

import android.util.Log;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONException;

import java.util.LinkedList;

import static java.util.concurrent.TimeUnit.*;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.ScheduledExecutorService;

import java.util.Date;

import java.io.StringWriter;
import java.io.PrintWriter;

public class LocationRecorder extends CordovaPlugin {
 
	private static final String TAG = LocationRecorder.class.getSimpleName();

	private Context context;

	private Object mServiceConnectedLock = new Object();
	private Boolean mServiceConnected = null;
	private BackgroundServiceApi api;

	private SQLiteDatabase getDB() {
		return LocalStorage.getDB(this.context);
	}

	/*
	public void StartPollingThread() {
		Log.d(TAG, "starting thread");
		Thread t = new Thread(
			new Runnable() {
				@Override
				public void run() {
					try {
						while(true) {
							DoPollCycle();
							Thread.sleep(5000);
							Log.d(TAG, "done sleeping");
						}
					} catch (Exception e) {
						Log.d(TAG, "caught exception");
					} finally {
						Log.d(TAG, "finally");
					}
				}
			}, 
			"theThread");
		Log.d(TAG, "thread instantiated");
		t.start();
		isPolling = true;
	}
	*/

	@Override 
    public void initialize(CordovaInterface cordova, CordovaWebView webView) {
        super.initialize(cordova, webView);
		context = cordova.getActivity().getApplicationContext();
		BackgroundService.mAct = (Activity)context;
		Log.d(TAG, "context acquired");
    }

	@Override
    public boolean execute(String action, JSONArray args, 
		CallbackContext callbackContext) throws JSONException {

		try {
			Log.d(TAG, "handling action");

			if (action.equals("removeOldestItem")) {
				removeOldestItem();
				callbackContext.success();
				return true;
			} else if (action.equals("getOldestItem")) {
				JSONObject o = getOldestItemJSON();
				callbackContext.success(o);
				Log.d(TAG, o.toString());
				return true;
			} else if (action.equals("startService")) {
				Log.d(TAG, "startService");
				startService();
				Log.d(TAG, "startService returning");
				return true;
			} else if (action.equals("isServiceRunning")) {
				Log.d(TAG, "isServiceRunningJSON");
				JSONObject msg = isServiceRunningJSON();
				Log.d(TAG, "callbackContext");
				callbackContext.success(msg);
				Log.d(TAG, "isServiceRunningJSON returning");
				return true;
			} else if (action.equals("stopService")) {
				stopService();
				return true;
			} else if (action.equals("setPollingIntervalSeconds")) {
				setPollingIntervalSecondsJSON(args);
				return true;
			} else if (action.equals("getPollingIntervalSeconds")) {
				JSONObject msg = getPollingIntervalSecondsJSON();
				callbackContext.success(msg);
				return true;
			} else if (action.equals("getItemCount")) {
				JSONObject msg = getItemCountJSON();
				callbackContext.success(msg);
				return true;
			} else if (action.equals("getOldestItems")) {
				JSONObject msg = getOldestItemsJSON(args);
				callbackContext.success(msg);
				return true;
			} else if (action.equals("removeOldestItems")) {
				removeOldestItemsJSON(args);
				return true;
			}

		} catch (Exception e) {
			StringWriter sw = new StringWriter();
			PrintWriter pw = new PrintWriter(sw);
			e.printStackTrace(pw);
			Log.d(TAG, sw.toString());
		}

		Log.d(TAG, "Returning false: " + action + " " + args);
        return false;
    }

	private ServiceConnection serviceConnection = new ServiceConnection() {

		@Override
		public void onServiceConnected(ComponentName name, IBinder service) {
			api = BackgroundServiceApi.Stub.asInterface(service);
			//try {
			//	api.addListener(serviceListener);
			//} catch (RemoteException e) {
			//}
			Log.d(TAG, "Service connected");
			synchronized(mServiceConnectedLock) {
				mServiceConnected = true;
				mServiceConnectedLock.notify();
			}

		}

		@Override
		public void onServiceDisconnected(ComponentName name) {
			api = null;
			Log.d(TAG, "Service disconnected");
			synchronized(mServiceConnectedLock) {
				mServiceConnected = false;
				mServiceConnectedLock.notify();
			}
		}
	};

	private JSONObject isServiceRunningJSON()
	{
		boolean isRunning = isServiceRunning();

		JSONObject ret = new JSONObject();
		try {
			ret.put("isRunning", isRunning);
		} catch (Exception e) {
			Log.d(TAG, "JSONObject failed: " + e.getMessage());
		}
		return ret;
	}

	private boolean isServiceRunning()
	{
		boolean result = false;

		ActivityManager manager = 
			(ActivityManager)context.getSystemService(
				Context.ACTIVITY_SERVICE); 
		for (RunningServiceInfo service : manager.getRunningServices(
				Integer.MAX_VALUE)) { 
			String serviceName = service.service.getClassName();
			//Log.d(TAG, "Scanning services: " + serviceName);
			if (serviceName.equals(BackgroundService.SERVICE_NAME)) { 
				result = true; 
			} 
		} 

		return result;
	}

	private Intent getService(Context c) {
		return new Intent(c, BackgroundService.class);
	}

	private void stopService() {
		if(isServiceRunning()) {
			unbindService();
			Intent bgs = getService(context);
			context.stopService(bgs);
		}
	}

	private void startService() {
		if(!isServiceRunning()) {
			Intent bgs = getService(context);
			ComponentName cn = context.startService(bgs);
			if (cn != null) {
				bindService();
			} else {
				Log.d(TAG, "service does not exist");
			}
		} else {
			Log.d(TAG, "service is running");
		}
	}

	private void unbindService() {
		try {
			context.unbindService(serviceConnection);
		} catch (Exception e) {
			Log.d(TAG, "unbind failed: " + e.getMessage());
		}
	}

	private void bindService(boolean isRecursive) {
		if(isServiceRunning()) {
			if (context.bindService(getService(context), 
				serviceConnection, 0)) {

				Log.d(TAG, "Waiting for service connected lock");
				synchronized(mServiceConnectedLock) {
					while (mServiceConnected==null) {
						try {
							mServiceConnectedLock.wait();
							Log.d(TAG, "Service connected");
						} catch (InterruptedException e) {
							Log.d(TAG, "Service connection failed");
						}
					}
				}
			} else {
				Log.d(TAG, "bindService Failed");
			}
		} else if (!isRecursive) {
			startService();
			bindService(true);
		} else {
			Log.d(TAG, "Unable to start and bind to service");
		}
	}

	private void bindService() {
		bindService(false);
	}

	private int getPollingIntervalSeconds() {
		int ret = -1;

		if(api == null) {
			bindService();
		}

		if(api != null) {
			try {
				ret = api.getPollingIntervalSeconds();
			} catch (Exception e) {
				Log.d(TAG, "API call failed");
			}
		} else {
			Log.d(TAG, "API not bound");
		}

		return ret;
	}

	private JSONObject getPollingIntervalSecondsJSON() {
		JSONObject ret = new JSONObject(); 

		try {
			ret.put("pollingIntervalSeconds", getPollingIntervalSeconds());
		} catch (Exception e) {
			Log.d(TAG, "JSON put failed");
		}

		return ret;
	}

	private void setPollingIntervalSecondsJSON(JSONArray args) {

		int secs = -1;

		try {
			secs = args.getInt(0);	
		} catch (Exception e) {
			Log.d(TAG, "JSON getInt failed: " + e.getMessage());
		}

		if(api == null) {
			bindService();
		}
		
		if(api != null) {
			try { 
				Log.d(TAG, "Setting Polling Interval");
				api.setPollingIntervalSeconds(secs);
			} catch (Exception e) {
				Log.d(TAG, "API call failed: " + e.getMessage());
			}
		} else {
			Log.d(TAG, "API not bound");
		}
	}

	private void removeOldestItems(int count) {
		Log.d(TAG, "deleting location");

		String q = 
			"delete from locations where time in " + 
			"( " +
			"  select time " +
			"  from locations " + 
			"  order by time asc " +
			"  limit " + count + 
			");";
		getDB().execSQL(q);
	}

	private void removeOldestItemsJSON(JSONArray args) {
		int count = -1;

		try {
			count = args.getInt(0);	
		} catch (Exception e) {
			Log.d(TAG, "JSON getInt failed: " + e.getMessage());
		}
		
		if(count > 0) {
			removeOldestItems(count);
		} else {
			Log.d(TAG, "Count is too small: " + count);
		}
	}

	private void removeOldestItem() {
		removeOldestItems(1);
	}

	private JSONObject getOldestItemsJSON(JSONArray args) {

		JSONObject ret = new JSONObject();

		int count = -1;

		try {
			count = args.getInt(0);
		} catch (Exception e) {
			Log.d(TAG, "JSON getInt failed: " + e.getMessage());
		}

		if(count > 0) {
			ret = getOldestItemsJSON(count);
		} else {
			Log.d(TAG, "Count is too small: " + count);
		}

		return ret;
	}

	private JSONObject getOldestItemsJSON(int count) {
		JSONObject ret = new JSONObject();
		JSONArray retLocs = new JSONArray();

		if(count > 0) {
			Log.d(TAG, "getting location");

			String q = 
				"select " +
				"  time, lat, lon, alt, acc " +
				"from locations " + 
				"order by time asc "+
				"limit " + count +
				";";

			Cursor c = getDB().rawQuery(q, null);

			/*
			while(c.getCount() == 0) {
				try {
					Thread.sleep(500);
				} catch (Exception e) {
					Log.d(TAG, "Blew up while sleeping");
				}
				c = getDB().rawQuery(q, null);
			}
			*/

			while(c.moveToNext()) {
				try {
					JSONObject row = new JSONObject();
					row.put("time", c.getString(c.getColumnIndex("time")));
					row.put("lat", c.getDouble(c.getColumnIndex("lat")));
					row.put("lon", c.getDouble(c.getColumnIndex("lon")));
					row.put("alt", c.getDouble(c.getColumnIndex("alt")));
					row.put("acc", c.getDouble(c.getColumnIndex("acc")));
					retLocs.put(row);
				} catch (Exception e) {
					Log.d(TAG, "JSONObject failed: " + e.getMessage());
				}
			}

			try {
				ret.put("locations", retLocs);
			} catch (Exception e) {
				Log.d(TAG, "JSONObject put failed: " + e.getMessage());
			}
		}

		return ret;
	}

	private JSONObject getOldestItemJSON() {
		return getOldestItemsJSON(1);
	}

	private JSONObject getItemCountJSON() {
		JSONObject ret = new JSONObject();

		Log.d(TAG, "getting count");

		String q = 
			"select " +
			"  count(*)" +
			"from locations " + 
			";";

		Cursor c = getDB().rawQuery(q, null);

		if(c.moveToNext()) {
			try {
				ret.put("count", c.getDouble(c.getColumnIndex("count(*)")));
			} catch (Exception e) {
				Log.d(TAG, "JSONObject failed: " + e.getMessage());
			}
		} else {
			try {
				ret.put("count", -1);
			} catch (Exception e) {
				Log.d(TAG, "JSONObject failed: " + e.getMessage());
			}
		}

		return ret;
	}
}
