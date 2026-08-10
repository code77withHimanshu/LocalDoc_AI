package com.localdocai.backend.service;

import com.localdocai.backend.dto.ChatRequest;
import com.localdocai.backend.dto.ChatResponse;
import com.localdocai.backend.dto.DocumentsResponse;
import com.localdocai.backend.dto.UploadResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

/**
 * Thin HTTP client that forwards requests from the Spring Boot API layer
 * to the Python AI service. Spring Boot deliberately holds no AI logic
 * itself - it only relays requests/responses.
 */
@Service
public class AiServiceClient {

    private final RestTemplate restTemplate;
    private final String aiServiceUrl;

    public AiServiceClient(RestTemplate restTemplate, @Value("${ai.service.url}") String aiServiceUrl) {
        this.restTemplate = restTemplate;
        this.aiServiceUrl = aiServiceUrl;
    }

    public UploadResponse uploadDocument(MultipartFile file) throws IOException {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        ByteArrayResource fileResource = new ByteArrayResource(file.getBytes()) {
            @Override
            public String getFilename() {
                return file.getOriginalFilename();
            }
        };

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", fileResource);

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
        return restTemplate.postForObject(aiServiceUrl + "/documents", requestEntity, UploadResponse.class);
    }

    public DocumentsResponse listDocuments() {
        return restTemplate.getForObject(aiServiceUrl + "/documents", DocumentsResponse.class);
    }

    public ChatResponse chat(ChatRequest request) {
        return restTemplate.postForObject(aiServiceUrl + "/chat", request, ChatResponse.class);
    }

    public void deleteDocument(String filename) {
        restTemplate.delete(aiServiceUrl + "/documents/{filename}", filename);
    }
}
