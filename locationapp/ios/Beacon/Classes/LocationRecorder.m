/********* LocationPolling.m Cordova Plugin Implementation *******/

#import <Cordova/CDV.h>
#import "Controller.h"
#import "LocationRecorder.h"
#import "LocationDatabase.h"

@implementation LocationRecorder

//
// Initialization Section (run once)
//
- (void)pluginInitialize
{
    // get polling interval from property list. Run in background.
    //[self.commandDelegate runInBackground:^{[self readConf];}];
    self.pollingInterval = [[self readConf:@"pollingInterval"] intValue];
    if(self.pollingInterval == 0){
        self.pollingInterval = 60;
    }
    
    //NSLog(@"polling interval == %d",self.pollingInterval);
    
    self.batchSize = [[self readConf:@"batchUpdateSize"] intValue];
    if(self.batchSize == 0){
        self.batchSize = 1;
    }
    
    //NSLog(@"batch size == %d",self.batchSize);

    
	self.CLController = [LocationService.alloc init];
	self.CLController.delegate = self;
    

/*
 */
    // add observers
    [NSNotificationCenter.defaultCenter addObserver:self
                                        selector:@selector(enteredBackground)
                                        name:UIApplicationDidEnterBackgroundNotification
                                        object: nil];
    
    [NSNotificationCenter.defaultCenter addObserver:self
                                        selector:@selector(enteredForeground)
                                        name:UIApplicationWillEnterForegroundNotification
                                        object: nil];
/*
 */
    NSLog(@"LocationRecorder Plugin Initialized");
}

//
// Background Callback Section
//
/*
 */
- (void)enteredBackground
{
    [self.CLController.locMgr stopUpdatingLocation];
    if(self.serviceRunning && CLLocationManager.locationServicesEnabled && (CLLocationManager.authorizationStatus == kCLAuthorizationStatusAuthorized)) {
        //[self.commandDelegate runInBackground:^{[self.CLController.locMgr startMonitoringSignificantLocationChanges];}];
        [self.commandDelegate runInBackground:^{[self.CLController.locMgr startUpdatingLocation];}];
        NSLog(@"Monitoring only significant changes");
    }
}

- (void)enteredForeground
{
    [self.CLController.locMgr stopMonitoringSignificantLocationChanges];
    if(self.serviceRunning && CLLocationManager.locationServicesEnabled && (CLLocationManager.authorizationStatus == kCLAuthorizationStatusAuthorized)) {
        [self.commandDelegate runInBackground:^{[self.CLController.locMgr startUpdatingLocation];}];
        NSLog(@"Resume updating locations");
    }
}

//
// Location Callback Section
//
- (void)locationUpdate:(CLLocation *)location
{
    CLLocationCoordinate2D coordinate = location.coordinate;
    
    // if pollingInterval seconds passed since last update
    if(([NSDate.date timeIntervalSince1970] - self.startTime) >= self.pollingInterval) {
        self.startTime = [NSDate.date timeIntervalSince1970];
        NSLog(@"Writing to database: %f %f", location.coordinate.latitude, location.coordinate.longitude);
        [self.commandDelegate runInBackground:^{[LocationDatabase.database add:coordinate.latitude :coordinate.longitude :location.timestamp :location.altitude :location.horizontalAccuracy];}];
    }
}

- (void)locationError:(NSError *)error {
	NSLog(@"%@", error.description);
}

//
//Configuration Section
//
- (NSString *)readConf:(NSString*)prop
{
    NSString *errorDesc = nil;
    NSPropertyListFormat format;
    NSString *plistPath;
    
    NSString *rootPath = [NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES)
                          objectAtIndex:0];
    plistPath = [rootPath stringByAppendingPathComponent:@"Data.plist"];
    
    if(![[NSFileManager defaultManager] fileExistsAtPath:plistPath]) {
        plistPath = [[NSBundle mainBundle] pathForResource:@"Data" ofType:@"plist"];
    }
    
    NSData *plistXML = [[NSFileManager defaultManager] contentsAtPath:plistPath];
    NSDictionary *temp = (NSDictionary *)[NSPropertyListSerialization
                                          propertyListFromData:plistXML
                                          mutabilityOption:NSPropertyListMutableContainersAndLeaves
                                          format:&format
                                          errorDescription:&errorDesc];
    if(!temp) {
        NSLog(@"Error reading plist: %@, format: %d", errorDesc, format);
    }
    
    //self.pollingInterval = [[temp objectForKey:@"pollingInterval"] intValue];
    return [temp objectForKey:prop];
}

