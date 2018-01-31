//
//  LocationDatabase.m
//  Beacon
//
//  Created by Canvas on 9/10/13.
//
//

#import "LocationDatabase.h"

@implementation LocationDatabase

static LocationDatabase *_database;

+ (LocationDatabase*) database {
    if(_database == nil) {
        _database = [[LocationDatabase alloc] init];
    }
    return _database;
}

- (void)add:(double)lat :(double)lon :(NSDate*)time :(double)alt :(double)acc
{
    
    NSString *query = [NSString stringWithFormat:@"INSERT INTO locations (lat, lon, time, alt, acc)\
                       VALUES ('%f', '%f', '%f', '%f', '%f')",
                       lat, lon, time.timeIntervalSince1970, alt, acc];
    
    sqlite3_stmt *statement;
    
    if(sqlite3_prepare_v2(_database, [query UTF8String], -1, &statement, nil) == SQLITE_OK) {
        if(sqlite3_step(statement) != SQLITE_DONE) {
            NSLog(@"Error: %s", sqlite3_errmsg(_database));
        }
    } else {
        NSLog(@"Error: %s", sqlite3_errmsg(_database));
    }

}


- (NSArray *)location
{
    NSMutableArray *location = [NSMutableArray.alloc init];

    NSString *query = @"SELECT lat, lon, acc, time, alt FROM locations ORDER BY time DESC LIMIT 1";
    
    sqlite3_stmt *statement;
    
    if(sqlite3_prepare_v2(_database, [query UTF8String], -1, &statement, nil) == SQLITE_OK) {
        
        while (sqlite3_step(statement) == SQLITE_ROW) {
            
            NSNumber *lat = [NSNumber numberWithDouble: sqlite3_column_double(statement, 0)];
            NSNumber *lon = [NSNumber numberWithDouble: sqlite3_column_double(statement, 1)];
            NSNumber *acc = [NSNumber numberWithDouble: sqlite3_column_double(statement, 2)];
            NSNumber *time = [NSNumber numberWithLong: sqlite3_column_int(statement, 3)];
            NSNumber *alt = [NSNumber numberWithLong: sqlite3_column_int(statement, 4)];

            
            NSDictionary *dict = @{
                                   @"lat" : lat,
                                   @"lon" : lon,
                                   @"acc" : acc,
                                   @"time" :time,
                                   @"alt" :alt
                                   };
            [location addObject:dict];
        }
        
        sqlite3_finalize(statement);
    }
    NSDictionary *retval = @{@"location":location};
    return [retval copy];
}

- (int)locationCount
{
    NSString* query = @"SELECT COUNT(*) FROM locations";
    sqlite3_stmt *statement;
    int count = false;
    if(sqlite3_prepare_v2(_database, [query UTF8String], -1, &statement, nil) == SQLITE_OK) {
        sqlite3_step(statement);
        count = sqlite3_column_int(statement, 0);
        sqlite3_finalize(statement);
    }
    return count;
}

- (void)removeLocations:(int)count
{
    NSString *query = [NSString stringWithFormat:@"DELETE FROM locations WHERE ROWID IN (SELECT ROWID FROM locations ORDER BY time ASC LIMIT '%d')", count];

    char *errMsg = 0;
    sqlite3_exec(_database, [query UTF8String], NULL, NULL, &errMsg);
}

// Get 'count' latest records
- (NSArray *)locations:(int)count
{
    
    NSMutableArray *locations = [[NSMutableArray alloc] init];
    
    NSString *query = [NSString stringWithFormat:@"SELECT lat, lon, acc, time FROM locations ORDER BY time ASC LIMIT %d", count];
    
    sqlite3_stmt *statement;
    
    if(sqlite3_prepare_v2(_database, [query UTF8String], -1, &statement, nil) == SQLITE_OK) {
        
        while (sqlite3_step(statement) == SQLITE_ROW) {
            
            NSNumber *lat = [NSNumber numberWithDouble: sqlite3_column_double(statement, 0)];
            NSNumber *lon = [NSNumber numberWithDouble: sqlite3_column_double(statement, 1)];
            NSNumber *acc = [NSNumber numberWithDouble: sqlite3_column_double(statement, 2)];
            NSNumber *time = [NSNumber numberWithLong: sqlite3_column_int(statement, 3)];
            NSNumber *alt = [NSNumber numberWithLong: sqlite3_column_int(statement, 4)];

            
            NSDictionary *dict = @{
                                   @"lat" : lat,
                                   @"lon" : lon,
                                   @"acc" : acc,
                                   @"time" :time,
                                   @"alt" :alt
                                   };
            [locations addObject:dict];
        }
        
        sqlite3_finalize(statement);
    }
    NSDictionary *retval = @{@"locations":locations};
    return [retval copy];
}

- (id)init {
    if ((self = [super init])) {
        [self initDb];
    }
    return self;
}

-(void)initDb{
    NSString *docsDir;
    NSArray *dirPaths;
    
    // Get the documents directory
    dirPaths = NSSearchPathForDirectoriesInDomains
    (NSDocumentDirectory, NSUserDomainMask, YES);
    docsDir = dirPaths[0];
    
    // Build the path to the database file
    databasePath = [[NSString alloc] initWithString:[docsDir stringByAppendingPathComponent: @"locations.db"]];
    const char *dbpath = [databasePath UTF8String];
    
    NSFileManager *filemgr = [NSFileManager defaultManager];
    if ([filemgr fileExistsAtPath: databasePath ] == NO)
    {
        if (sqlite3_open(dbpath, &_database) == SQLITE_OK)
        {
            char *errMsg;
            const char *sql_stmt = "create table if not exists locations (time real primary key, lat real, lon real, alt real, acc real)";
            if (sqlite3_exec(_database, sql_stmt, NULL, NULL, &errMsg)
                != SQLITE_OK)
            {
                NSLog(@"Failed to create table");
            }
            NSLog(@"Successfully created table");
        }
        else {
            NSLog(@"Failed to create database");
        }
    }
    else {
        if (sqlite3_open(dbpath, &_database) == SQLITE_OK)
        {
              NSLog(@"Successfully opened database");
        } 
        else {
            NSLog(@"Failed to open database");
        }
    }
}

- (void)dealloc {
    sqlite3_close(_database);
}
@end
