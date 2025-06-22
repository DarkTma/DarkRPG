package com.example.darkgame;

import android.app.AlertDialog;
import android.graphics.Color;
import android.os.Bundle;
import android.text.InputType;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.*;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import com.squareup.picasso.Picasso;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.Random;

import okhttp3.*;

public class CharacterFragment extends Fragment {

    private TextView tvName, tvHp, tvDefense, tvSpeed, tvMana, tvRegen, tvManaRegen;
    private ImageView ivCharacter;
    private Button btnCreate, btnDelete;
    private ProgressBar progressBar;
    private CharacterDBHelper dbHelper;
    private LinearLayout layout;
    private final OkHttpClient client = new OkHttpClient();
    private final String SERVER_URL = "https://darkrpg.onrender.com/generate";


    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                             @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_character, container, false);

        layout = view.findViewById(R.id.character_layout); // добавь id в LinearLayout
        tvName = view.findViewById(R.id.tvName);
        tvHp = view.findViewById(R.id.tvHp);
        tvDefense = view.findViewById(R.id.tvDefense);
        tvSpeed = view.findViewById(R.id.tvSpeed);
        tvMana = view.findViewById(R.id.tvMana);
        tvRegen = view.findViewById(R.id.tvRegen);
        tvManaRegen = view.findViewById(R.id.tvManaRegen);
        ivCharacter = view.findViewById(R.id.ivCharacter);
        btnCreate = view.findViewById(R.id.btnCreate);
        btnDelete = view.findViewById(R.id.btnDelete);
        progressBar = view.findViewById(R.id.progressBar);


//        tvName.setText("Имя: Paladin");
//        tvHp.setText("HP: 100");
//        tvDefense.setText("Защита: 20");
//        tvSpeed.setText("Скорость: 15");
//        tvMana.setText("Мана: 80");
//        tvRegen.setText("Регенерация HP: 5");
//        tvManaRegen.setText("Регенерация маны: 4");