- (void)writeConf:(NSString*)prop :(NSObject *)val
{
    NSString *error;
    NSString *rootPath = [NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES) objectAtIndex:0];
    NSString *plistPath = [rootPath stringByAppendingPathComponent:@"Data.plist"];
    
    NSDictionary *plistDict = [NSDictionary dictionaryWithObjects:[NSArray arrayWithObjects: val, nil]
                                                          forKeys:[NSArray arrayWithObjects: prop, nil]];
    
    NSData *plistData = [NSPropertyListSerialization dataFromPropertyList: plistDict
                                                                   format: NSPropertyListXMLFormat_v1_0
                                                         errorDescription: &error];
    if(plistData) {
        [plistData writeToFile:plistPath atomically:YES];
    } else {
        NSLog(@"%@", error);
    }
}

/*
 */

//
//Beeaware API Section
//
- (void)startService:(CDVInvokedUrlCommand*)command
{
    CDVPluginResult* result = nil;
    NSDictionary* retval = @{@"startService": [NSNumber numberWithBool:true]};
    self.startTime = 0;
    
    // check if location service enabled
    NSLog(@"services enabled %d",CLLocationManager.locationServicesEnabled);
    NSLog(@"status authorized %d",CLLocationManager.authorizationStatus == kCLAuthorizationStatusAuthorized);
    
    [CLLocationManager locationServicesEnabled];

    
    //if(CLLocationManager.locationServicesEnabled && (CLLocationManager.authorizationStatus == kCLAuthorizationStatusAuthorized)) {
        [self.commandDelegate runInBackground:^{[self.CLController.locMgr startUpdatingLocation];self.serviceRunning = true;}];
        result = [CDVPluginResult resultWithStatus:CDVCommandStatus_OK messageAsDictionary:retval];
        NSLog(@"service enabled and authorized");
    //} else {
    //    result = [CDVPluginResult resultWithStatus:CDVCommandStatus_ERROR messageAsString:@"Service not available"];
    //    NSLog(@"service NOT enabled and authorized: %d", CLLocationManager.authorizationStatus);
    //}
    
    [self.commandDelegate sendPluginResult:result callbackId:command.callbackId];
    //NSLog(@"LocationRecorder Service Started");
}

- (void)stopService:(CDVInvokedUrlCommand*)command
{
    NSDictionary* retval = @{@"stopService": [NSNumber numberWithBool:true]};
    [self.CLController.locMgr stopUpdatingLocation];
    CDVPluginResult* pluginResult = [CDVPluginResult resultWithStatus:CDVCommandStatus_OK messageAsDictionary:retval];
    self.serviceRunning = false;
    [self.commandDelegate sendPluginResult:pluginResult callbackId:command.callbackId];
}

- (void)isServiceRunning:(CDVInvokedUrlCommand *)command
{
    
    NSDictionary* retval = @{@"isRunning": [NSNumber numberWithBool:self.serviceRunning]};
    CDVPluginResult* result = [CDVPluginResult resultWithStatus:CDVCommandStatus_OK messageAsDictionary:retval];
    [self.commandDelegate sendPluginResult:result callbackId:command.callbackId];
}

-(void)removeOldestItems:(CDVInvokedUrlCommand *)command
{
    NSString* count = [command.arguments objectAtIndex:0];
    NSDictionary* retval = @{@"itemsRemoved":[NSNumber numberWithInt:count.integerValue]};
    
    // execute in background thread
    [self.commandDelegate runInBackground:^{[LocationDatabase.database removeLocations:count.intValue];
        CDVPluginResult* pluginResult = [CDVPluginResult resultWithStatus:CDVCommandStatus_OK messageAsDictionary:retval];
        [self.commandDelegate sendPluginResult:pluginResult callbackId:command.callbackId];
    }];
}

