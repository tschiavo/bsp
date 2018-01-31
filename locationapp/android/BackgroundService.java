/*
   Copyright 2013 The Moore Collective, LLC
*/
package org.yerr.beeaware.beacon;

import android.app.Activity;
import android.app.Service;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.IBinder;
import android.os.RemoteException;
import android.os.Handler;
import android.preference.PreferenceManager;
import android.util.Log;

import android.content.Context;

import android.location.Location;

import static java.util.concurrent.TimeUnit.*;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.ScheduledExecutorService;

import org.json.JSONObject;

import java.util.Date;


public class BackgroundService extends Service {  

	private static final String TAG = BackgroundService.class.getSimpleName();
	private final Object mResultLock = new Object();
	public static final String SERVICE_NAME = 
		"org.yerr.beeaware.beacon.BackgroundService";

    private Date nextRun = new Date();
    private Date now = new Date();

	public static Activity mAct = null;

	private static GPSTracker tracker;

    private final ScheduledExecutorService scheduler =
         Executors.newScheduledThreadPool(1);

    final Runnable poller = new Runnable() {
		public void run() {
			WebLog.Log("sending");
			DoScheduledAction();
		}
    };

    private void DoPollCycle() {
        Location l = tracker.getFreshLocation();
		if(l == null) {
			if(!tracker.isQueryInProgress()) {
				tracker.startLocationQuery();
			}
		} else {
			Log.d(TAG, "got a location: " +
				l.getTime() + " " +
				l.getLatitude() + " " +
				l.getLongitude() + " " +
				l.getAltitude() + " " +
				l.getAccuracy());

			WebLog.Log("got" + 
				l.getProvider() + "," +
				l.getTime() + "," +
				l.getLatitude() + "," +
				l.getLongitude() + "," +
				l.getAltitude() + "," +
				l.getAccuracy()
			);

			Log.d(TAG, "adding sql loc");
			LocalStorage.getDB(this).execSQL(
				"insert into locations values (" +
					l.getTime() + ", " +
					l.getLatitude() + ", " +
					l.getLongitude() + ", " +
					l.getAltitude() + ", " +
					l.getAccuracy() + ");");
			Log.d(TAG, "added sql loc");
		}
    }

	BackgroundServiceApi.Stub apiEndpoint = new BackgroundServiceApi.Stub() {

		public void setPollingIntervalSeconds(int secs) {
			Log.d(TAG, "Setting Polling Interval");
			SharedPreferences sp = getSharedPreferences(SERVICE_NAME, 0);
			SharedPreferences.Editor editor = sp.edit();
			editor.putInt("pollingIntervalSeconds", secs);
			editor.commit();
		}

		public int getPollingIntervalSeconds() {
			SharedPreferences sp = getSharedPreferences(SERVICE_NAME, 0);
			return sp.getInt("pollingIntervalSeconds", -1);
		}

	};

    private void DoScheduledAction() {
		try {
			Date now = new Date();
			Log.d(TAG, "checking " + now);
			long delta = this.nextRun.getTime() - now.getTime();
			WebLog.Log("check-" + now.getTime() + "-delta" + delta + ")"); 
			if(now.after(nextRun))
			{
				int interval_s = apiEndpoint.getPollingIntervalSeconds();
				if(interval_s >= 1) {
					int interval_ms = interval_s * 1000;
					this.nextRun.setTime(
						new Date(nextRun.getTime() + interval_ms).getTime());
					WebLog.Log("record-" + now.getTime());
					DoPollCycle();
				} else {
					Log.d(TAG, "Polling interval is too short: " + 
						interval_s);
				}
			}
		} catch (Exception e) {
			WebLog.Log("ExceptionDoing");
		}
    }

	@Override  
	public IBinder onBind(Intent intent) {
		Log.i(TAG, "onBind called");
		return apiEndpoint;
	}     

	@Override  
	public void onCreate() {     
		super.onCreate();     

		Log.i(TAG, "Service creating");

		synchronized (mResultLock) {
			Log.i(TAG, "Syncing result");
		};

		tracker = new GPSTracker(this, mAct);
        Log.d(TAG, "tracker constructed");

		try {
			final ScheduledFuture pollerHandle =
				scheduler.scheduleWithFixedDelay(
					this.poller, 0, 1000, MILLISECONDS);
			scheduler.schedule(poller, 0, SECONDS);
		} catch(Exception e) {
			Log.d(TAG, "Scheduling failed");
			WebLog.Log("Exceptionfailed");
		}	
	}

	@Override
	public void onStart(Intent intent, int startId) {
		Log.i(TAG, "Service started");       
	}

	public void onStop() {
		Log.i(TAG, "Service stopping");
	}

	@Override  
	public void onDestroy() {     
		super.onDestroy();     
		Log.i(TAG, "Service destroying");

		Log.i(TAG, "Stopping timer task");
		scheduler.shutdown();
	}
}  
