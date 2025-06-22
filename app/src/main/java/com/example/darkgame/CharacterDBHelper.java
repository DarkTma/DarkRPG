package com.example.darkgame;

import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.content.ContentValues;
import android.database.Cursor;

public class CharacterDBHelper extends SQLiteOpenHelper {

    private static final String DATABASE_NAME = "character.db";
    private static final int DATABASE_VERSION = 1;

    private static final String TABLE_NAME = "character";
    private static final String COL_NAME = "name";
    private static final String COL_MAX_HP = "max_hp";
    private static final String COL_CURR_HP = "curr_hp";
    private static final String COL_DEFENSE = "defense";
    private static final String COL_SPEED = "speed";
    private static final String COL_MAX_MANA = "max_mana";
    private static final String COL_CURR_MANA = "curr_mana";
    private static final String COL_HP_REGEN = "hp_regen";
    private static final String COL_MANA_REGEN = "mana_regen";
    private static final String COL_IMAGE_URL = "image_url";

    public CharacterDBHelper(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL(
                "CREATE TABLE " + TABLE_NAME + " (" +
                        "id INTEGER PRIMARY KEY AUTOINCREMENT," +
                        COL_NAME + " TEXT," +
                        COL_MAX_HP + " INTEGER," +
                        COL_CURR_HP + " INTEGER," +
                        COL_DEFENSE + " INTEGER," +
                        COL_SPEED + " INTEGER," +
                        COL_MAX_MANA + " INTEGER," +
                        COL_CURR_MANA + " INTEGER," +
                        COL_HP_REGEN + " INTEGER," +
                        COL_MANA_REGEN + " INTEGER," +
                        COL_IMAGE_URL + " TEXT)"
        );
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_NAME);
        onCreate(db);
    }

    public void saveCharacter(Character character, String imageUrl) {
        SQLiteDatabase db = this.getWritableDatabase();
        db.delete(TABLE_NAME, null, null); // сохраняем только 1

        ContentValues values = new ContentValues();
        values.put(COL_NAME, character.getName());
        values.put(COL_MAX_HP, character.getMaxHp());
        values.put(COL_CURR_HP, character.getCurrentHp());
        values.put(COL_DEFENSE, character.getDefense());
        values.put(COL_SPEED, character.getSpeed());
        values.put(COL_MAX_MANA, character.getMaxMana());
        values.put(COL_CURR_MANA, character.getCurrentMana());
        values.put(COL_HP_REGEN, character.getHpRegen());
        values.put(COL_MANA_REGEN, character.getManaRegen());
        values.put(COL_IMAGE_URL, imageUrl);

        db.insert(TABLE_NAME, null, values);
        db.close();
    }

    public Character getCharacter() {
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor cursor = db.rawQuery("SELECT * FROM " + TABLE_NAME + " LIMIT 1", null);

        if (cursor.moveToFirst()) {
            String name = cursor.getString(cursor.getColumnIndexOrThrow(COL_NAME));
            int maxHp = cursor.getInt(cursor.getColumnIndexOrThrow(COL_MAX_HP));
            int currHp = cursor.getInt(cursor.getColumnIndexOrThrow(COL_CURR_HP));
            int defense = cursor.getInt(cursor.getColumnIndexOrThrow(COL_DEFENSE));
            int speed = cursor.getInt(cursor.getColumnIndexOrThrow(COL_SPEED));
            int maxMana = cursor.getInt(cursor.getColumnIndexOrThrow(COL_MAX_MANA));
            int currMana = cursor.getInt(cursor.getColumnIndexOrThrow(COL_CURR_MANA));
            int hpRegen = cursor.getInt(cursor.getColumnIndexOrThrow(COL_HP_REGEN));
            int manaRegen = cursor.getInt(cursor.getColumnIndexOrThrow(COL_MANA_REGEN));

            Character character = new Character(name, maxHp, defense, speed, maxMana, hpRegen, manaRegen);

            // Принудительно установить текущее HP и Mana
            character.takeDamage(maxHp - currHp); // уменьшаем HP до нужного
            for (int i = character.getCurrentMana(); i > currMana; i--) {
                character.regenerate(); // не идеально, но просто
            }

            cursor.close();
            db.close();
            return character;
        }

        cursor.close();
        db.close();
        return null;
    }

    public String getImageUrl() {
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor cursor = db.rawQuery("SELECT " + COL_IMAGE_URL + " FROM " + TABLE_NAME + " LIMIT 1", null);
        if (cursor.moveToFirst()) {
            String url = cursor.getString(cursor.getColumnIndexOrThrow(COL_IMAGE_URL));
            cursor.close();
            db.close();
            return url;
        }
        cursor.close();
        db.close();
        return null;
    }

    public void deleteCharacter() {
        SQLiteDatabase db = this.getWritableDatabase();
        db.delete(TABLE_NAME, null, null);
        db.close();
    }
}
