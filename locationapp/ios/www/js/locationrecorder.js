var LocationRecorderIF = function() {};

LocationRecorderIF.prototype.startService = 
	function(succFun, failFun) { cordova.exec( succFun, failFun, 
		'LocationRecorder', 'startService', []);
}

LocationRecorderIF.prototype.isServiceRunning = 
	function(succFun, failFun) { cordova.exec( succFun, failFun, 
		'LocationRecorder', 'isServiceRunning', []);
}

LocationRecorderIF.prototype.stopService = 
	function(succFun, failFun) { cordova.exec( succFun, failFun, 
		'LocationRecorder', 'stopService', []);
}

LocationRecorderIF.prototype.setPollingIntervalSeconds = 
	function(params, succFun, failFun) { cordova.exec( succFun, failFun, 
		'LocationRecorder', 'setPollingIntervalSeconds', params);
}

LocationRecorderIF.prototype.getPollingIntervalSeconds = 
	function(succFun, failFun) { cordova.exec( succFun, failFun, 
		'LocationRecorder', 'getPollingIntervalSeconds', []);
}

LocationRecorderIF.prototype.setBatchUploadSize =
function(params, succFun, failFun) { cordova.exec( succFun, failFun,
        'LocationRecorder', 'setBatchUploadSize', params);
}

LocationRecorderIF.prototype.getBatchUploadSize =
function(succFun, failFun) { cordova.exec( succFun, failFun,
        'LocationRecorder', 'getBatchUploadSize', []);
}

LocationRecorderIF.prototype.getItemCount = 
	function(succFun, failFun) { cordova.exec( succFun, failFun, 
		'LocationRecorder', 'getItemCount', []);
}

LocationRecorderIF.prototype.getOldestItem = 
	function(succFun, failFun) { cordova.exec( succFun, failFun, 
		'LocationRecorder', 'getOldestItem', []);
}

LocationRecorderIF.prototype.getOldestItems = 
	function(params, succFun,failFun) { cordova.exec( succFun, failFun, 
		'LocationRecorder', 'getOldestItems', params);
}

LocationRecorderIF.prototype.removeOldestItem = 
	function(succFun, failFun) { cordova.exec( succFun, failFun, 
		'LocationRecorder', 'removeOldestItem', []);
}

LocationRecorderIF.prototype.removeOldestItems = 
	function(params, succFun, failFun) { cordova.exec( succFun, failFun, 
		'LocationRecorder', 'removeOldestItems', params);
}

if(!window.plugins) {
    window.plugins = {};
}
if (!window.plugins.LocationRecorder) {
    window.plugins.LocationRecorder = new LocationRecorderIF();
}
