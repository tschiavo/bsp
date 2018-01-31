/*
   Copyright 2013 The Moore Collective, LLC
*/

package org.yerr.beeaware.beacon;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Service;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.os.IBinder;
import android.provider.Settings;
import android.util.Log;

import java.io.StringWriter;
import java.io.PrintWriter;
 
public class GPSTracker extends Service implements LocationListener {
 
	private final static String CN = GPSTracker.class.getSimpleName();

    private final Context mSvcCtxt;
    private final Activity mAct;
 
	Location location;

    // The minimum distance to change Updates in meters
    private static final long MIN_DISTANCE_CHANGE_FOR_UPDATES = 1;
 
    // The minimum time between updates in milliseconds
    private static final long MIN_TIME_BW_UPDATES = 1000 * 10;

	private boolean tryingForGPS = false;
	private boolean tryingForNetwork = false;
 
	private boolean queryInProgress = false;

    // Declaring a Location Manager
    public GPSTracker(Context svcContext, Activity appActivity) {
        this.mSvcCtxt = svcContext;
        this.mAct = appActivity;
    }

	private LocationManager getLocationManager() {
		return (LocationManager) mSvcCtxt.getSystemService(LOCATION_SERVICE);
	}
 
    public void startLocationQuery() {
		if(!queryInProgress) {
			try {
				Log.d(CN, "Context " + mSvcCtxt);
				final LocationManager locationManager = getLocationManager();
	 
				if(locationManager != null) {
					boolean isGPSEnabled = locationManager
						.isProviderEnabled(LocationManager.GPS_PROVIDER);
					boolean isNetworkEnabled = locationManager
						.isProviderEnabled(LocationManager.NETWORK_PROVIDER);

					if(isGPSEnabled && !tryingForGPS) {
						tryingForGPS = true;
						final LocationListener locListener = this;
						mAct.runOnUiThread(new Runnable() { 
						@Override
						public void run() {
						locationManager.requestSingleUpdate(
							LocationManager.GPS_PROVIDER,
							locListener,
							null);
						}});
						queryInProgress = true;
						Log.d(CN, "GPS Updates Registered");
					} else if(isNetworkEnabled && !tryingForNetwork) {
						tryingForNetwork = true;
						final LocationListener locListener = this;
						mAct.runOnUiThread(new Runnable() { 
						@Override
						public void run() {
						locationManager.requestSingleUpdate(
							LocationManager.NETWORK_PROVIDER,
							locListener,
							null);
						}});
						queryInProgress = true;
						Log.d(CN, "Network Updates Registered");
					}
				}
			} catch (Exception e) {
				StringWriter sw = new StringWriter();
				PrintWriter pw = new PrintWriter(sw);
				e.printStackTrace(pw);
				Log.d(CN, sw.toString());
			}
		}
    }

	public boolean isQueryInProgress() {
		return queryInProgress;
	}

	public Location getFreshLocation() {
		Location ret = location;
		this.location = null;
		return ret;
	}
     
    /**
     * Stop using GPS listener
     * Calling this function will stop using GPS in your app
     * */
    public void removeUpdates(){
		LocationManager lm = getLocationManager();
        if(lm != null){
			Log.d(CN, "Removing Updates");
            lm.removeUpdates(GPSTracker.this);
        }
		tryingForGPS = false;
		tryingForNetwork = false;
		queryInProgress = false;
    }
     
    @Override
    public void onLocationChanged(Location location) {
		this.location = location;
		removeUpdates();
    }
 
    @Override
    public void onProviderDisabled(String provider) {
    }
 
    @Override
    public void onProviderEnabled(String provider) {
    }
 
    @Override
    public void onStatusChanged(String provider, int status, Bundle extras) {
    }

	@Override
	public IBinder onBind(Intent i) {
		return null;
	}
}