- (void)removeOldestItem:(CDVInvokedUrlCommand *)command
{
    NSDictionary* retval = @{@"itemRemoved":[NSNumber numberWithInt:1]};
    [self.commandDelegate runInBackground:^{[LocationDatabase.database removeLocations:1];
        CDVPluginResult* pluginResult = [CDVPluginResult resultWithStatus:CDVCommandStatus_OK messageAsDictionary:retval];
        [self.commandDelegate sendPluginResult:pluginResult callbackId:command.callbackId];
    }];
}

- (void)getPollingIntervalSeconds:(CDVInvokedUrlCommand *)command
{
    NSDictionary *retval = @{@"pollingIntervalSeconds" : [NSNumber numberWithInt:self.pollingInterval]};
    CDVPluginResult* result = [CDVPluginResult resultWithStatus:CDVCommandStatus_OK messageAsDictionary:retval];
    [self.commandDelegate sendPluginResult:result callbackId:command.callbackId];
    
}

- (void)setPollingIntervalSeconds:(CDVInvokedUrlCommand *)command
{
    NSString* pollingInterval = [command.arguments objectAtIndex:0];
    self.pollingInterval = pollingInterval.intValue;

    // store data in application property list
    [self.commandDelegate runInBackground:^{[self writeConf:@"pollingInterval" :[NSNumber numberWithInt:self.pollingInterval]];}];
    
    NSDictionary* retval = @{@"pollingIntervalSeconds":[NSNumber numberWithInt:self.pollingInterval]};
    CDVPluginResult* result = [CDVPluginResult resultWithStatus:CDVCommandStatus_OK messageAsDictionary:retval];
    [self.commandDelegate sendPluginResult:result callbackId:command.callbackId];
}

- (void)getBatchUploadSize:(CDVInvokedUrlCommand *)command
{
    NSDictionary *retval = @{@"batchUploadSize" : [NSNumber numberWithInt:self.batchSize]};
    CDVPluginResult* result = [CDVPluginResult resultWithStatus:CDVCommandStatus_OK messageAsDictionary:retval];
    [self.commandDelegate sendPluginResult:result callbackId:command.callbackId];
    
}

- (void)setBatchUploadSize:(CDVInvokedUrlCommand *)command
{
    NSString* batchSize = [command.arguments objectAtIndex:0];
    self.batchSize = batchSize.intValue;
    
    // store data in application property list
    [self.commandDelegate runInBackground:^{[self writeConf:@"batchUploadSize" :[NSNumber numberWithInt:self.batchSize]];}];
    
    NSDictionary* retval = @{@"batchUploadSize":[NSNumber numberWithInt:self.batchSize]};
    CDVPluginResult* result = [CDVPluginResult resultWithStatus:CDVCommandStatus_OK messageAsDictionary:retval];
    [self.commandDelegate sendPluginResult:result callbackId:command.callbackId];
}
- (void)getItemCount:(CDVInvokedUrlCommand *)command
{
    int count = [LocationDatabase.database locationCount];
    NSDictionary* retval = @{@"count":[NSNumber numberWithInt:count]};
    CDVPluginResult* result = [CDVPluginResult resultWithStatus:CDVCommandStatus_OK messageAsDictionary:retval];
    [self.commandDelegate sendPluginResult:result callbackId:command.callbackId];
}

- (void)getOldestItems:(CDVInvokedUrlCommand *)command
{
    NSString* count = [command.arguments objectAtIndex:0];
    NSArray *locations = [LocationDatabase.database locations:count.intValue];
    CDVPluginResult* result = [CDVPluginResult resultWithStatus:CDVCommandStatus_OK messageAsArray:locations];
    [self.commandDelegate sendPluginResult:result callbackId:command.callbackId];
}

- (void)getOldestItem:(CDVInvokedUrlCommand *)command
{
    NSArray *location = LocationDatabase.database.location;
    CDVPluginResult* result = [CDVPluginResult resultWithStatus:CDVCommandStatus_OK messageAsArray:location];
    [self.commandDelegate sendPluginResult:result callbackId:command.callbackId];
}

@end