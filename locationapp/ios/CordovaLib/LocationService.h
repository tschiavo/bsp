//
//  CoreLocationController.h
//  Beacon
//
//  Created by Canvas on 9/9/13.
//
//

#import <Foundation/Foundation.h>
#import <CoreLocation/CoreLocation.h>

@protocol CoreLocationControllerDelegate

@required
- (void)locationUpdate:(CLLocation *)location; // Our location updates are sent here
- (void)locationError:(NSError *)error; // Any errors are sent here
@end

@interface LocationService : NSObject <CLLocationManagerDelegate> {
	CLLocationManager *locMgr;
	id __weak delegate;
}

@property (nonatomic, strong) CLLocationManager *locMgr;
@property (nonatomic, weak) id delegate;

@end
