//
//  LocationDatabase.h
//  Beacon
//
//  Created by Canvas on 9/10/13.
//
//

#import <Foundation/Foundation.h>
#import <sqlite3.h>

@interface LocationDatabase : NSObject {
    sqlite3* _database;
    NSString* databasePath;
}

+ (LocationDatabase*)database;

- (void)initDb;
- (NSArray*)location;
- (NSArray*)locations:(int)count;
- (int)locationCount;

- (void)removeLocations:(int)count;
- (void) add:(double) lat :(double) lon :(NSDate*) time :(double)alt :(double)acc;

@end
