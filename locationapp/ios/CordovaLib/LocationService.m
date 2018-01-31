//
//  CoreLocationController.m
//  Beacon
//
//  Created by Canvas on 9/9/13.
//
//

#import "LocationService.h"

@implementation LocationService

@synthesize locMgr, delegate;

- (id)init {
	self = [super init];
    
	if(self != nil) {
		self.locMgr = [[CLLocationManager alloc] init];
		self.locMgr.delegate = self;
        self.locMgr.desiredAccuracy = kCLLocationAccuracyBest;
        //self.locMgr.distanceFilter = kCLDistanceFilterNone; //default setting, all horizontal distance changes
        //self.locMgr.activityType = CLActivityTypeOther; //since we are not explicitly vehicular or fitness
        self.locMgr.pausesLocationUpdatesAutomatically = NO;
	}
    
	return self;
}

- (void)locationManager:(CLLocationManager *)manager didUpdateToLocation:(CLLocation *)newLocation fromLocation:(CLLocation *)oldLocation {
    [self.delegate locationUpdate:newLocation];
}

- (void)locationManager:(CLLocationManager *)manager didFailWithError:(NSError *)error {
    [self.delegate locationError:error];
}

- (void)dealloc {
	//self.locMgr;
}
@end
