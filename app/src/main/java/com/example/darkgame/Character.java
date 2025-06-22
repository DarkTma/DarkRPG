package com.example.darkgame;

public class Character {
    private String name;
    private int maxHp;
    private int currentHp;
    private int defense;
    private int speed;
    private int maxMana;
    private int currentMana;
    private int hpRegen;
    private int manaRegen;

    public Character(String name, int maxHp, int defense, int speed, int maxMana, int hpRegen, int manaRegen) {
        this.name = name;
        this.maxHp = maxHp;
        this.currentHp = maxHp;
        this.defense = defense;
        this.speed = speed;
        this.maxMana = maxMana;
        this.currentMana = maxMana;
        this.hpRegen = hpRegen;
        this.manaRegen = manaRegen;
    }

    // Геттеры и сеттеры
    public String getName() { return name; }
    public int getMaxHp() { return maxHp; }
    public int getCurrentHp() { return currentHp; }
    public int getDefense() { return defense; }
    public int getSpeed() { return speed; }
    public int getMaxMana() { return maxMana; }
    public int getCurrentMana() { return currentMana; }
    public int getHpRegen() { return hpRegen; }
    public int getManaRegen() { return manaRegen; }

    public void takeDamage(int damage) {
        int actualDamage = Math.max(0, damage - defense);
        currentHp = Math.max(0, currentHp - actualDamage);
    }

    public void regenerate() {
        currentHp = Math.min(maxHp, currentHp + hpRegen);
        currentMana = Math.min(maxMana, currentMana + manaRegen);
    }
}
