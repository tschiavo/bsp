//
//  Controller.h
//  Beacon
//
//  Created by Canvas on 9/9/13.
//
//

#import <Foundation/Foundation.h>

@interface Controller : NSObject {
    NSString *lat;
    NSString *lon;
}

@property (copy, nonatomic) NSString *lat;
@property (retain, nonatomic) NSString *lon;

@end
