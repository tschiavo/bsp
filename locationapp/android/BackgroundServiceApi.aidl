/*
   Copyright 2013 The Moore Collective, LLC
*/
package org.yerr.beeaware.beacon;

interface BackgroundServiceApi {
	int getPollingIntervalSeconds();
	void setPollingIntervalSeconds(int secs);
}
