/*
   Copyright 2013 The Moore Collective, LLC
*/
package org.yerr.beeaware.beacon;

import android.content.BroadcastReceiver;  
import android.content.Context;  
import android.content.Intent;  
import android.content.SharedPreferences;  
import android.preference.PreferenceManager; 

public class BootReceiver extends BroadcastReceiver {  

	@Override  
	public void onReceive(Context context, Intent intent) {  
		if ("android.intent.action.BOOT_COMPLETED".equals(
			intent.getAction())) {  
			Intent bgs = new Intent(context, BackgroundService.class);  
			context.startService(bgs);  
		}
	}  
}  
