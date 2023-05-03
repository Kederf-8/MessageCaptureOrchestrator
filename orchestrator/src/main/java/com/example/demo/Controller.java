package com.example.demo;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("")
public class Controller {

  @PostMapping("/sum")
  public ResponseEntity<String> sum(
      @RequestParam int num1,
      @RequestParam int num2) {
    ProcessBuilder pb = new ProcessBuilder(
        "python3",
        "script.py",
        String.valueOf(num1),
        String.valueOf(num2));
    try {
      Process process = pb.start();
      BufferedReader reader = new BufferedReader(
          new InputStreamReader(process.getInputStream()));
      StringBuilder output = new StringBuilder();
      String line;
      while ((line = reader.readLine()) != null) {
        output.append(line).append("\n");
      }
      int exitCode = process.waitFor();
      if (exitCode == 0) {
        return ResponseEntity.ok(output.toString());
      } else {
        return ResponseEntity
            .status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body("Python script failed with exit code " + exitCode);
      }
    } catch (Exception e) {
      return ResponseEntity
          .status(HttpStatus.INTERNAL_SERVER_ERROR)
          .body("Error executing Python script: " + e.getMessage());
    }
  }

  @PostMapping("/start-shell")
  public ResponseEntity<String> startShell() {
    ProcessBuilder pb = new ProcessBuilder("python", "docker-composeCreator.py");
    try {
      Process process = pb.start();
      BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
      BufferedReader errorReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
      String line;
      StringBuilder output = new StringBuilder();
      while ((line = reader.readLine()) != null) {
        output.append(line).append("\n");
      }
      while ((line = errorReader.readLine()) != null) {
        output.append(line).append("\n");
      }
      int exitCode = process.waitFor();
      if (exitCode == 0) {
        return ResponseEntity.ok(output.toString());
      } else {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body("Python script failed with exit code " + exitCode);
      }
    } catch (Exception e) {
      return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
          .body("Error executing Python script: " + e.getMessage());
    }
  }
}
