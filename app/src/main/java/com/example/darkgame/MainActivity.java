package com.example.darkgame;

import android.os.Bundle;
import android.widget.Button;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.fragment.app.Fragment;

public class MainActivity extends AppCompatActivity {

    Button btnWorld, btnCharacter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        btnWorld = findViewById(R.id.btn_world);
        btnCharacter = findViewById(R.id.btn_character);

        // Загрузка дефолтного фрагмента
        loadFragment(new WorldFragment());

        btnWorld.setOnClickListener(v -> loadFragment(new WorldFragment())); // ✅

// В MainActivity.java
        btnCharacter.setOnClickListener(v -> {
            Fragment fragment = new CharacterFragment();
            getSupportFragmentManager()
                    .beginTransaction()
                    .replace(R.id.fragment_container, fragment)
                    .addToBackStack(null)
                    .commit();
        });

    }

    private void loadFragment(Fragment fragment) {
        getSupportFragmentManager().beginTransaction()
                .replace(R.id.fragment_container, fragment)
                .commit();
    }
}
