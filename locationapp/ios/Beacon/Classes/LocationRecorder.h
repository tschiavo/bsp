/********* LocationPolling.h Cordova Plugin Header *******/

#import <Cordova/CDV.h>
#import "LocationService.h"

@interface LocationRecorder : CDVPlugin <CoreLocationControllerDelegate>
@property (nonatomic, retain) LocationService *CLController;
@property BOOL serviceRunning;
@property int pollingInterval;
@property int batchSize;
@property double startTime;

- (void)startService:(CDVInvokedUrlCommand*)command;
- (void)isServiceRunning:(CDVInvokedUrlCommand*)command;
- (void)stopService:(CDVInvokedUrlCommand*)command;

- (void)setPollingIntervalSeconds:(CDVInvokedUrlCommand*)command;
- (void)getPollingIntervalSeconds:(CDVInvokedUrlCommand*)command;

- (void)setBatchUploadSize:(CDVInvokedUrlCommand*)command;
- (void)getBatchUploadSize:(CDVInvokedUrlCommand*)command;

- (void)removeOldestItem:(CDVInvokedUrlCommand*)command;
- (void)removeOldestItems:(CDVInvokedUrlCommand*)command;

- (void)getItemCount:(CDVInvokedUrlCommand*)command;
- (void)getOldestItem:(CDVInvokedUrlCommand*)command;
- (void)getOldestItems:(CDVInvokedUrlCommand*)command;

@end

