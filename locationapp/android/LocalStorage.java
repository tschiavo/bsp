/*
   Copyright 2013 The Moore Collective, LLC
*/
package org.yerr.beeaware.beacon;

import android.content.Context;

import android.database.sqlite.SQLiteOpenHelper;
import android.database.sqlite.SQLiteDatabase;

public class LocalStorage extends SQLiteOpenHelper {

    public static LocalStorage db = null;

    public static SQLiteDatabase getDB(Context c) {
        if(db == null) {
            db = new LocalStorage(c);
        }
        return db.getWritableDatabase();
    }

    private static final int DATABASE_VERSION = 2;
    private static final String DICTIONARY_TABLE_CREATE =
		"create table locations (" +
		"	time timestamp," +
		"	lat float," +
		"	lon float," +
		"	alt float," +
		"	acc float" +
		");";

    LocalStorage(Context context) {
        super(context, "BeeawareBeacon", null, DATABASE_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL(DICTIONARY_TABLE_CREATE);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldV, int newV) {
    }
}
