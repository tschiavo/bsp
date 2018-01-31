//
//  Controller.m
//  Beacon
//
//  Created by Canvas on 9/9/13.
//
//

#import "Controller.h"

@implementation Controller
@synthesize lat;
@synthesize lon;

-(id)init {
    self = [super init];
    
    if(self) {
        
        NSString *errorDesc = nil;
        NSPropertyListFormat format;
        
        NSString *rootPath = [NSSearchPathForDirectoriesInDomains(NSDocumentDirectory,
                                                                  NSUserDomainMask, YES) objectAtIndex:0];
        
        NSString *plistPath;
        
        plistPath = [rootPath stringByAppendingPathComponent:@"Data.plist"];
        
        NSData *plistXML = [[NSFileManager defaultManager] contentsAtPath:plistPath];
        
        NSDictionary *temp = (NSDictionary *)[NSPropertyListSerialization
                                              propertyListFromData:plistXML
                                              mutabilityOption:NSPropertyListMutableContainersAndLeaves
                                              format:&format
                                              errorDescription:&errorDesc];
        if (!temp) {
            NSLog(@"Error reading plist: %@, format: %d", errorDesc, format);
        }
        
        self.lon = [temp objectForKey:@"location"];
        
        NSLog(@"%@", self.lon);
        
        //self.lat = [NSMutableArray arrayWithArray:[temp objectForKey:@"location"]];
    }
    
    return self;
}

@end