// Отображаем элементы
        tvName.setVisibility(View.VISIBLE);
        tvHp.setVisibility(View.VISIBLE);
        tvDefense.setVisibility(View.VISIBLE);
        tvSpeed.setVisibility(View.VISIBLE);
        tvMana.setVisibility(View.VISIBLE);
        tvRegen.setVisibility(View.VISIBLE);
        tvManaRegen.setVisibility(View.VISIBLE);

        dbHelper = new CharacterDBHelper(requireContext());
        loadCharacter();

        btnCreate.setOnClickListener(v -> showCreationDialog());
        btnDelete.setOnClickListener(v -> {
            dbHelper.deleteCharacter();
            Toast.makeText(getContext(), "Персонаж удалён", Toast.LENGTH_SHORT).show();
            loadCharacter();
        });

        btnCreate = view.findViewById(R.id.btnCreate);
        btnCreate.setText("TEST"); // чтобы было видно
        btnCreate.setVisibility(View.VISIBLE);
        btnCreate.setBackgroundColor(Color.RED); // точно будет видно

        tvName.setText("Имя: TestHero");
        tvName.setVisibility(View.VISIBLE);


        Toast.makeText(getContext(), "CharacterFragment открыт", Toast.LENGTH_SHORT).show();



        return view;
    }

    private void loadCharacter() {
        Character character = dbHelper.getCharacter();
        if (character == null) {
            // Показываем кнопку "Создать"
            btnCreate.setVisibility(View.VISIBLE);
            btnDelete.setVisibility(View.GONE);
            ivCharacter.setVisibility(View.GONE);

            // Скрываем текстовые поля
            tvName.setVisibility(View.GONE);
            tvHp.setVisibility(View.GONE);
            tvDefense.setVisibility(View.GONE);
            tvSpeed.setVisibility(View.GONE);
            tvMana.setVisibility(View.GONE);
            tvRegen.setVisibility(View.GONE);
            tvManaRegen.setVisibility(View.GONE);
        } else {
            // Показываем всё
            btnCreate.setVisibility(View.GONE);
            btnDelete.setVisibility(View.VISIBLE);

            tvName.setVisibility(View.VISIBLE);
            tvHp.setVisibility(View.VISIBLE);
            tvDefense.setVisibility(View.VISIBLE);
            tvSpeed.setVisibility(View.VISIBLE);
            tvMana.setVisibility(View.VISIBLE);
            tvRegen.setVisibility(View.VISIBLE);
            tvManaRegen.setVisibility(View.VISIBLE);

            tvName.setText("Имя: " + character.getName());
            tvHp.setText("HP: " + character.getCurrentHp() + "/" + character.getMaxHp());
            tvDefense.setText("Защита: " + character.getDefense());
            tvSpeed.setText("Скорость: " + character.getSpeed());
            tvMana.setText("Мана: " + character.getCurrentMana() + "/" + character.getMaxMana());
            tvRegen.setText("Регенерация HP: " + character.getHpRegen());
            tvManaRegen.setText("Регенерация маны: " + character.getManaRegen());

            String url = dbHelper.getImageUrl();
            if (url != null && !url.isEmpty()) {
                ivCharacter.setVisibility(View.VISIBLE);
                Picasso.get().load(url).into(ivCharacter);
            } else {
                ivCharacter.setVisibility(View.GONE);
            }
        }
    }


    private void showCreationDialog() {
        String[] options = {"Описание вручную", "Выбрать пол и создать воина"};
        AlertDialog.Builder builder = new AlertDialog.Builder(getContext());
        builder.setTitle("Как создать персонажа?")
                .setItems(options, (dialog, which) -> {
                    if (which == 0) {
                        askForDescription();
                    } else {
                        askForGender();
                    }
                })
                .show();
    }

    private void askForDescription() {
        EditText input = new EditText(getContext());
        input.setHint("Введите описание персонажа");
        input.setInputType(InputType.TYPE_CLASS_TEXT);

        new AlertDialog.Builder(getContext())
                .setTitle("Описание персонажа")
                .setView(input)
                .setPositiveButton("Создать", (dialog, which) -> {
                    String prompt = input.getText().toString();
                    if (!prompt.isEmpty()) {
                        generateCharacter(prompt, "Пользователь");
                    }
                })
                .setNegativeButton("Отмена", null)
                .show();
    }

    private void askForGender() {
        String[] genders = {"Мужчина", "Женщина"};
        new AlertDialog.Builder(getContext())
                .setTitle("Выбери пол")
                .setItems(genders, (dialog, which) -> {
                    String prompt = (which == 0)
                            ? "A strong male fantasy warrior in armor, heroic and detailed"
                            : "A brave female fantasy warrior in golden armor, glowing, detailed";
                    String name = (which == 0) ? "Воин" : "Воительница";
                    generateCharacter(prompt, name);
                })
                .show();
    }

    private void generateCharacter(String prompt, String name) {
        requireActivity().runOnUiThread(() -> progressBar.setVisibility(View.VISIBLE));

        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put("prompt", prompt);
        } catch (JSONException e) {
            e.printStackTrace();
        }

        RequestBody body = RequestBody.create(
                MediaType.parse("application/json"),
                jsonObject.toString()
        );

        Request request = new Request.Builder()
                .url(SERVER_URL)
                .post(body)
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                requireActivity().runOnUiThread(() -> {
                    progressBar.setVisibility(View.GONE); // скрыть
                    Toast.makeText(getContext(), "Ошибка соединения", Toast.LENGTH_SHORT).show();
                });
            }

            @Override
            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                String json = response.body().string();
                Log.d("CharacterFragment", "Response JSON: " + json);

                try {
                    JSONObject obj = new JSONObject(json);
                    String imageUrl = obj.getString("url");

                    Random r = new Random();
                    Character character = new Character(
                            name,
                            r.nextInt(50) + 50,
                            r.nextInt(20) + 10,
                            r.nextInt(20) + 10,
                            r.nextInt(40) + 40,
                            r.nextInt(5) + 3,
                            r.nextInt(5) + 3
                    );

                    dbHelper.saveCharacter(character, imageUrl);

                    requireActivity().runOnUiThread(() -> {
                        progressBar.setVisibility(View.GONE); // скрыть
                        Toast.makeText(getContext(), "Создан!", Toast.LENGTH_SHORT).show();
                        loadCharacter();
                    });
                } catch (Exception e) {
                    requireActivity().runOnUiThread(() -> {
                        progressBar.setVisibility(View.GONE); // скрыть
                        Toast.makeText(getContext(), "Ошибка парсинга", Toast.LENGTH_SHORT).show();
                    });
                }
            }
        });
    }

}
