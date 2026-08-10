package com.localdocai.backend.controller;

import com.localdocai.backend.dto.DocumentsResponse;
import com.localdocai.backend.service.AiServiceClient;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.HttpStatus;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.web.client.HttpClientErrorException;

import java.util.List;

import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(DocumentController.class)
class DocumentControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private AiServiceClient aiServiceClient;

    @Test
    void listsDocumentsFromAiService() throws Exception {
        DocumentsResponse response = new DocumentsResponse();
        response.setDocuments(List.of("sample.pdf"));
        when(aiServiceClient.listDocuments()).thenReturn(response);

        mockMvc.perform(get("/api/documents"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.documents[0]").value("sample.pdf"));
    }

    @Test
    void deletesDocumentSuccessfully() throws Exception {
        mockMvc.perform(delete("/api/documents/sample.pdf"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.filename").value("sample.pdf"))
                .andExpect(jsonPath("$.deleted").value(true));
    }

    @Test
    void returnsNotFoundWhenDeletingMissingDocument() throws Exception {
        doThrow(HttpClientErrorException.NotFound.create(
                HttpStatus.NOT_FOUND, "Not Found", null, null, null))
                .when(aiServiceClient).deleteDocument(eq("missing.pdf"));

        mockMvc.perform(delete("/api/documents/missing.pdf"))
                .andExpect(status().isNotFound());
    }
}
