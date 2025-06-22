package com.example.darkgame;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

public class CharacterFragment extends Fragment {

    private Character playerCharacter;

    @Nullable
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        View view = inflater.inflate(R.layout.fragment_character, container, false);

        // Инициализация персонажа
        playerCharacter = new Character("Артур", 100, 10, 5, 50, 2, 3);

        // Находим элементы
        ((TextView) view.findViewById(R.id.tvName)).setText("Имя: " + playerCharacter.getName());
        ((TextView) view.findViewById(R.id.tvHp)).setText("HP: " + playerCharacter.getCurrentHp() + "/" + playerCharacter.getMaxHp());
        ((TextView) view.findViewById(R.id.tvDefense)).setText("Защита: " + playerCharacter.getDefense());
        ((TextView) view.findViewById(R.id.tvSpeed)).setText("Скорость: " + playerCharacter.getSpeed());
        ((TextView) view.findViewById(R.id.tvMana)).setText("Мана: " + playerCharacter.getCurrentMana() + "/" + playerCharacter.getMaxMana());
        ((TextView) view.findViewById(R.id.tvRegen)).setText("Регенерация HP: " + playerCharacter.getHpRegen());
        ((TextView) view.findViewById(R.id.tvManaRegen)).setText("Регенерация маны: " + playerCharacter.getManaRegen());

        return view;
    }
}

