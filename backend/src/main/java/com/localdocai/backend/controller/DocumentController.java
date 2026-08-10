package com.localdocai.backend.controller;

import com.localdocai.backend.service.AiServiceClient;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestClientException;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Map;

@RestController
@RequestMapping("/api/documents")
public class DocumentController {

    private final AiServiceClient aiServiceClient;

    public DocumentController(AiServiceClient aiServiceClient) {
        this.aiServiceClient = aiServiceClient;
    }

    @PostMapping
    public ResponseEntity<?> upload(@RequestParam("file") MultipartFile file) {
        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("error", "File must not be empty"));
        }
        try {
            return ResponseEntity.ok(aiServiceClient.uploadDocument(file));
        } catch (IOException | RestClientException e) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(Map.of("error", "AI service unavailable: " + e.getMessage()));
        }
    }

    @GetMapping
    public ResponseEntity<?> list() {
        try {
            return ResponseEntity.ok(aiServiceClient.listDocuments());
        } catch (RestClientException e) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(Map.of("error", "AI service unavailable: " + e.getMessage()));
        }
    }

    @DeleteMapping("/{filename}")
    public ResponseEntity<?> delete(@PathVariable String filename) {
        try {
            aiServiceClient.deleteDocument(filename);
            return ResponseEntity.ok(Map.of("filename", filename, "deleted", true));
        } catch (HttpClientErrorException.NotFound e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("error", "Document not found: " + filename));
        } catch (RestClientException e) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(Map.of("error", "AI service unavailable: " + e.getMessage()));
        }
    }
}
